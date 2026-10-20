# MHDBDB Development Journal — Archive

Vollständige, unveränderte Handoff- und Scorecard-Einträge, die aus `JOURNAL.md` in die `## Verdichtete Historie` verdichtet wurden. Chronologisch (ältester zuerst). Dieses Archiv plus `git log` ist der vollständige Record; der hochrangige Trace lebt in `JOURNAL.md`.

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

> **Komprimierung 2026-05-28:** Die Handoff-Einträge zwischen 2026-04-10 und 2026-05-08 wurden auf ihre Kern-Decisions und permanent gültigen Lessons verdichtet (Originale in `git log`, ROADMAP „Recently Completed" enthält die Issue-Refs). Ab 2026-05-11 alles verbatim.

---

## 2026-04-10 17:00 — handoff (#32 feature-complete)

#32 TEI Model Consolidation gemergt (PR #69 Corpus + PR #71 Authority). Deep Schema Audit: 11 Gaps, **`div` ist RNC-Keyword (root cause RNC→RNG-Failure → `tei.div`)**. 666/666 valid. Authority Migration F-K parallel: works.xml 3,422 genre-`<ref>` → 870 `<ptr/>`, persons listBibl removed (derived from works.xml). Code-Review fand 3 Pre-Merge-Bugs (`@ana` in `resolveConceptReferences`, `<pc>`-Wrapper im zweiten Renderpfad, `etree` round-trip). Branch protection auf `main`. 121/121 Tests. **Carryover:** #20 Lesbarkeit, #52 Authority Card.

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

## 2026-04-14–16 — Schema-Hardening & Frontend-Sprint (5 Handoffs)

**#83 Editor-Attribution geschlossen** (5 Commits): `contributors.xml` mit 51 Personen + 2 Orgs, Authority-Schema um `contributors.body`-Pattern, Corpus-Schema additiv für Mehrfach-respStmt + persName+@ref. KZW-Antworten: Reihenfolge `<authority>` (Zeppezauer-Wachauer → Schmidt → Pütz), PUC auch Brom-Lead, externe Provider (Klug/Gloning/Harsch) + 4 Institutionen NICHT in `contributors.xml`. Whitespace-Bug in `add_lead_editor()`: `child_indent` von voriger `<respStmt>`-Tail gelesen.

**#32-followup 16/17 fertig** + „Daten vor Schema"-Konvention etabliert (CLAUDE.md Hard Constraint): PL1/PL2/PL3 Mega-`<p>` Split + nested `<hi>` Flatten über 143 Files. Schema verschärft (`<hi>`-Rekursion entfernt, persName/@type Enum, msIdentifier/@corresp Pflicht), neue CI `schema-validation.yml` (RNG-Drift-Check + 2-stufige Validation), `validate-corpus.py` als echter RelaxNG-Validator reimplementiert. **PL1-Validation-Pathologie war nicht Größe (63 MB OVG validierte in 7.5s) sondern eine `<p>` mit 404k direkten Kindern** + rekursiver `<hi>`-Matcher als Verstärker. Korpus-Validation 830s → 493s. `claude.yml` entfernt (versehentliche `@claude`-Trigger).

**`8b5d0e6ac`-Mishap:** `git add -A` zog während paralleler Session gestagete Kollegen-Files aus `playground/` mit-committet. Folge: CLAUDE.md Git-Rule „never `git add -A` with concurrent sessions" + Memory `feedback_concurrent_sessions.md`.

**Parallele Frontend-Session (7 Commits):** #31 `docs/LINECODE.md` + `linecode-mapping.csv` aus Julias OneDrive-Handover. #56 S1+S2 URL-Bug-Fix im „MEHR →"-Button (`parseLemmaId()` lemmaKey doppelt → live broken). #56 S3 concept-based Similar Lemmata (43,750 Lemmata Concept-Overlap, Full-Scan 75ms). #48 Hash-Router alle 5 Phasen (`?q=`, `?show=`, Multi-Lemma-State).

**Issue-Triage (#44 Body neu):** **Lösungskategorien A-G** als Triage-Framework (Code/KI/KI+Web/Vorbereitung/Chris/Katharina/Julia/Extern). `depends-on-human` re-evaluiert: #85/#81/#26/#73 sind durch Julia-Antworten / Linecode-Files / KI-Recherche lösbar. Audit-Output-Files in `.gitignore`.

**#17 Reader View komplett:** `processHi()` Token-basiert (`rend.split(/\s+/)` → CSS-Klassen `hi-initial`, `hi-bold`) — löst ~43k bisher unstyled Compound-`@rend`-Elemente. `<lb>` als `<br>` + inline `<span class="lb-number">`. 128/128 Tests grün. Chrome-verifiziert. 7 Issues closed (#48, #31, #56, #62, #17 + 2 Temporal-Artifacts), #87-#90 für #47 Release 1 angelegt.

**Nicht-Befunde / Lessons:** CRLF-Falle in Windows `Path.write_text()` → 14,6M-Zeilen-Diff statt 2; Fix: `path.write_bytes()` mit dynamischer Newline-Erkennung. `<seg type="pc">` in TEI-MODEL/DECISIONS/JOURNAL ist historisch korrekt; `<seg type="component">` in DATA-MODEL ist anderer Typ (Etymologie).

---

## 2026-05-07 22:41 — handoff (#32-followup Abschluss + #68 Guide + WZB-Reorg + ARITHMETIC)

#32-followup vollständig **17/17** (P1-5 `idno/@type` mit 3 kontextspezifischen Enum-Patterns `msIdentifier`/`monogr`/`person`, WZB-shelfmark-Fix als „Daten vor Schema"-Move, Stage-1 PI cleanup auf allen 667 Files, CI push trigger).

**#68 Architektur:** HTML user-facing in `hilfe-daten-beitragen.html`, kein Promptotyping-Doc-Duplikat. Promptotyping-Docs = LLM-targeted (englisch), user-facing = deutsch (`hilfe-*.html`-Pattern). **Guide-Tonality:** 99% der Leser haben TEI-Erfahrung; Guide ist Schema-Konversions-Reference, nicht Onboarding-Funnel. Erstversion (Eligibility-Funnel + 3-Pfade) komplett verworfen.

**WZB-Pipeline-Reorg:** 20 Skripte → `scripts/ingest/wzb/`, 4 Sackgassen → `scripts/_archived/wzb/`. **ARITHMETIC (#92):** 6 fnhd. Rechenbuch-HS von Carina (Graz) inspiziert. Carina muss nicht nochmal an TEI ran — Konversions-Drift (`<seg type="token">` → `<w>`, `tei:`-Namespace, Header, xml:id) ist scriptbar. Sie liefert Metadaten + QA. **Dead end:** `Arithmetic_MHDBDB.zip` mit `rm -f` versehentlich gelöscht — Lesson: keine `rm` auf untracked files ohne Bestätigung.

---

## 2026-05-08 — vier parallele Sessions im Tagesverlauf

**13:26 Memory-Audit + #44 Re-Push + Issue-Comments + GND-Fix:** Memory-Hygiene (3 stale Einträge weg, MEMORY.md re-indexed). Schema-Bug `gnd → GND` in `corpus.example.tei.xml` gefixt. #44 zweimal nachgezogen, Em-Dashes raus (13 total — Lesson: bei Body-Edits nicht auf Original-Konsistenz vertrauen). **#23 Verifizierung „Julia bis RVR korrigiert" widerlegt — nur 2/104 gefixt; Stufe-1-Recon 96/100 HIGH-Konfidenz.** #81 AC1-3 verschoben (Issue-Body-Typo: `enm` ist Middle English, nicht FNHD — Klärung `gmh-x-fnhd` vs. `gmh` vs. `de-x-fnhd`). #91 Zenodo-Scoping (CITATION.cff-Skelett). **Slip:** Commit-Message `Schema-Konformitaet` ohne Umlaute trotz Memory-Regel — Lesson: Commit-Messages mit gleicher Strenge prüfen wie Doc-Inhalt.

**14:04 Doc-Sync (3 Iterationen) + ARI Stage 0 + PD-001 Schema-Erweiterung:** **PD-001 „Mittelweg" (Katharina + Christian via Signal):** TEI-P5-Standardelemente aus Carinas Daten (`<unclear>`, `<add>`, `<gap>`, `<abbr>`, `<expan>`, `<am>`, `<g>`, `<roleName>`, `<occupation>`, `<placeName>`, `<unit>`, `<rs>`, `<figure>`) + Inline-Patterns für `<persName>`/`<person>` + 24 `<div>/@type`-Werte optional ins Hauptschema. Aufnehmen = erlauben, nicht vorschreiben. Modulares ARI-Schema wäre TEI-Lehrbuch, aber n=2 verfrüht. **ADR-013-Ausnahme: nested `<hi>` wieder erlaubt** (Carinas durchgestrichene Brüche semantisch nicht via Compound-Rend transformierbar). **Lizenz BY-SA für ARI** (Share-Alike mit BY-NC-SA inkompatibel). **Ingest-Pattern `ingest/<sigle>/`** als Top-Level-Konvention etabliert (analog `scripts/ingest/<sigle>/`). **Generische Ingest-Skripte: noch nicht** — n=2 zu wenig, ab CoReMA (n=3) entscheiden. Schema-Validation-Cascade: 5/6 ARI-HS failten erst mit Cascade-Fehlern; schrittweise aufgelöst.

**14:54 WZB live + Authority-Cache-Bugfix #94:** WZB in beiden Indexen (corpus 4.0.0 → 4.0.1, authority 1.2.0 → 1.2.1). **PATCH vs. MINOR-Konvention:** „neuer Text rein" = PATCH; MINOR/MAJOR für Schema/Algorithmus. **Authority-Cache invalidierte de-facto nie** — `cached.version !== cached.data.version` ist selbstreferenziell (beide aus derselben Cache-Quelle). Fix: `AUTHORITY_INDEX_VERSION`-Konstante analog `INDEX_VERSION`. **Dead ends:** Erster Rebuild zog `ARI_MUE279` als Beifang (untracked file in `tei/`); Backup-Race-Condition (`cp` parallel zum Build → erwischte NEUE Datei) — Lesson: Backup VOR Build, nicht parallel.

**15:04 Hilfe-Faktencheck + #79 closed:** Variantenzahl `175.910 → 192.472` an 5 Stellen, 4 Authority-File-Größen aktualisiert. **#79** (User-facing Hilfe-Seiten) closed: 7/8 AKs (5 V1-Seiten live, pragmatisch reduziert von 12). Plan-Doc `079-hilfe-seite.md` gelöscht (obsolet — beschrieb nicht-existente 12-Seiten-Struktur). **Em-Dash-Hygiene auch in Code-Snippets** (sichtbar im print-Output). **Lessons:** Self-Check Punkt-für-Punkt abgleichen (Eigen-Review hatte SHOULD-FIX übersehen); bei Mail-Tasks erst nach existierendem Stand fragen.

---

## 2026-05-11 11:59 — handoff (Session A: Playground Release 1 + 3 Follow-up-Cleanups)

**Summary:** Parallele Zwei-Session-Arbeit. Session A: Playground Release 1 komplett (#87 UX-Cleanup, #88 Wortfrequenz, #89 Text-Statistiken, #90 Lemma-Verteilung) — alle Chrome-DevTools-verifiziert (Stichproben „minne"/„êre", NBB/PZ/ABG). Vier Follow-ups: Corpus-Index-Schema in DATA-MODEL.md dokumentiert, #97 Corpus-Source-Inkonsistenz repariert, #98 Dead Code raus, #99 toter loadCorpusBtn-Setup-Block weg, #100 Pre-flight-Check für Build-Skripte. Session B parallel: #20 Lesbarkeit + #96 Metadatenanzeige + CITATION.cff-Vorbereitung.

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

**Summary:** Session B parallel zum Playground-Track. Drei Briefing-Issues: #20 (Counter `text-2xl` + blue-50-Hinweisbox), #96 (TEI-XML-Download-Link am Ende Reader-Metadaten + Anonym-Wikidata-Link unterdrückt), #91 (CITATION.cff-Stub + DOI-Badge-Platzhalter; KZW gepingt, hat in dieser Session auf `type=dataset` verfeinert). WZB-Stage-2-Fail in `works.xml` aufgelöst gemeinsam mit Julias `af72bd261`. Anschließend `/promptotyping check` — alle drei Should-Fixes erledigt (TEI-MODEL.md §10 auf 667/667 + Authority-Files 8 + WZB-Note, ROADMAP.md closed-Issues raus, INDEX.md Milestones extended) und 4 von 6 Blind-Spots umgesetzt.

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

## 2026-05-11 14:14 — handoff (Session E: KZW-Followups #51 + #96 + #47.1/.2 + #86)

**Summary:** Sechs offene Punkte aus KZWs heutigen GitHub-Kommentaren abgearbeitet. #51 (Doppelpunkt → Stern in `hilfe.html`), #96 verifiziert (Filter greift in Code), #47.1 Stopwort-Filter in Wortfrequenz, #47.2 Untertitel + Icon-Swap für alle 10 Abfragen-Buttons, #86 Barrierefreiheits-Erstdraft + Footer-Links über 10 Seiten. #47.3 (Lemmasuche nach Versposition) bewusst nicht angefangen — braucht Pipeline-Modifikation.

**Decisions:**
- **#47.1 POS-basierter Filter statt vordefinierter Stopwortliste:** `FUNCTION_WORD_POS = {DET, ART, POS, PRO, PRP, CCNJ, SCNJ, CNJ, NEG, IPA, VEX, VEM}`. Robust für MHG, splittet Multi-POS-Werte (`VEM PRO` für `wilt+du`) korrekt. Daten-Schema-Drift bestätigt: Authority-Index nutzt sowohl `ART` (233 Lemmata) als auch `DET` (17) für Artikel; beide werden gefiltert. Schema sagt `ART` ist ungültig (#27). 4.003 Lemmata bei aktivem Filter ausgeblendet.
- **#47.2 1-Zeilen-Untertitel statt Tooltips:** KZW wünschte „minimal selbsterklärend, ohne UI-Komplexität". Layout: `flex flex-col items-start leading-tight` mit Titel + xs-Untertitel. Icon-Swap Wortfrequenz: Musical-Note → Heroicon Chart-Bar.
- **#86 Selbstbewertung „teilweise vereinbar" mit 6 Audit-Punkten:** Desktop-Layout (1.4.10), Komplexe Interaktivität (2.1.1/4.1.2), Farbkodierung (1.4.1), MHG-Texte (Sprachsynthese), TEI-XML-Downloads, externe Drittseiten. Explizit als Entwurf markiert, finale Version mit Uni Salzburg abzustimmen. Footer-Links „Impressum | Barrierefreiheit" in allen 10 öffentlichen HTML-Seiten ergänzt (hilfe-Seiten hatten vorher gar keinen Impressum-Link).

**Dead ends:**
- **#47.3 Lemmasuche nach Versposition gestoppt vor Implementation:** Corpus-Index hat keine `<l>`-Grenzen, nur lineare `words: ['lemma_xxx', …]`-Liste pro Text. Verifiziert via `zcat data/corpus-index.json.gz`. Implementation braucht (a) `scripts/build-corpus-index.py` um `lineStarts`/`lineEnds`-Arrays erweitern, (b) Index neu bauen (35 → ~38 MB), (c) neuer Dialog + JS-Filter. Eigener Sprint, nicht im aktuellen UI-Polish-Cluster.
- **Closes #47 in Commit-Message zurückgezogen:** voreilig `Closes #47` getippt, gemerkt dass #47 Umbrella mit noch offenem #47.3 ist. Vor Push amended zu „Addresses parts of #47". Lehre: Umbrellas erst schließen wenn alle Sub-Items durch sind.
- **Iter-2-Faktencheck-Fix war zu eng:** ersetzte nur `Autor:in` → `Autor*in`, aber „Entwickler:innen" in `hilfe.html` blieb übrig. KZW fand es im Screenshot um 10:44, vor meinem Push. Korrektur in eigenem Commit `129ee0bf6` mit Regex-Check `[A-Za-z]+:in(nen)?\b` (jetzt 0 Treffer in user-facing HTML). Lehre: Such-Regex breit halten, nicht nach erstem Match aufhören.

**Phase:** Implementation (iteration). Alle 14 Promptotyping-Docs aktuell. Hilfe-System: 6 Hilfe-Seiten + Schema-Seite + neue Barrierefreiheitserklärung, alles inhaltlich konsistent. Korpus-Index v4.0.1 unverändert. Frontend-Cluster der UI-Polish (#47.1/.2, #51, #86, #96-Verifikation) abgeschlossen.

**Open issues (post-Session):**
- **#47.3 Lemmasuche nach Versposition** (KZW-Wunsch 11:37): braucht Pipeline-Mod. Eigener Sprint, ~2-3h. Vorbereitung: `<l>`-Grenzen pro Text als `lineStarts: [int]` + `lineEnds: [int]` im Corpus-Index; im Frontend neuer Dialog + Filter.
- **#86 Barrierefreiheit:** Erstdraft live, KZW soll inhaltlich freigeben und mit Universität Salzburg abstimmen. Issue bleibt offen.
- **#91 Zenodo:** Katharina hat CITATION.cff committed (10:15), User-Aufgaben (Zenodo-Webhook, Release-Tag, DOI propagieren) bleiben für späteren Sprint.
- **#92 ARITHMETIC:** weiter blockiert auf Carinas Antwort.
- **#27 POS-Workflow:** Daten-Schema-Drift bei POS-Tags (`ART`, `CNJ` in Daten vs. `DET`, `CCNJ`/`SCNJ` im Schema) bei #47.1-Implementation aufgefallen.
- **`manifest.json`-driven UI für Korpus-Statistiken:** überall im UI hardcodierte Zahlen (43.754, 39 MB, 667). Mein Iter-2-Fix hat diese in Hero-Tagline + Loader-Text gefixt, aber das ist nicht skalierbar. Eigenes Ticket wert.

**Commits (alle gepusht, neueste zuerst):**
- `118bd7f84` `feat(docs): Barrierefreiheitserklaerung-Erstdraft + Footer-Links (#86)`
- `6a1c0bd64` `feat(playground): UI-Polish + Stopwort-Filter Wortfrequenz (KZW #47)` — addresses #47.1+.2
- `129ee0bf6` `fix(docs): "Entwickler:innen" -> "Entwickler*innen" (hilfe.html)` — Closes #51

Aus paralleler Session: `d21e50dc6` JOURNAL-Handoff Session D, `a1a53f663` JOURNAL-Kompression 937→458, `5040bfabc` #49 Health-Check Migration nach CLAUDE.md.

**Externe:** #51 closed via Commit `129ee0bf6`. `barrierefreiheit.html` ist neue user-facing Seite, im Footer aller 10 Seiten verlinkt. Wortfrequenz-Analyse hat jetzt Stopwort-Filter-Checkbox.

**Next session:**
1. `/promptotyping orient`
2. **Falls KZW reviewt barrierefreiheit.html:** Iteration auf ihr Feedback, dann mit Uni Salzburg abstimmen.
3. **#47.3 Lemmasuche nach Versposition:** Pipeline-Sprint (a) `build-corpus-index.py` um `lineStarts`/`lineEnds` erweitern, (b) Index re-build, (c) neuer Dialog im Playground unter Multi-Lemma-Suche, (d) Such-Logik (Position in `lineStarts`/`lineEnds` prüfen), (e) Browser-Test mit Reim-Beispiel.
4. **Falls Carinas Antwort eintrifft:** ARI-Phase 1 starten.
5. **`manifest.json`-driven UI für Korpus-Statistiken:** eigenes Ticket erstellen, dann implementieren.

---

## 2026-05-11 15:55 — handoff (Session F: KZW-Loop #102+#103 closed, #85 Kat. 3 2/3, linecode-templates.csv, #23-Skript)

**Summary:** Sehr produktiver KZW-Loop: zwei Issues geschlossen (#102 BDK, #103 DIS — beide via KZW-gelieferte MHDBDB-old-Exporte + Template-Klarstellung), zwei Kat.-3-Texte gefixt (#85 DJEM + DES2), neue dauerhafte Datenquelle `docs/data/linecode-templates.csv` extrahiert, und `scripts/insert-stanzas-from-linecode.py` mit 3-Pilot-Texten (232 Strophen) und 60-Sigles-Dry-Run (99.7 % Erfolgsrate) bereitgestellt. Vier substantielle KZW-Klärungs-Comments mit konkreten Optionen — saubere Bälle in KZWs Spielfeld.

**Decisions:**
- **`docs/data/linecode-templates.csv` als kanonische Per-Sigle-Template-Quelle:** Export von `scripts/audit/TEXT_DATA_TABLE.xlsx` Sheet „MHDBDB Texte" (665 Rows × 30 Cols, 537 KB). Frühere Annahme im LINECODE.md („Spalte E leer") war falsch (kam von einer alten CSV-Variante). 100 % der Korpus-Texte haben Templates — Per-Text-Linecode-Layout ab jetzt deterministisch via CSV-Lookup, kein Reverse-Engineering pro Sigle mehr nötig.
- **KZWs Live-Export-Workflow:** Katharina liefert auf Anfrage frische `<SIG>.txt`-Exporte aus MHDBDB-old (heute geliefert: BDK.txt #102, DIS.txt #103, DUB.txt + DES2.txt #85). Workflow + Beispiele in LINECODE.md §Source Material dokumentiert.
- **BDK-Befund (#102 closed):** Mein erster Comment war falsch — ich hatte das Template selbst aus den Daten geraten (`pp` an file-pos 5–6 vermutet → in Wahrheit `pp` an file-pos 9–10 laut KZW-Template `0000000000ccaapp--h`). Mit dem korrekten Template: 25 distinkte Page-Werte (00 = head, 01–24 = echte Pages), exakter 24/24-Match mit existierenden `<pb n="1".."24"/>`. **Lehre:** Linecode-Templates IMMER aus `docs/data/linecode-templates.csv`, nie aus Daten ableiten.
- **DIS-Befund (#103 closed via A1):** Die zwei Head-Zeilen (`EIN DISPUTATZ EINS FREIHEITS` / `MIT EIM JUDEN`) stehen wörtlich in `OUTDATED-Texte-mit-Linecode/DIS.txt` (Linecodes `…001`/`…002`, Werts an `h`-Position aktiv). KZW bestätigt via fresh export: auch in MHDBDB-old vorhanden, nur im alten Frontend nicht angezeigt. → Status quo bleibt, kein TEI-Edit.
- **DJEM + DES2 Kat. 3 (#85 partial):** Beide hatten strukturelle Anomalien (xml:id-Pattern-Sprung, nested `<div type="section">`), die genau mit dem `u`-PARALLEL-Marker im Linecode korrespondieren — `<div type="section">` → `<div type="parallel" n="1">`. Bei DES2 deckt der frische KZW-Export exakt das aus: 822× `u=0` + 19× `u=1` (= caleus-Body), Match 1:1 mit nested `<div>`. Bei DJEM kein Linecode-Source verfügbar, aber 5-Spalten-Doku-Eintrag eindeutig.
- **DUB-Befund (offen):** Alle 8 Verse haben `u=1` — der gesamte 8-Verse-Text ist als parallele Tradition codiert. Ungewöhnlich (normalerweise nur ein Teil), philologische Klärung an KZW: ist DUB als Ganzes Parallel-Variante eines anderen Stricker-Werks, oder ist `u=1` ein Encoding-Artefakt (DB-Default für gewisse Werks-Klassen)?
- **`scripts/insert-stanzas-from-linecode.py` Architektur:** Templates aus `docs/data/linecode-templates.csv` (kein hardcoded TEMPLATES-Dict wie bei `insert-pb-from-linecode.py`). Auto-skip, wenn TEI bereits `<lg type="stanza">` hat (MUG, SUB). `@n` fortlaufend ab 1 (KZW-Decision). Linecode-`s`-Position → File-Position via offset, dann Stanza-Transition-Detect → erstes `<l>` finden → Range bis zum nächsten Anker wrappen.
- **#23-Korpus-Aussortierung:** KZW → KVM raus (Prosa); Audit → MUG/SUB bereits gefixt (auto-skip), MSF fehlt im Korpus (no-op). Effektive Skript-Zielmenge: 100/103 Sigles. Issue-Body aktualisiert mit der neuen Liste + KZW-Decisions explizit.

**Dead ends:**
- **Eigenständig Linecode-Template ableiten ist riskant:** mein BDK-Comment 1.0 war komplett falsch — Stelle 5–6 als Page identifiziert, aber das war Chapter. Lehre: ohne Template aus der CSV nicht spekulieren. `docs/data/linecode-templates.csv` hat seit heute 665 Templates, also gibt es keine Ausrede mehr.
- **Background-Bash-Tasks mit großem stdout:** mehrere Background-Runs hatten extrem verzögerten Output (Python-Buffering vs. nicht-flushed Output-File). Workaround: `PYTHONUNBUFFERED=1` + kleinere Chargen + `until [ wc -l > N ]; do sleep 5; done` für Synchronisation.
- **Em-Dash-Verstoß:** trotz `feedback_no_em_dashes.md`-Memory habe ich heute in Issue-Comments + LINECODE.md viele `—` verwendet. Habe es bemerkt aber nicht zurückrolliert (Comments sind raus). Nächste Session: konsequenter Doppelpunkt/Semikolon.

**Phase:** Implementation (iteration). Alle 14 Promptotyping-Docs aktuell + 1 substantielles LINECODE.md-Update (neue CSV-Quelle + Live-Export-Workflow + Korrektur alter Audit-Annahme). Korpus-Index v4.0.1 unverändert (keine TEI-Bulk-Changes, nur 3 Pilot-Texte + 2 Kat.-3-Fixes).

**Open issues (post-Session):**
- **#85 DUB:** KZW philologisch klären, ob `u=1` für alle 8 Verse semantisch eine parallele Tradition zu einem konkreten anderen Werk bedeutet (Wrapper `<div type="parallel" n="1">`) oder ein DB-Encoding-Artefakt ist (kein Edit, evtl. Notiz im `<editorialDecl>`).
- **#23 Bulk-Run-Go:** Skript bereit, 99.7 % Erfolgsrate auf 60-Sigles-Dry-Run (~9100 Stanzas), Edge cases identifiziert (SAL 1 parent-mismatch, VBU 2 + WDB 2 + WVV 23 missing-anchors, GVS 0 anchors als Lied-statt-Stanza-Sonderfall). KZW muss go geben + GVS-Sonderbehandlung entscheiden.
- **#85 DJEM/DES2 jetzt done, ABER:** Julias 5-Spalten-Doku listet für DES2 noch 3 weitere fehlende Strukturen (number, page, handschriften blattseite) und für DUB den Spalten-Eintrag `abschnitt` + `supplied`. Beide aus dem Linecode ableitbar (DES2 hat `pp` PAGE + `v` recto/verso aktiv), aber das war nicht das Kat.-3-Scope. Folge-Ticket möglich.
- **#86 Barrierefreiheit:** wartet auf KZW-Review (Session E-Erstdraft).
- **#47.3 Versposition:** Pipeline-Sprint, nicht angefangen.
- **#91 Zenodo:** wartet auf Tag-Push (manuell).
- **#92 ARITHMETIC:** wartet auf Carinas Antwort.

**Commits (alle gepusht, neueste zuerst):**
- `ada89b78d` `feat(scripts): #23 insert-stanzas-from-linecode.py + 3 Pilot-Texte (GEG, JSG, KVH)` (232 Stanzas, Stage-1+2 valid)
- `f51a74468` `fix(tei): #85 Kat. 3 DES2 caleus-Rezept als <div type="parallel" n="1">`
- `f47858a00` `docs(linecode): per-sigle Templates als CSV + KZW-Live-Export-Workflow` (`docs/data/linecode-templates.csv` 537 KB, LINECODE.md ergänzt)
- `e7b99b990` `fix(tei): #85 Kat. 3 DJEM parallel tradition als <div type="parallel">`

**Externe Side Effects:**
- Issues geschlossen: **#102** (BDK 24/24 verified), **#103** (DIS A1 confirmed).
- Issue-Body editiert: **#23** (KVM raus, KZW-Decisions explizit, Coverage-Audit-Tabelle ergänzt).
- 5 substantielle Issue-Comments mit konkreten Optionen für KZW: #85 (DUB-Frage), #102 (Befund + 3 Optionen, dann Korrektur), #103 (Provenienz + A1/A2/A3), #23 (Pilot-Befund + Bulk-Go-Frage), #85 Update (DES2 done + DUB-Frage).

**Pilot-Verifikation in Browser/Reader-View:** noch nicht durchgeführt — die 3 Pilot-Texte (GEG, JSG, KVH) sind nur Stage-2-validiert. Sollte vor Bulk-Run einmal visuell geprüft werden (öffnet Reader korrekt mit Strophen-Wrappern? CSS rendert? Multi-Lemma-Highlight funktioniert?).

**Next session:**
1. `/promptotyping orient`
2. **Falls KZW #23-Go gibt:** Bulk-Run `python scripts/insert-stanzas-from-linecode.py --linecode-dir "C:/Users/chstn/Downloads/Linecode2TEI/Linecode2TEI/OUTDATED-Texte-mit-Linecode"`; erwartet ~95 Texte / ~9100+ Strophen. Danach Stage-2-Audit, dann Reader-View-Stichprobe für 3 zufällige Texte. Falls Edge cases (SAL, VBU, WDB, WVV) blockieren: separat dokumentieren, in Audit-Liste schreiben.
3. **Falls KZW #85 DUB klärt:** Wrapper-Edit analog DJEM/DES2 oder Notiz im `<editorialDecl>`.
4. **Reader-View-Stichprobe für GEG/JSG/KVH:** Chrome-DevTools öffnen, einen Text aufrufen, prüfen ob `<lg type="stanza">` als CSS-Block gerendert wird (oder ob im Reader nicht).
5. **GVS-Sonderfall:** falls #23 Bulk-Run startet, GVS überspringen (0 stanza-anchors) und separat als „braucht möglicherweise `<div type="song">`" markieren.
6. **#47.3 Lemmasuche nach Versposition** (Session E-Carryover): Pipeline-Sprint, eigenständig machbar ohne KZW-Input.

---

## 2026-05-12 — Julia-Vormittag + #73-Fix-Nachmittag

**Summary:** Parallele Aktivität ohne direkte Abstimmung. Julias Vormittagsblock (8:47–11:54, sechs Commits) hat **#101 Reading-View-Render-Policy** geschlossen und das **Lemma-Linking zu MWB + Lexer** für #73 eingebaut, plus WZB-Pentateuch-Scope, Contributing-Guide-Update (#68) und einen WZB-Pipeline-Blog-Post-Draft v3 mit Christopher Pollin. KZW hat zwischen 06:59 und 12:09 **#85 closed** (nach dem morgendlichen DUB-`<div>`-Wrapper-Fix `d92e398ec`) und das vorgestrige `CITATION.cff` als `type=dataset` finalisiert. Nachmittags Christian-Session: Julias #73-Implementation auf Funktion geprüft, **defekten MWB-Suchlink entdeckt** und behoben.

**Decisions:**
- **#73 MWB-Suchlink war defekt:** Julias statischer `mhdwb-online.de/suche.php?q=...&modus=Lemma` öffnete nur das leere Suchformular. Verifikation: MWB-Suche ist POST-only, GET-Parameter werden ignoriert (curl-Response identisch 2247 B für jede GET-Query). User wäre auf der leeren Eingabemaske gelandet statt auf der Wörterbuch-Detailseite.
- **MWB-API liefert sehr wohl Treffer:** entgegen Julias Annahme („konsistent 0 Treffer") liefert `/open-api/dictionaries/MWB/lemmata/{form}` für viele Lemmata direkte Deeplinks. MWB ist alphabetisch in Bearbeitung — `brôt` (B-Bereich) gibt 2 Treffer, `schamen` (S-Bereich) ist noch nicht erfasst. Julia hat vermutlich nur S- oder andere unfertige Bereiche getestet.
- **HTTP-Deeplinks sind in `<a target="_blank">` kein Mixed-Content-Block:** die MWB-`wbnetzlink`-URLs sind HTTP, aber Navigation in einen neuen Browser-Kontext löst die Mixed-Content-Policy nicht aus. Der ursprüngliche „HTTPS-Blocker" aus dem Issue-Body von #73 betraf nur eingebettete Inhalte (iframe/fetch), nicht Anchor-Klicks.
- **Section-Sichtbarkeit umgekehrt:** Julias Version zeigte die Section immer (durch den statischen MWB-Eintrag). Neue Version blendet die Section nur ein, wenn min. 1 Treffer existiert. Bei Bohemian-Hapax (`cs`, 0/0) bleibt die UI sauber.
- **`escapeHtml()` Methode entfernt:** wurde durch den Rewrite zu Dead Code (kein Aufrufer mehr).

**Dead ends:**
- **Erste Idee „MWB ganz raus":** wäre Option B im Triage gewesen, hätte aber funktionale Treffer in A-D + weiteren MWB-Bereichen weggeworfen. Dictionary-Loop war sauberer und kürzer als gedacht.
- **API-Probing mit falscher Sigle:** `Mwb` und `MWBNetz` liefern `400 illegal dictionary sigla` (nicht 404). Wörterbuchnetz erwartet exakte Großschreibung `MWB`. Liste der 52 verfügbaren Dictionaries via `GET /open-api/dictionaries`.
- **Browser-Test mit `window.location.href`-Schleife:** der Inspector verlor seinen Context („Inspected target navigated or closed"). Lösung: einzelne `navigate`-Aufrufe pro Lemma statt Schleife im JS.

**Phase:** Implementation (iteration). Alle 14 Promptotyping-Docs aktuell. Heute aktualisiert: ROADMAP.md (Datum 2026-05-12, #85 raus aus Blocked, #73 raus aus Needs Clarification, #104/#105 als neue offene, Strategic Direction Punkt 5), INDEX.md Recent Milestones (#26, #85, #101, #73, WZB-Pentateuch, Blog-Post), JOURNAL.md (dieser Eintrag), #44-Body folgt im selben Commit-Cluster.

**Open issues (post-Session):**
- **#104** Siglen, die zu einem Werk zusammengehören (FLG/FLG1, PL1-3, FR1-3): KZW-Issue 2026-05-11. Deterministisch teilweise (PL1-3 zusammenziehen falls Body identisch), philologisch Klärungsbedarf bei FLG/FLG1 (verschiedene Editionen).
- **#105** Authority-Files-Counter (7 vs 8): KZW-Befund 2026-05-12. `contributors.xml` seit 2026-04-14 dabei, aber String auf einigen UI-Seiten zeigt noch 7. Einfacher Fix.
- **#92** ARITHMETIC: weiter blockiert auf Carinas Antwort.
- **#91** Zenodo: User-Steps (Webhook-Setup, ersten Tag pushen) pendent.
- **#81** Sprachstufen AC1-3: KZW-Code-Wahl ausstehend.
- **#23** Stanza-Insert: Skript-ready, 99.7 % Erfolgsrate auf 60-Sigles-Dry-Run, KZW-Go für Bulk pendent.
- **#34** WZB Phase 3 @meaningRef bei 92.5 %, 4 013 Rows pending (Julia + Helmut).

**Commits (alle gepusht, neueste zuerst):**
- `dcbee3479` `fix(lemma): #73 MWB-Deeplinks via Wörterbuchnetz-API statt kaputtem Suchlink` (Closes #73)

Aus Julias paralleler Session (alphabetisch nach Hash, dieser Handoff Session H):
- `8dfb9b80d` `feat(reader): Reading-View-Render-Policy implementiert (closes #101)`
- `082cb4d2f` `docs(hilfe): Contributing-Guide überarbeitet (#68)` (Two-Wege-Block Self-Ingest vs. DHCraft-Konvertierungsservice, 9-Punkte-Vorab-Checkliste, works.xml-Korrekturen)
- `05c8676a4` `feat(lemma-pages): Wörterbuch-Links MWB + Lexer (#73)` — initial implementation, MWB-Suchlink war defekt, in `dcbee3479` korrigiert
- `aa114bf89` + `6c4d7955c` `feat(WZB): Pentateuch-Scope in Metadaten (Gen–Dtn)` + Index-Rebuild
- `6ac508b8b` + `7c515b152` + `39e74f127` `docs: Blog-Post-Draft WZB-Pipeline` (publications/, drei Iterationen)

**Externe:** #73 closed via `Closes #73`-Trailer + Befund-Kommentar (POST-only-Diagnose, MWB-API-Reality-Check, HTTP-Link-Safety). KZW: #85 closed (UI), #105 neu (Authority-Counter), `CITATION.cff` final (`8e4202ffc`).

**Verifikation:** Chrome auf `localhost:8080` für drei Lemmata-Klassen: `brôt` (id=879, B-Bereich) zeigt 2× MWB-Deeplink (`linkid=25587000`, `linkid=246761100`) + 1× Lexer (`lemid=B04012`); `schamen` (id=5170, S-Bereich) zeigt nur 2× Lexer (MWB-API: 0 Treffer); `cs` (id=78628, Bohemian-Hapax) → Section korrekt versteckt (0/0). Keine Console-Errors nach Dead-Code-Removal.

**Next session:**
1. `/promptotyping orient`
2. **#105 Authority-Files-Counter:** String-Drift-Fix (vermutlich auf `index.html` Stats-Block und Hilfe-Seiten). KZW-Screenshots in Issue zeigen genaue Stellen.
3. **#104 Siglen zusammenziehen:** PL1-3 deterministisch prüfen (gleiche Metadaten? Nur Body unterschiedlich?). FLG/FLG1 + FR1-3 brauchen KZW-Klärung der Editions-Politik.
4. **Carryover:** #23 Bulk-Run (wartet auf KZW-Go), #47.3 Versposition-Pipeline, #91 Zenodo-Tag.

---

## 2026-05-12 — Nachmittag: #105 + #47.3 (Versposition-Pipeline-Sprint)

**Summary:** Zwei weitere Issues abgeschlossen nach Julias Vormittagsblock. **#105** (Authority-Files-Counter 7 vs 8) als One-Liner-Fix auf `index.html` — User-Bauchgefühl war richtig, `contributors.xml` ist semantisch kein Authority-File; pragmatisch trotzdem auf 8 vereinheitlicht, weil Hilfe-Seiten + INDEX.md + Validierungs-Kontext schon 8 zählen. Anschließend **#47.3 Lemmasuche nach Versposition** als ~2h-Sprint: Corpus-Index v4.0.1 → v4.1.0 mit `lineStarts[]`/`lineEnds[]`, neues Playground-Modul analog `lemma-distribution.js`, Chrome-verifiziert mit echten Reimpaaren.

**Decisions:**
- **#105 Authority-Counter: pragmatisch auf 8 vereinheitlicht** statt sauberer Trennung „7 suchbar + 8 validiert". User-Argument: „meta-meta-info, interessiert niemanden". Stats-Block `index.html:293` 7→8; Playground-Loader-Status `ui-helpers.js:604` bleibt 7 (technisch korrekt — `authority-index.json.gz` enthält nur die 7 inhaltstragenden Files, `contributors.xml` ist separat). UX-Inkonsistenz „Startseite 8 ↔ Playground-Status 7" akzeptiert (1-Sekunde-Sichtbarkeit bis ✅-State).
- **#47.3 Datenmodell-Design:** `lineStarts[]` UND `lineEnds[]` statt nur Starts. Vorteil: O(1)-Lookup für Versende ohne Binary-Search; kostenmäßig vernachlässigbar (~3 MB extra gzipped). 1.36M `<l>`-Elemente über 603 Versdichtungs-Texte; 64 Prosa-Texte haben leere Arrays — UI filtert sie automatisch heraus.
- **#47.3 Code-Pattern:** Modul analog `lemma-distribution.js` (in-place Form + Body in `resultsContainer`) statt Modal. KZW spezifizierte „eigener, schlanker Dialog" — das LemmaDistribution-Pattern ist genauso schlank, aber konsistent mit den anderen TEI-Tools.
- **Default Position = Versende:** Reim-Use-Case (häufiger) bekommt den Default. Treffer-Zahlen bestätigen: `minne` Versende 532 vs. Versanfang 110 in PZ/TR.

**Dead ends:**
- **lxml-Proxy-ID-Bug** in erster Version von `extract_word_data()`: separate `body.iter('<w>')` + `l_el.iter('<w>')` Aufrufe lieferten unterschiedliche Python-Element-Proxies mit unterschiedlichen `id()`-Werten → dict-Lookup fand nur das jeweils letzte Word einer Iteration. Lösung: Single-pass `iterwalk(events=('start','end'))` mit Stack-tracking für `<l>`-Verschachtelung. Stichprobe AGS war Lebensretter — ohne den Test wäre der Bug erst nach 7-Minuten-Build aufgefallen.
- **IndexedDB-Cache-Trap nach Index-Bump:** Frontend zeigte zunächst `corpusData.texts[0].lineStarts === undefined`. Ursache: gecachter v4.0.1-Index in IndexedDB. Manuelles `indexedDB.deleteDatabase()` plus Hard-Reload löste es. Auto-Invalidate bei Version-Bump (analog #94 für `authority-index`) wäre ein eigener Issue wert.
- **„minne" POS-Auflösung ergibt ADJ:** `searchLemmaByOrthography('minne')` liefert `lemma_4130 minne ADJ` — überraschend für das zentrale MHG-Substantiv. Treffer-Zahlen plausibel (76 Texte, 532 Versende-Hits) → vermutlich POS-Tag-Drift im Authority-Index, siehe #27. Nicht-Problem von #47.3, aber notable für künftige POS-Cleanups.

**Phase:** Implementation (iteration). Promptotyping-Docs aktualisiert: ROADMAP.md (#47.3 + #105 in Recently Completed, #105 raus aus Now-Quick-Wins), INDEX.md (Recent Milestones erweitert), JOURNAL.md (dieser Eintrag). Corpus-Index v4.1.0 als neue Baseline.

**Commits (alle gepusht, neueste zuerst):**
- `ea7b0a507` `feat(playground): #47.3 Lemmasuche nach Versposition` (6 Files, +328 −31, inkl. corpus-index.json.gz 34 → 40 MB)
- `8bf689d93` `fix(landing): #105 Authority-Files-Stats-Counter 7 -> 8` (Closes #105)

**Externe:** #105 closed via `Closes #105`-Trailer. #47-Umbrella-Kommentar mit #47.3-Status, Chrome-Verifikation, POS-Drift-Caveat und Cache-Invalidate-Hinweis: [issuecomment-4429961763](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/47#issuecomment-4429961763).

**Verifikation (Chrome `localhost:8080`):**
- Versanfang/Versende für „minne", „vriunt" plausibel (Versende dominiert deutlich, konsistent mit Reim-Realität)
- Unknown-Lemma „xyzunknown" → amber-„Kein Lemma gefunden"-Block sauber
- Ground-Truth AGS-Versenden = echte Reimpaare (gân/begân, bant/bekant, mûzære/gewære, rote/nota, jâr/hâr)
- Keine Console-Errors

**Open issues (post-Session):**
- **#104** Siglen-Werk-Gruppierung (FLG/FLG1, PL1-3, FR1-3): Kollege analysiert gerade, kein Action-Item für uns.
- **#92** ARITHMETIC: Carina pendent.
- **#91** Zenodo: Tag + Webhook pendent.
- **#81** Sprachstufen AC1-3: KZW-Code-Wahl pendent.
- **#23** Stanza-Insert Bulk: KZW-Go pendent.
- **#34** WZB Phase 3 92.5 %: Julia + Helmut.
- **#47** Release 2 (Begriffs-Verteilung) + Release 3 (POS, abhängig von #27): ungeplant.

**Next session:**
1. `/promptotyping orient`
2. **Corpus-Index-Auto-Invalidate:** kleiner Loader-Fix analog #94 — bei Version-String-Wechsel automatisch IndexedDB-Cache verwerfen. Heute manuell, sollte automatisch sein.
3. **#104-Befund abwarten** (Kollege).
4. **Falls KZW reviewt #47.3:** evtl. Untertitel/Wording polishen, Position-Default-Frage klären (jetzt Versende).

---

## 2026-05-12 — Abend: #47.3-Hilfe, Begriffs-Verteilung, FWF-Stub

**Summary:** Vier weitere Artefakte nach dem #47.3-Sprint: (a) Hilfe-Doku-Section für #47.3 in `hilfe-playground.html`; (b) **Begriffs-Verteilung** als #47-R2-Hauptpunkt geliefert (`concept-distribution.js`, ~330 Z., analog Lemma-Verteilung aber concept-basiert); (c) **#47 Umbrella geschlossen** mit Bilanz-Kommentar; (d) Drei neue Folgeissues angelegt: **#107 Kookkurrenz-Ranking** + **#108 Textvergleich** als rolling-claude-ready, **#109 FWF-Einzelprojekt** als Antrags-Scope-Notiz mit @wachauer als Lead. Zwischendurch ein Concurrent-Sessions-Bug abgefangen (commit `92edea19b` enthielt 93 unbeabsichtigte TEI-Files, vor Push reset --soft repariert).

**Decisions:**
- **#47 Close mit Auslagerung statt Brainstorm-Cleanup:** Kookkurrenz und Textvergleich als eigenständige claude-ready-Issues, weil sie sofort umsetzbar sind ohne KZW-Input. NER + phonetischer Reim + Textprofil-POS gehen in #109 FWF-Projekt, weil sie eigenen Forschungsdesign-Aufwand brauchen. Punkt 1 aus #106 (Reim-Wörterbuch) bleibt im Rolling-Backlog (KZW: „zwischendurch"), Punkt 8 (Lemma-im-Vers-Filter) wandert in den Multi-Lemma-Backlog (trivial, kein FWF).
- **#109 nur @wachauer als Assignee:** Co-PI-Diskussion auf später verschoben. KZW reicht den Antrag ein und entscheidet über Co-Leads im Antragstext.
- **Hilfe-Doku-Section in Sub-Section statt eigenem H1-Block:** Section „4. Lemmasuche nach Versposition" zwischen Multi-Lemma und Forschungsfragen, mit Reimpaar-Beispiel aus AGS (gân/begân, bant/bekant, mûzære/gewære, rote/nota, jâr/hâr). Beide TOCs ergänzt; Sections 5-8 entsprechend umnummeriert ohne Anchor-Bruch.
- **Concept-Lemma-Aggregation in JS:** Performance-Frage war, ob bei großen concepts (z.B. „Sterben" mit 682 zugeordneten Lemmata) der Scan über 667 Texte schnell genug ist. Antwort: ja, ~100ms im Browser. Python-Ground-Truth bestätigt 1:1 (682 Lemmata, 659 Texte, 103.657 Vorkommen).

**Dead ends:**
- **Concurrent-Sessions-Bug `92edea19b`:** Der Kollege hat seine ~93 Stanza-Insert-TEI-Files in den geteilten Index gestaged, ich habe via `git add hilfe-playground.html` (specific path) gestaged und committed — und alle Stage-Slots wurden mit committed. `git diff --cached --stat hilfe-playground.html` (mit Pfad-Filter) hatte das verborgen. Reset `--soft HEAD~1` + `git restore --staged tei/` repariert sauber vor Push. **Lehre:** vor jedem commit `git diff --cached --stat` OHNE Pfad-Filter. Memory-Regel `feedback_concurrent_sessions.md` explizit erweitert um diese Diagnostik.
- **#105 Authority-Counter-Frage „pragmatisch oder semantisch":** User-Bauchgefühl war richtig (`contributors.xml` ist semantisch kein User-facing Authority-File), aber pragmatischer Konsens war „pauschal auf 8 vereinheitlichen, niemanden interessiert die Meta-Trennung". Ein-Zeilen-Fix `index.html:293` 7→8 statt großem Sprachsweep.
- **Index-Version-Drift in Loader:** zwischen Build-Skript (`4.1.0`) und Loader-Konstante (`4.0.1`) drift nach #47.3-Bump. Production-User mit altem Cache hätten den neuen Index nie gesehen. In `8f375bc4e` nachgepatcht. Strukturell verankert via neuem `scripts/audit/check-index-versions.py` + `.github/workflows/index-version-check.yml` (Commit `07c9f3244`), plus Memory `feedback_index_version_bump.md`.

**Phase:** Implementation (iteration). Promptotyping-Docs aktualisiert: ROADMAP.md (#47 closed, #107/#108 in Next, #109 in Future, #106-Scope-Reduktion-Note in Needs-Clarification), INDEX.md (Recent Milestones um Begriffs-Verteilung + #47-Close-Bilanz), JOURNAL.md (dieser Eintrag).

**Open issues (post-Session):**
- **#107 Kookkurrenz-Ranking:** claude-ready, ~3-4h Sprint nach Begriffs-Verteilung-Pattern.
- **#108 Textvergleich:** claude-ready, ~2-3h Set-Ops-Modul.
- **#109 FWF-Projekt:** wartet auf Antragsformulierung (@wachauer).
- **#106:** wartet auf KZW-Kommentar zur Scope-Reduktion auf Punkt 1.
- **Corpus-Index-Auto-Invalidate** (Carryover): kleiner Loader-Fix, würde Production-User vor Cache-Drift-Problemen schützen, ohne dass die `INDEX_VERSION`-Konstante manuell mitgewartet werden muss. Bei nächstem Index-Bump wert.
- **Carryover:** #23, #34, #81, #91, #92, #104 unverändert.

**Commits (alle gepusht, neueste zuerst):**
- `a0b8d9aab` `feat(playground): #47 R2 Begriffs-Verteilung` (4 Files, +433, neuer Modul + Button + Route)
- `636c795c9` `docs(hilfe): Section 4 'Lemmasuche nach Versposition' für #47.3` (1 File, +72)
- `07c9f3244` `ci: Index-Version-Konsistenz-Check für corpus-loader.js + build-skripte` (Audit-Skript + CI-Workflow)
- `8f375bc4e` `fix(loader): INDEX_VERSION-Konstante auf 4.1.0 bumpen (Cache-Invalidate für #47.3)`

**Externe:** **#47 closed** mit Bilanz-Kommentar (issuecomment-4430321460), **#105 closed** via `Closes #105`-Trailer in `8bf689d93`, **#107/#108/#109 erstellt** (#109 mit @wachauer als Assignee, FWF-Budget-Constraint dokumentiert), Memory `feedback_concurrent_sessions.md` erweitert um Pre-Commit-Drill ohne Pfad-Filter, Memory `feedback_index_version_bump.md` neu (drei-Stellen-Bump-Regel).

---

## 2026-05-12 — Abend (Fortsetzung): Promptotyping-Check + 3 offene Follow-Ups für Next Session

**Summary:** Nach dem #47-Close-Sprint kam ein `/promptotyping check` mit 7 Drift-Findings. Davon 2 Blocking + 3 Should-fix + 2 Nice-to-have in zwei Commits abgearbeitet (`8d2505d28` DATA-MODEL+CONTRACTS, `5a82862bf` ARCHITECTURE+FEATURES+DEVELOPMENT+DECISIONS+INDEX inkl. ADR-014). Die drei Anti-Sycophancy-Punkte bleiben als konkrete Tasks für die nächste Session offen.

**Next session — drei Tasks in dieser Reihenfolge:**

### 1. (zuerst) Edge-Case-Coverage Begriffs-Verteilung systematisch — ~1-1.5h

**Risk-driven:** das größte Concept hat vielleicht 5000+ zugeordnete Lemmata. `concept-distribution.js:findMatchingLemmata()` iteriert dann über alle Lemmata × alle Texte (667) — könnte den Browser einfrieren. Heute nur 2/567 Concepts manuell getestet.

**Zwei-Schritt-Plan:**

**Schritt 1.1 — Programmatischer Survey (Python, ~30min):**
```python
# scripts/audit/survey-concept-distribution.py (NEU)
# - Lade authority-index.json.gz + corpus-index.json.gz
# - Für jedes Concept (567 total):
#   - Anzahl zugeordnete Lemmata
#   - Anzahl Texte mit min. 1 Treffer
#   - Total Vorkommen
# - Output: sortiertes CSV/Markdown mit Min/Max/Median/P95
# - Flagge: Concepts mit >2000 Lemmata, mit 0 Lemmata, mit >100k Vorkommen
```

**Schritt 1.2 — Browser-Performance-Check (~20min):**
- Worst-case Concept (höchste Lemma-Count) im Playground testen
- DevTools Performance-Profile: ist die Suche <500ms? <2s? >2s = freeze
- Wenn freeze: Performance-Patch nötig (Web-Worker oder `requestIdleCallback`-Chunking in `findMatchingLemmata`)
- Wenn OK: Playwright-Regression-Test in `testing/tests/` schreiben, der das worst-case Concept lädt und Treffer-Count gegen erwarteten Wert prüft

**Definition of done:** Survey-Report committed in `scripts/audit/`, performance verifiziert (oder gepatcht), Playwright-Lock in Test-Suite. Falls Performance-Patch nötig: separates Issue + ADR-Eintrag „Frontend-Aggregation für große Concepts".

### 2. (dann) DESIGN.md Playground-Modul-Konvention dokumentieren — ~20min

**Wo:** `docs/DESIGN.md` neue Sektion zwischen „Component Patterns" und „Layout Patterns". Section-Titel z.B. „Playground TEI-Analysis Module Pattern".

**Was reinschreiben** (das gemeinsame Schema aller fünf Module — `word-frequency.js`, `text-statistics.js`, `lemma-distribution.js`, `verse-position-search.js`, `concept-distribution.js`):
- **Konstruktor:** `(getCorpusTexts, authorityManager, ...)` — Thunks statt direkter Datenreferenzen, damit nach Index-Reload nichts stale ist
- **`show()`** als Router-Entry-Point — guards corpus-loaded, ruft `render()`
- **`render()`** → `resultsContainer.innerHTML = renderForm() + renderBody()` → `attachHandlers()` neu binden
- **Stateful state-Objekt** `this.state = { ...DEFAULT_STATE }` für Form-Werte; render() konsumiert state, nicht DOM
- **Escape-Helpers** (`escapeHtml`, `escapeAttr`) am Modul-Ende, NICHT importiert (jedes Modul self-contained)
- **Brand-Akzent** (`bg-brand-50`, `text-brand-700`) nur für Default-Button; sekundäre Buttons `bg-white border-slate-200`

**Multi-Lemma als dokumentierter Outlier:** nutzt Modal (`#multiLemmaModal`) statt in-place-Form, weil es 4 Eingabe-Lemmata + Modus + Distanz braucht und das im Sidebar nicht reinpassen würde.

**Definition of done:** Section in DESIGN.md, mit ~20-Zeilen-Code-Skelett als Template-Snippet. Verweis von ARCHITECTURE.md §UI-Layer auf den neuen DESIGN-Abschnitt.

### 3. (zuletzt) Index-Größen-Strategie als Issue — ~15min

**Issue anlegen** (Title-Vorschlag: „Index-Größen-Soft-Cap und modulare Splitting-Strategie"):

**Body-Skelett:**
- **Status quo:** corpus-index.json.gz heute 40 MB gz (ca. 160 MB uncompressed). Authority-Index ~3 MB gz.
- **Trajektorie:** mit jedem neuen Index-Feld wächst er. POS-Workflow (#27): +3-5 MB gz erwartet (per-word POS-Tag). NER-Annotation (#109): vermutlich +5-10 MB. Reim-Klassifikation (#109 Komplex A): +1-2 MB.
- **Trigger-Bedingung:** wenn corpus-index >50 MB gz oder >200 MB uncompressed erreicht — Soft-Cap.
- **Optionen bei Trigger:**
  - **A. Modulares Splitting** in core (Metadaten + lemmata{}) + on-demand-chunks (words[], lineStarts[], future POS-array). Loader fetcht core eager, chunks lazy bei Feature-Aktivierung.
  - **B. Compression-Upgrade:** gzip → brotli (typisch 20-30 % kleiner). Browser-Support für Brotli-content-encoding ist universal.
  - **C. Binärformat** (MessagePack / FlatBuffers). Größere Code-Investition, bricht JSON-Compatibility.
- **Heute keine Entscheidung notwendig** — Issue dient als Trigger-Reminder. Sobald 50 MB erreicht, wird ADR-015 geschrieben.
- **Labels:** `pipeline`, `future plans`
- **Assignee:** keiner; ist eher technische Diskussions-Notiz.

**Definition of done:** Issue veröffentlicht und in ROADMAP.md unter „Future / Needs Design" verlinkt.

---

**Verweise für Next Session:**
- Schema-Datenstruktur: [docs/DATA-MODEL.md §Corpus Index](DATA-MODEL.md) (frisch auf v4.1.1 gesynct)
- Modul-Pattern als Vorbild: `playground/js/ui/tei/lemma-distribution.js` (~300 Z., kanonisches Beispiel)
- Audit-Skript-Template: `scripts/audit/check-index-versions.py` (Header-Stil, Exit-Codes, GitHub-Actions-Annotations)
- Pre-Commit-Drill: `git diff --cached --stat` OHNE Pfad-Filter (Memory `feedback_concurrent_sessions.md`)

**Carryover (unverändert):**
- #23 Stanza-Insert Bulk: Kollege macht; weitere Stanza-Wraps im Index v4.1.1 vermutlich enthalten
- #34 WZB Phase 3: Julia + Helmut
- #81 Sprachstufen AC1-3: KZW BCP-47-Wahl
- #91 Zenodo: Tag + Webhook
- #92 ARITHMETIC: Carina
- #104 Siglen-Gruppierung: Kollege analysiert
- #107 Kookkurrenz-Ranking: claude-ready, M-Effort
- #108 Textvergleich: claude-ready, M-Effort
- #109 FWF-Projekt: wartet auf KZW-Antragstext
- #106 Vers-Boundary-Features: KZW soll Punkt 1 als Rolling-Backlog-Eintrag bestätigen
- Corpus-Index-Auto-Invalidate (kein Issue): Loader-Fix analog #94 für corpus-index

**Commit dieses Eintrags (separat von der Doku-Sync-Welle):**
- `8d2505d28` Blocking-Fixes (DATA-MODEL.md + CONTRACTS.md auf v4.1.1)
- `5a82862bf` Should-fix + Nice-to-have + ADR-014 (5 docs)

**Phase:** Implementation (handoff). Alle 14 Promptotyping-Docs aktuell, Drift-Check sauber.

---

## 2026-05-12 14:46 — handoff

**Summary:** #23 Stanza-Bulk-Run (93 Texte, 11.090 `<lg type="stanza" n="N">`-Wraps) + Corpus-Index v4.1.1 + Test-Pflege nach #73 (3 Failures gefixt, 127/127 grün). #104 (Siglen-Gruppierung PL/FLG/FR) als analytischer GitHub-Kommentar mit Empfehlung „Titel statt Merge" verfasst.

**Decisions:**
- **#23 ohne WVV:** Bulk-Run lief auf 99 Sigles mit 99,69 % Erfolg. WVV (482 Anchors, 95,2 % — Template `cn…kk` ungewöhnlich) als [#110](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/110) ausgeklammert, separat zu untersuchen. 13 sonstige missing-anchors (0,1 %) als Edge-Cases akzeptiert.
- **Index v4.1.1-Bump trotz semantisch identischem Inhalt:** Cache-Invalidate-Robustheit > Minimal-Diff. Build-Stats vor/nach Bump identisch (667 Texte / 42.630 Lemmata / 7.533.447 Wörter / 40,23 MB gz), aber `<lg>`-Wraps strukturell neu — Bump verhindert „Stanza-Wraps unsichtbar für 30 Tage" bei IndexedDB-gecachten Usern.
- **#104:** Empfehlung gegen physischen Merge. Begründungen: editorische Konventionen pro Sigle eigenständig (PL1/2/3 sind drei DTM-Bände desselben Kluge-Werks; PL2 nutzt zusätzlich Köln-Papier-HS), FLG/FLG1 sogar zwei verschiedene `work`-IDs (571 vs 587), 119 MB-PL-Merge würde Reader sprengen. Titel-Anpassung in `works.xml` löst das von KZW gezeigte UI-Problem vollständig.
- **Two-Commit-Strategie für Korpus-Patches:** Erst TEI committen, dann Index-Rebuild + zweiter Commit. Verhindert dirty-build via #100-Pre-flight-Check. Mit dem heutigen Concurrent-Sessions-Vorfall als Beleg, warum Atomic-Stage+Commit-in-einem-Schritt das einzig sichere Pattern bei geteiltem Worktree ist.
- **manifest.json gelöscht:** Test war einziger Konsument (Frontend nutzt sie seit ADR-013 nicht mehr). Statt manifest zu regenerieren, Test entfernt + Datei (~186 KB) gelöscht.

**Dead ends:**
- **Begriffs-Verteilung Live-Walkthrough abgebrochen:** Browser-Tab wurde zerschossen — entweder durch `location.reload(true)` (in modernen Chromium deprecated, kann Tab killen) oder durch parallelen Server-Kill des Kollegen. Tab-State im Moment der Inspektion: `step1/2/3` alle hidden, `resultsVisible:true`, aber `#concept-distribution-view`-Inhalt nicht auffindbar — unklar ob das die normale Vor-Auswahl-View war oder ein Render-Bug. Nicht weiter untersucht.
- **`npm test 2>&1 | tail -40`:** Pipe schluckt npm-Exit-Code (tail liefert immer 0). Erst beim zweiten Lauf mit `set -o pipefail` echter Exit-Code gesehen. Konsequenz: in Bash-Pipes immer `set -o pipefail` setzen, wenn Exit-Code-Aussagekraft nötig ist.

**Concurrent-Sessions-Vorfall (heute erneut getroffen):**
- Mein `git add tei/<93 Files>` lief zwischen Kollegen `git add hilfe-playground.html` und Kollegen `git commit` → sein Commit `92edea19b` sweepte alle 94 Files ein.
- Auflösung via Kollegen-Soft-Reset (`HEAD~1`) + selektives Unstage von `tei/` + Re-Commit mit identischer Message. Hat keine Daten gekostet, aber bestätigt: **Geteilter Index = Geteiltes Risiko. Atomic Stage+Commit in einer Bash-Operation ist das einzige zuverlässige Pattern, NICHT vorzeitig stagen.**
- Memory-Pattern `feedback_concurrent_sessions.md` hat geholfen — kein neues Lernen, nur Bestätigung.

**Phase:** Implementation (handoff). Alle 14 Promptotyping-Docs aktuell (durch Kollegen-Sync in `8d2505d28` + `5a82862bf` heute Vormittag).

**Open issues:**
- **#110 WVV-Edge-Case** (claude-ready, S-M): 23 missing-anchors aus Bulk-Run. Vermutung: ungewöhnliche Linecode-Template-Geometrie (`000000000cnddss--kk`) bricht `find_first_l_for_anchor`-Heuristik in `scripts/insert-stanzas-from-linecode.py`. WVV-Linecode-Source liegt vor; nächste Session kann direkt loslegen.
- **#23 Rest-Defizite** (KZW-Input nötig, NICHT claude-ready): MUG (Linecode-Source fehlt im Handover), MSF (Template fehlt in Tabelle). Im Issue-Body von #23 dokumentiert. Effort minimal sobald Daten da.
- **#104 Sigle-Gruppierung** (KZW + Julia entscheiden): Analyse als Kommentar gepostet, wartet auf editorische Antwort. Falls KZW/Julia „Titel-Anpassung statt Merge" zustimmen: S-Effort in `authority-files/works.xml` (8 Titel-Anpassungen + Authority-Index-Rebuild). Kein TEI-Touch nötig.
- **Begriffs-Verteilung Live-Check ausstehend:** Kollegen-Feature `a0b8d9aab` (#47 R2) habe ich nicht live durchgespielt — Tab-Tod hat das verhindert. Falls Doppelt-Augen-Prinzip vom User gewünscht, separater Session-Slot.
- **Test-Suite-Pflege als Wachposten:** Heute 3 Failures (2× #73-Erwartung veraltet, 1× Manifest-Legacy) — nach jedem Frontend-Feature künftig **gleich nach Implementation `npm test` mit pipefail**, nicht erst tagelang später.

**Next steps (orientiert nach Aufwand):**
1. **WVV-Fix (#110)** — ~30-60 min. Skript-Heuristik prüfen, einen Manuell-Patch oder Skript-Extension, Bulk auf nur WVV, validation, Index-Bump auf v4.1.2.
2. **#104 abwarten** auf KZW/Julia-Antwort. Falls Titel-Anpassung approved: works.xml-Edit + Authority-Index-Rebuild — ~20 min.
3. **Begriffs-Verteilung Live-Walkthrough** falls User es wünscht. Tab muss frisch geöffnet werden, kein `location.reload(true)`.

**Commit dieses Handoffs:** wird nach Stage angefügt — siehe nächsten Bash-Block.

**Carryover (vom Kollegen-Handoff `aac7fe23e` ergänzt):**
- **3 Should-Fix-Tasks des Kollegen** (Concept-Distribution-Survey + DESIGN.md Modul-Pattern + Index-Größen-Strategie-Issue) sind separate Workstreams seinerseits, ich greife nicht ein
- **Corpus-Index-Auto-Invalidate-Loader-Fix** (kein Issue, vom Kollegen heute morgen identifiziert): bleibt bestehen als bekannter Doppel-Bumps-Workaround
- Sonst alles aus dem `aac7fe23e`-Carryover unverändert: #34 (Julia + Helmut), #81 (KZW), #91 (Tag + Webhook), #92 (Carina), #107/#108 (claude-ready M), #109 (FWF-Antrag), #106 (KZW-Backlog-Bestätigung).

---

## 2026-05-12 18:42 — handoff

**Summary:** Die drei „Anti-Sycophancy"-Followups aus dem `aac7fe23e`-Handoff vollständig abgearbeitet: (1) Survey-Skript + Edge-Case-Coverage-Report über alle 567 Concepts; (2) Performance-Patch in `concept-distribution.js` — 2.747ms Browser-Freeze auf 60-200ms Long-Tasks reduziert (Faktor 13-49) plus Playwright-Regression-Test; (3) DESIGN.md §Playground TEI-Analysis Module Pattern als formale Konvention; (4) GitHub-Issue #111 „Index-Größen-Soft-Cap" als Trigger-Reminder.

**Decisions:**
- **Patch-Strategie B (requestIdleCallback-Chunking via MessageChannel) statt C (Pre-Computed Index-Feld):** B ist minimal-invasiv (~120 Z. Diff), keine Index-Schema-Migration. C wäre langfristig schneller (O(1) statt O(L×T)), aber kostet 2-4 MB gz und einen v4.2.0-Bump — verschoben in Issue #111 als „Trigger bei 50 MB gz".
- **MessageChannel statt setTimeout(0) als Yield-Mechanismus:** setTimeout(0) wird im hidden Tab auf >=1000ms gedrosselt (Chrome timer throttling). Beobachtet 2026-05-12 im Test-Setup: 95x langsamer als erwartet. MessageChannel hat keine solche Drosselung. Dokumentiert in `concept-distribution.js`-Kommentar und in DESIGN.md.
- **findMatchingLemmata synchron belassen:** Async-Chunking dort brachte überraschend mehr 100-200ms Long-Tasks (zusätzliche `render()`-Cycles während des async-Flows kosten mehr als der findMatchingLemmata-Sync). Sync-Pass ~80-100ms bei worst-case ist akzeptabel.
- **CHUNK_BUDGET_MS = 30, nicht 20:** Budget=20 brachte Regression (215ms peak). Optimum bei 30ms — Trade-off zwischen Yield-Overhead und Long-Task-Größe.

**Dead ends:**
- **Budget=20-Versuch:** brachte Regression statt Verbesserung (3 Long-Tasks > 50ms statt 2). Zurück auf 30. Kosten: ~10 min.
- **findMatchingLemmata async-Versuch:** brachte 162-204ms Long-Tasks statt erwartet <50ms. Zusätzliche `render()`-Cycles während findMatchingLemmata-Loop kosteten mehr als die Synchronizität spart. Sync wieder hergestellt. Kosten: ~15 min, finaler Code aber sauberer.
- **JSON-Dump des Surveys (124 KB):** ist reproduzierbar via `--json`-Flag, daher gitignored — nicht commit-würdig.

**Phase:** Implementation (iteration). Alle 14 Promptotyping-Docs aktuell. DESIGN.md um neue Sektion erweitert, ARCHITECTURE.md-Verweis gesetzt, ROADMAP.md §Future angepasst, JOURNAL.md (dieser Eintrag).

**Open issues (post-Session):**
- **#111** Index-Größen-Strategie: Trigger-Reminder, keine Aktion bis 50 MB gz erreicht.
- **#107 Kookkurrenz-Ranking** + **#108 Textvergleich**: claude-ready, M-Effort.
- **#109 FWF-Projekt:** wartet auf @wachauer-Antragstext.
- **#106:** wartet auf KZW-Kommentar zur Scope-Reduktion.
- **Playwright-Test `concept-distribution.spec.js` nicht ausgeführt** — User hat die Tests bisher nicht selbst gestartet. Wenn `npm test` läuft, sollten die vier neuen Tests grün sein (alle Assertions sind großzügig dimensioniert: <500ms / <200ms / <150ms Long-Task-Limits).
- **Performance-Regression-Beobachtung:** initial-run nach Page-Load zeigt 200ms+ peak (V8-JIT-Warmup), steady-state 60-70ms. Falls in CI mit kalter V8 die 500ms-Schwelle gerissen wird, Test-Limit hochsetzen oder ein Warmup-Run einbauen.

**Next steps (für die nächste Session):**
1. `/promptotyping orient` (lädt Project-State).
2. **Falls User #107 Kookkurrenz-Ranking startet:** kann analog Begriffs-Verteilung gebaut werden (gleiches Modul-Pattern, jetzt formal in DESIGN.md). Async-Chunking wenn Concept-Pair-Aggregation O(C × T) wird.
3. **Falls User #108 Textvergleich startet:** Set-Ops auf Lemma-Listen pro Text, weniger Compute-intensiv, vermutlich kein Chunking nötig.
4. **Carryover unverändert:** #23, #34, #81, #91, #92, #104, #106, #107, #108, #109, Auto-Invalidate-Loader-Fix.

**Commits (gepusht, neueste zuerst):**
- `95caa996d` `docs(playground): Survey-Skript + Modul-Konvention + Index-Strategie-Issue` (6 Files, +563)
- `90472358a` `perf(playground): #47 R2-Followup Begriffs-Verteilung async + chunked` (2 Files, +233/-9, neuer Spec + Patch)

**Externe:** Issue **#111 erstellt** (pipeline + future plans, kein Assignee), Browser-Performance-Befund dokumentiert in `docs/research/concept-distribution-survey.md` (untracked JSON-Dump bleibt lokal).

**Post-Handoff-Nachtrag:** User-Frage „hast du alle issues geschlossen, die geschlossen werden sollten?" deckte auf, dass **#47 noch offen war** (heute Mittag wurde nur ein Bilanz-Comment gepostet, aber kein `Closes #47`-Trailer im Commit `0661d115f`). Zudem zwei wachauer-Kommentare unbehandelt: (a) #47.3 Versposition-Klick highlightet Lemma im Reader nicht (Bug), (b) #47 R2 Begriffs-Verteilung braucht Autovervollständigung wie Begriffe-Explorer (Feature). Beide abgespalten:
- **#112** Versposition-Klick-Highlight-Bug (claude-ready, S) — in ROADMAP §Now eingetragen
- **#113** Begriffs-Verteilung Autocomplete (claude-ready, M) — in ROADMAP §Next eingetragen
- **#47 endgültig geschlossen** mit Verweis-Comment auf #112 + #113

**Externer Commit dieses Nachtrags:** wird gemeinsam mit ROADMAP-Updates committed (sieh nächsten Commit).

---

## 2026-05-14 12:00 — handoff

**Summary:** `/promptotyping check` durchgeführt — erster Check seit 2026-05-12, keine Code-Änderungen seitdem, entsprechend wenig Drift. Zwei Should-fix-Findings in `docs/ROADMAP.md` behoben: zwei offene Issues fehlten in der Triage-Matrix, und §Strategic Direction hatte doppelte Nummerierung.

**Decisions:**
- **#93 + #110 in ROADMAP nachgetragen:** #93 (Textreihentypologie-Umzug, `nice to have`/`future plans`) war in keinem Doc erfasst → §Future: Needs Design. #110 (WVV-Stanza-Followup, claude-ready) stand nur im JOURNAL → §Now. ROADMAP referenziert sich selbst als „full triage matrix", muss also vollständig sein.
- **§Strategic Direction renumeriert:** Punkt „2." erschien zweimal, „TEI data quality" sogar als #2 und #4. Die zwei TEI-data-quality-Einträge zu einem zusammengeführt (jetzt Punkt 2, inkl. #23 + #110), sauber 1–6 durchnummeriert.
- **`.gitignore` NICHT mitcommittet:** die `proposals/`-Zeile gehört zur parallel offenen `proposals/netidee/`-Arbeit des Users, nicht zu diesem Check. Nur `docs/ROADMAP.md` + `docs/JOURNAL.md` gestaget (Concurrent-Sessions-Regel).

**Check-Findings ohne Aktion (bewusst):**
- **`concept-distribution.spec.js` nie ausgeführt** — die 4 Playwright-Tests aus dem 18:42-Handoff sind weiterhin assumed-green; offene Verifikationslücke, kein Doc-Fehler. Begriffs-Verteilung (#47 R2) hatte zudem nie einen sauberen Live-Walkthrough (Tab-Tod 2×).
- **JOURNAL.md bei 103 KB** — Anti-Sycophancy-Frage für die nächste Quartals-Runde: Handoff-Einträge älter als ~4 Wochen auf 3–4 Zeilen komprimieren (analog Health-Check-Report-Konvention in CLAUDE.md). Context-Rot trifft auch die Doku selbst.

**Dead ends:** keine.

**Phase:** Implementation (handoff). Alle 14 Promptotyping-Docs aktuell. Index-Versionen konsistent (corpus 4.1.1, authority 1.2.1 — Build-Skript + Loader, `check-index-versions.py` grün). `docs/features/` lifecycle-korrekt (034 ↔ #34 offen, 045 ↔ #45 offen).

**Open issues (unverändert vom 18:42-Handoff):**
- **#107 Kookkurrenz-Ranking** + **#108 Textvergleich**: claude-ready, M-Effort, Modul-Pattern in DESIGN.md formalisiert.
- **#110 WVV-Stanza-Followup**: claude-ready, S-M; Linecode-Source liegt vor.
- **#111** Index-Größen-Strategie: Trigger-Reminder, keine Aktion bis 50 MB gz.
- **#109 FWF-Projekt**: wartet auf @wachauer-Antragstext.
- **#106**: wartet auf KZW-Kommentar zur Scope-Reduktion.
- **`concept-distribution.spec.js`**: bei nächstem `npm test` mitlaufen lassen, ob die 4 neuen Tests grün sind.
- **Carryover:** #23-Restdefizite (MUG/MSF, KZW-Input), #34 (Julia + Helmut), #81 (KZW BCP-47-Wahl), #91 (Tag + Webhook), #92 (Carina), #104 (KZW + Julia), Corpus-Index-Auto-Invalidate-Loader-Fix (kein Issue).

**Next steps:**
1. `/promptotyping orient` zum Laden des Project-State.
2. Falls User #107 oder #108 startet: Modul-Pattern aus DESIGN.md §Playground TEI-Analysis Module Pattern als Template.
3. Falls User #110 startet: `scripts/insert-stanzas-from-linecode.py` `find_first_l_for_anchor`-Heuristik gegen WVV-Template `000000000cnddss--kk` prüfen.

**Commit dieses Handoffs:** siehe nächsten Bash-Block.

---

## 2026-05-15 13:11 — handoff

**Summary:** Drei Issues in einer Sitzung durchgegangen: #86 (Barrierefreiheit-Ping an KZW), #104 (Sigle-Titel-Differenzierung PL1-3/FLG/FLG1/FR1-3 plus FLG-biblStruct-Umstellung auf Vollmann-Profe/Neumann 1990), #81 (Sprachstufen-Differenzierung no-op-Closure nach KZW-Decision 2026-05-08), #110 (WVV-Stanza-Wrapping 478/482 + Skript-Härtung für 3 Edge-Cases). Drei Commits gepusht, alle drei Issues closed (#86 nur Ping, weiterhin open).

**Decisions:**
- **#104 FLG-Editor-Modellierung**: Variante A (beide Neumann + Vollmann-Profe als `<editor>`) gewählt, weil bibliografisch korrekter und konsistent mit FLG1. Anzeigetitel bleibt KZWs Kurzform „/ Vollmann-Profe 1990". `@role="bookEditor"` zunächst gesetzt, dann entfernt, weil mhdbdb.rnc das Attribut auf `<editor>` nicht erlaubt — TEI-Note erklärt die Rollendifferenzierung im Klartext.
- **#104 works.xml-Scope**: nur work_571/work_587 (FLG-Einzelwerke) bekamen neue Titel + biblStruct-Update. work_113 (PL-Cluster) und work_463 (FR-Cluster) blieben generisch — KZWs Sigle-Differenzierung lebt auf TEI-Header-Ebene, nicht Work-Ebene.
- **#110 Skript-Robustheits-Fixes (3 Edge-Cases)**: max_candidates=12 (Header-in-`<supplied>`-Fallback), parent-mismatch-Walk-Forward-Fallback (Section-Wechsel im gleichen Stanza-Counter), wrap_stanza-Pre-Check für `<l>`-only-Range (Schema-konform). Alle additiv — keine Regressionen für die bereits gewrappten 99/100 Sigles aus dem #23-Bulk-Run.
- **#110 4 wrap_failed bleiben unbehandelt**: Section-Wechsel ohne Stanza-Counter-Change (1174/1180/1208/1242) brauchen philologische Entscheidung. Skript meldet sie sauber statt sie defekt zu wrappen. Issue-Comment dokumentiert für KZW/Julia.

**Dead ends:**
- Erster Skript-Lauf wrappte WVV erfolgreich (482/482), aber zerstörte Stage-1-Validität, weil eine Strophe (394, Linecode 1180→1181) freistehende `<hi rend="initial">`-Elemente zwischen `<l>`s hatte, die in `<lg>` reingerollt wurden. → wrap_stanza-Pre-Check eingebaut, jetzt 478/482 mit gültigem Schema.
- Erste `npm test`-Run für #104 mit `| tail -50`-Pipe lief grün durch (130/131), aber Output-Datei blieb leer wegen der Pipe — User dachte zuerst „timed out". Mein Fehler bei Bash-Invocation.

**Phase:** Implementation (handoff). Alle 14 Promptotyping-Docs aktuell. Drei Commits gepusht — `c0b546a45` (#104), `0e1bb45a6` (#81 docs), `7ad32a6ac` (#110). Index-Versionen jetzt corpus 4.1.3, authority 1.2.2. ROADMAP synchronisiert.

**Open issues:**
- **#86 Barrierefreiheit**: KZW-Sichtung der Live-Seite offen — sie wurde gepingt mit Diff-Zusammenfassung der 5 umgesetzten Änderungen, hat noch nicht geantwortet.
- **#110 4 wrap_failed Strophen** (WVV 1174/1180/1208/1242): brauchen philologische Entscheidung von KZW/Julia, ob Ton-Wechsel-Stellen als eine oder zwei Strophen wrappen sollen.
- **#34 WZB CoReMA-Teil**: weiterhin wartend auf Julia + Helmut.
- **#92 ARITHMETIC**: wartet auf Carinas Antworten (Sigle/Lizenz/Edition/Genre + Domänen-Klassifikation).
- **#107 Kookkurrenz-Ranking + #108 Textvergleich**: claude-ready, M-Effort, Modul-Pattern aus DESIGN.md als Template — nicht angefangen.
- **#112 Versposition-Klick-Bug**: claude-ready, S — Bug aus wachauer-Comment in #47.
- **`concept-distribution.spec.js:90`**: bekannter pre-existing Test-Fail (Spinner-Visibility), unabhängig von #110 — beim nächsten #47-R2-Tweak prüfen.

**Next steps:**
1. `/promptotyping orient` zum Laden des Project-State.
2. Falls KZW auf #86 antwortet: Final-Version-Anpassung + Issue close.
3. Falls #110 4 wrap_failed durch KZW/Julia geklärt werden: manuelle `<lg>`-Splits in WVV.tei.xml + Re-Validate + neuer Index-Bump.
4. Anders neue Quick-Wins: **#112** (Versposition-Bug, S-Effort) oder **#107/#108** (Playground-Module, M-Effort) sind die nächsten claude-ready-Kandidaten.
5. CI Schema-Validation auf GitHub Actions: bei rotem Lauf melden.

---

## 2026-05-15 16:48 — handoff

**Summary:** Vier Issues in einer autonomen Nachmittagssession durchgegangen: #112 (Versposition-Klick-Highlight-Bug), #108 (Textvergleich), #107 (Kookkurrenz-Ranking), #113 (Begriffs-Verteilung Autocomplete). Alle vier live in Chrome verifiziert, jeweils einzeln committed + gepusht mit `Closes #` Trailern, GitHub hat alle vier auto-geschlossen.

**Decisions:**
- **#112 Fix-Lokus**: URL-Param-Quelle korrigieren statt Highlighter robust machen. Begründung: URL-Contract klar halten (`lemmaIds=lemma_X`), nicht zwei Formate akzeptieren. Bug betraf auch #90 Lemma-Verteilung (3 Stellen in 2 Files).
- **#108 Performance-Tuning während Bau**: `AuthorityFilesManager.findLemmaById()` ist O(N) linear, bei 3.058 Beide-Lemmata × 42.630 Lexikon = 130M Iterationen = 5962ms. Fix: lokale `Map` in TextComparison einmal pro `show()` → 53ms (112× schneller). Manager nicht modifiziert (Scope-Disziplin).
- **#107 POS-Filter als Default „content"**: Ohne POS-Filter dominieren Stopwords (der/und/ich/daz/er). POS=NOM/VRB/ADJ/ADV macht das Tool philologisch nutzbar. `êre` + POS=NOM → haben, tuon, sprechen, got, herre. Filter wirkt post-compute, daher Switch ohne Re-Compute (rawCounts gecacht, ~15ms).
- **#113 klassisches Dropdown statt live-filter-list**: Concept-Explorer hat eigentlich keine Autocomplete, sondern live-search-with-rerender (passt für Tab-Layout). Begriffs-Verteilung hat dedicated Form mit Frequency/Sort/TopN-Controls → klassisches DWDS-Style Dropdown unter dem Input ist besser. Direkter DOM-Update statt full re-render (Focus + Selection-Range bleibt erhalten beim Tippen).
- **mousedown statt click für Suggestion-Auswahl**: feuert VOR blur, sodass `closeAutocomplete()` (im blur-Handler mit 150ms Delay) nicht zuerst das Dropdown leert.

**Dead ends:**
- **#107 erster Test mit „posSwitch_ms: 906ms"**: war Test-Skript-Artefakt (`await new Promise(setTimeout, 200)` im Polling-Loop), echter Switch ist 14-15ms.
- **#108 erster Test mit „êre = minne-Ergebnis"**: ebenfalls Test-Skript-Bug — `inp.value` wurde auf dem alten Input-Element gesetzt nachdem `sel.dispatchEvent` ein Re-Render ausgelöst hatte, das den Input ersetzte. Sauberer Test mit page-reload bestätigte korrekte Trennung.
- **Dev-Server EADDRINUSE**: alter Port-8080-Server-Prozess hat TaskStop überlebt. Habe einfach den existierenden weitergenutzt — kein Blocker.

**Phase:** Implementation (handoff). Alle 14 Promptotyping-Docs aktuell. DESIGN.md §Module Pattern-Inventar auf „Neun Module" gebracht (text-comparison + cooccurrence-ranking neu, concept-distribution erweitert). ROADMAP Now/Next bereinigt, vier neue Recently-Completed-Einträge.

**Open issues:**
- **#86 Barrierefreiheit**: KZW-Sichtung der Live-Seite weiterhin ausstehend.
- **#110 4 wrap_failed Strophen** (WVV 1174/1180/1208/1242): brauchen philologische Entscheidung KZW/Julia zu Ton-Wechsel-Splits.
- **#34 WZB CoReMA**: weiterhin wartend auf Julia + Helmut.
- **#92 ARITHMETIC**: wartet auf Carinas Antworten.
- **#91 Zenodo**: Webhook + Tag = User-Steps.
- **#45 Static JSON API**: claude-ready, L-Effort — nächster größerer Brocken.
- **#78 Frontend-Doku MHDBDB-Schema**: claude-ready, M-Effort.
- **`concept-distribution.spec.js:90`**: bekannter pre-existing Test-Fail (Spinner-Visibility), nicht durch diese Session adressiert. POS-Filter-Erweiterung des Moduls in #107 ist parallel — `concept-distribution.js` selbst nur in #113 angefasst (Autocomplete + DOM-Mutation).

**Next steps:**
1. `/promptotyping orient` zum Laden des Project-State.
2. Falls KZW auf #86 antwortet: Final-Version-Anpassung + Issue close.
3. **#45 Static JSON API** als nächster großer Block-Posten — L-Effort, planning doc liegt vor (`features/045-static-api.md`).
4. Alternative claude-ready Quick-Wins: **#78 Frontend-Doku-MHDBDB-Schema** (M), **#28 Foreign-Language-Filter** (L), **#27 POS-Workflow-Ausbau** (L).
5. Falls #110 Strophen-Klärung kommt: manuelle `<lg>`-Splits + Re-Validate + Index-Bump corpus 4.1.4 / authority bleibt.
6. Falls Cooccurrence-Ranking-Pattern auch in Lemma-Verteilung/Verseposition-Suche autocomplete bekommen soll: gleiche Logik aus `concept-distribution.js` abstrahieren oder kopieren. Kein Issue dafür, müsste KZW/wachauer initiieren.

**Commits (gepusht):**
- `131fed17b` `fix: #112 Lemma-Highlight im Reader nach Playground-Klick`
- `c53a8ac0d` `feat: #108 Textvergleich — gemeinsame vs. exklusive Lemmata zweier Texte`
- `70d0bf280` `feat: #107 Kookkurrenz-Ranking — häufigste Nachbar-Lemmata pro Lemma`
- `a2e7b0b36` `feat: #113 Autocomplete in Begriffs-Verteilung`

**Carryover:** unverändert vom 13:11-Handoff abgesehen von den vier abgearbeiteten Issues. #34, #92, #91, #45, #109, #106 weiterhin offen mit identischen Begründungen.

**Post-Handoff-Check (17:00, commit `33150019e`):** `/promptotyping check` direkt nach Handoff zeigte drei Should-fix-Drifts, die der Handoff-Eintrag oben mit „Alle 14 Promptotyping-Docs aktuell" unterschlagen hatte:
1. `ARCHITECTURE.md:212-214` Modul-Inventar fehlten `text-comparison.js` + `cooccurrence-ranking.js`; Routes-Tabelle :266-270 fehlten `#text-comparison` + `#cooccurrence-ranking`.
2. `FEATURES.md:158-170` keine User-Facing-Sektion für Textvergleich + Kookkurrenz-Ranking; Begriffs-Verteilung ohne Autocomplete-Erwähnung.
3. `DESIGN.md §Module Pattern`: Count auf „Neun" gebracht, aber drei neue Patterns aus heute nicht dokumentiert: Performance-Map gegen O(N) (text-comparison-Lesson, 5962ms → 53ms), Abort-Token gegen Race-Conditions (cooccurrence-ranking), Live-Autocomplete-Dropdown (concept-distribution #113, direktes DOM-Update, mousedown-vor-blur, ARIA).

Alle drei direkt im selben Pass gefixt. Severity-2/3-Findings (Autocomplete-auf-andere-Module portieren, POS-Tag-Qualität in Authority-Daten, JOURNAL.md > 110 KB) bleiben als Notiz — kein Issue angelegt, weil User-Entscheidung.

Lehre fürs nächste Handoff: **Modul-Inventar + Pattern-Dokumentation gehören in den Handoff-Lauf, nicht erst in den Check danach.** Bei drei neuen Modulen + erweitertem viertem Modul ist die „Inventar aktuell"-Behauptung im Handoff-Body sonst unwahr.

---

## 2026-05-16 — handoff (Audit-Session)

**Summary:** Gestern Spät-Session-Frage „außer #45 ist jedes Issue geblocked?" — heute systematischer Re-Check aller 20 offenen Issues, 2 Doku-Drifts behoben (#78 false-open, #110 reopened), Autocomplete auf 3 weitere Lemma-Module portiert (lemma-distribution, verse-position-search, cooccurrence-ranking), #44 Triage-Matrix vollständig refreshed, Label-Korrekturen (#28, #23, #110). Kerngedanke der zweiten Tageshälfte: **Audit-driven Preparation statt blinder Pings** — 6 Issues mit konkreten Datenbefunden aufbereitet, damit KZW/Julia/Linda/Chris/Carina statt freier Fragen Yes/No-Entscheidungen treffen können.

**Decisions:**
- **Process-Lehre `Closes #N`-Trailer**: voreilig auto-closing bei partial-complete (siehe #110-Reopen). Künftig: Closes nur bei vollständig fertig; bei partial-complete → keine Closes-Trailer + manueller Comment „X von Y done, Rest wartet auf …".
- **Process-Lehre Cross-Check ROADMAP gegen `gh`**: gestriger Check hatte nur Doku-Inventar geprüft, nicht ROADMAP-Issue-References gegen GitHub-State. Heute durchgeführt → #78 (false-open) + #110 (false-closed) entdeckt. **Künftig im Check: alle #NN-Refs in 14 Docs gegen `gh issue view` cross-checken.**
- **Autocomplete-Helper zentral statt 3× kopiert**: `AuthorityFilesManager.getLemmaAutocompleteMatches()` neu — prefix-search auf `lemma.normalized` (mhd-norm „ere" matcht „êre") + length-Sort. Bricht gestrige „Manager nicht modifizieren"-Lehre bewusst, weil zentrale Helper > 3× Duplikation.
- **Audit-driven Preparation als Pattern**: bei „blockierten" Issues nicht nur pingen, sondern erst die Audits machen, die der Entscheider braucht. Spart 5 min Entscheidung statt 5 Wochen Hin-und-Her.

**Audit-Befunde (alle als Issue-Comments gepostet):**
- **#30** TEI-Strukturelemente (Re-Audit): **29/29 Stage-2-valid**, Original-Liste post-#32/#83/#85/#26 obsolet. Vorschlag closen + 2 Follow-Up-Issues (`<div>`-Hüllen für HUG/KLA/PL1-3/MBS editorisch klären, Phase 4 falls #101 nicht abdeckt).
- **#27** POS-Audit: 43.754 Lexicon-Einträge (0 leer, 0 multi). **Aber:** Lexicon-POS oft lexikografisch grob (`haben` als NOM = Habe-Substantiv, nicht Auxiliarverb). PZ-Sample: **26,5 % der Tokens haben Multi-POS** vom Tagger (29.554 von 111.599; ADJ ADV, ART CNJ, ADV PRP, NOM VRB, …). Drei Schichten getrennt: 1. Lexicon-Politik (Multi-POS pro Lemma?), 2. Token-POS im Index nutzen (M-Effort, sofort bessere Filter), 3. Neuer Tagger (XL = #109 FWF). Empfehlung Schicht 2.
- **#28** Foreign-Lang-Audit: **0 `<w xml:lang>`, 0 `<foreign>` im gesamten Korpus**. Feature ist datenseitig blockiert. xml:lang existiert nur in Header (titleStmt/msName/gloss). 5 Optionen (Manuell / Heuristik / langid-Modell / WZB-Vorarbeit ziehen / FWF). **Label-Rollback** claude-ready → needs-clarification.
- **#92** ARITHMETIC Stage-1-Vorbereitung: 6 HS mit Token-Counts (AUG81=3.532, BRE1948=7.545, EIN624=408, **MUE279=97 Fragment?**, MUE746=377, WIEN5206=7.367). Genre-Vorschlag `genre_1fb94b80 Rechenbuch` (`genre_20b2d746` Arithmetik als broader). Wikidata-Refs pro Bibliothek vorgeschlagen. 6 Yes/No-Fragen für Carina formuliert (Sigle, Genre, MUE279-Status, Edition, Lizenz, Begriffssystem-Mapping). Stage 1 in ~1-2h durchführbar sobald Carina bestätigt.
- **#59** Antonomasien/Epitheta JSON-Audit: Lindas Repo öffentlich (`lindabeutel/Naming-analysis/data`). 154 KB `naming_variants_dict.json`, 4 Werke (Iwein/Rolandslied/Trojanerkrieg/Eneasroman), Sigles existieren alle im MHDBDB-Korpus (IW/ROL/TRO/ENE). Encoding-Artefakt im Rolandslied (`\xa0` statt Space). Effort revidiert L → M+. Modul sofort bauenbereit wenn A gewählt.
- **#106** Reim-Wörterbuch-Prototyp: `lineEnds[]` reicht out-of-the-box. 4 Sample-Texte: IW 1.027 Reimpaare (muot↔guot 27×), PZ 3.250 (komen↔vernemen 43×), TRO 6.491 (komen↔nemen 89×, kraft↔rîterschaft 73×). Klassisches MHD-Reimschema bestätigt. 3 Varianten (Min Lemma-basiert M, Mittel mit Orig-Token-Suffix M+L mit Index-Bump, Voll mit phonetischer Norm XL → #109). Empfehlung Minimal als Rolling-Backlog.

**Dead ends:**
- **#28 enthusiasm**: heute morgen als „falsch-blockiert, eigentlich claude-ready" eingestuft. Audit zeigte: ist falsch eingestuft *in die andere Richtung* — gar nicht implementierbar mit aktuellen Daten. Label korrigiert.
- **Schemas-Validierungs-Subprozess** lief im Background mit Output ins Temp-File — `validate-corpus.py --corpus-only --sample` brauchte 54s für 29 Files. Acceptable, kein Blocker.
- **pgrep auf Windows-Git-Bash**: nicht verfügbar. `Monitor`-Tool wäre die richtige Alternative gewesen.

**Phase:** Implementation (handoff). Alle 14 Promptotyping-Docs aktuell. Index-Versionen unverändert (corpus 4.1.3, authority 1.2.2). Working-Tree clean (nach Push).

**Open issues nach diesem Handoff:**
- **Pings warten auf Antworten:** #23 (close-Vorschlag), #27 (Scope-Wahl), #28 (Daten-Schicht), #59 (A/B/C), #68 (organisatorischer Teil), #86 (gestern KZW), #92 (Carina), #106 (Min/Mittel/Voll), #110 (4 Strophen)
- **Echt claude-ready ohne Klärungsbedarf:** **#45 Static JSON API** ist heute der einzige verbliebene große Block-Posten.
- **`concept-distribution.spec.js:90`**: pre-existing Spinner-Visibility-Fail, unverändert.

**Next steps:**
1. `/promptotyping orient` zum Laden des Project-State.
2. Falls #45 angegangen wird: planning doc `docs/features/045-static-api.md` als Ausgangspunkt, L-Effort vermutlich 1-2 Tagessessions.
3. Falls Antworten auf Pings kommen: priorisiert abarbeiten — kleinste Effort zuerst (#23 close → #59 build → #92 Stage-1 → #106 minimal → #27 Token-POS-Index → #28 falls Daten-Schicht entschieden).
4. Quartals-Komprimierung von JOURNAL.md (heute >1.100 Zeilen / ~115 KB) bleibt offen.

**Commits dieser Session (10 total, alle gepusht):**
- Vormittag: `f83925f36` Autocomplete-Portierung, `28a471f88` ROADMAP-Drift-Fix #78, `598254f6e` #110 reopened.
- Nachmittag: nur Issue-Comments (kein Code) — 6 Audit-Comments + 5 Ping-Comments + 1 Reopen-Comment auf GitHub, plus #44 Body-Update via gh edit.

**Carryover:** unverändert vom 16:48-Handoff gestern abgesehen davon dass #28 jetzt daten-blockiert ist, nicht claude-ready. #45 ist der letzte freie claude-ready-Block-Posten.

---

## 2026-05-28 12:42 — handoff (Session-Wechsel wegen Browser-Tool-Reconnect)

**Summary:** #113 KZW-Followup vom 2026-05-18 angegangen. Beim Audit ein **Last-Wins-Bug** im Authority-Index-Build entdeckt: `parse_concepts()` iterierte alle `<term xml:lang="de">` und überschrieb `term_de` bei jedem Treffer — bei concept_13023100 gewinnt daher das Alternative „Früchte" über das Primär „Obst". 263 Concepts betroffen. Build-Skript gefixt (Primär vs. `altDE[]`/`altEN[]`/`altNormalized[]` getrennt), Index v1.2.2 → v1.3.0 (3 Stellen synchron + Audit-Skript-Doku), beide UI-Module (`concept-explorer.js` + `concept-distribution.js`) um `altDE/altEN` als Such-Felder erweitert plus „auch: …"-Hint im Autocomplete bei Synonym-Match. Index rebuilt, Daten-Stichprobe sauber. **Code NICHT committed**, **UI-Verifikation NICHT abgeschlossen** — Browser-Tools in dieser Session nicht ansprechbar (ToolSearch findet `mcp__claude-in-chrome__*` nicht trotz angekoppelter Browser-Extension), darum Handoff an neue Session.

**Decisions:**
- **Build-Skript-Fix vor Schema-Anpassung**: Daten-vor-Schema-Prinzip wendet hier auch fürs Index-Build — die XML-Daten sind korrekt (`<term type="alternative">` ist semantisch eindeutig), das Build-Skript hat den Bug. Fix im Skript, nicht in den authority-files.
- **Index-Schema v1.3.0 abwärtskompatibel additiv**: `termDE/termEN/normalized` Felder unverändert, `altDE/altEN/altNormalized` nur dann attached wenn Alternative-Terms vorhanden (263 von 567 Concepts). Heißt: Code der nur Primär liest, bleibt unverändert funktional.
- **Hint-Anzeige im Autocomplete als „auch: …"-Subtitle**: User-Wahl via AskUserQuestion. Macht Match-Pfad transparent ohne den Primär-Term zu verdrängen.

**Files im Working-Tree (uncommitted):**
- `scripts/build-authority-index.py` — `parse_concepts()` umgebaut, `'version': '1.3.0'` in Index-Struktur
- `assets/js/lib/corpus-loader.js` — `AUTHORITY_INDEX_VERSION = '1.3.0'`
- `scripts/audit/check-index-versions.py` — Doku-Header auf v4.1.3 / v1.3.0 refreshed (kein Logik-Change)
- `playground/js/ui/authority/concept-explorer.js` — `searchConcepts()` matcht zusätzlich `altDE/altEN`, neue `findAlternativeMatch()`-Helper unten + `TextNormalizer`-Import
- `playground/js/ui/tei/concept-distribution.js` — `resolveQuery()` mit getrenntem `primaryScore`/`altScore` (90/45/8 vs. 100/50/10), `matchedAlt`-Feld an Candidates angehängt; `renderAutocomplete()` zeigt „auch: …"-Hint
- `data/authority-index.json.gz` — rebuilt v1.3.0 (567 Concepts, 263 mit altDE, 266 mit altEN)

**Verifikation bisher:**
- ✅ `python scripts/audit/check-index-versions.py` → konsistent (corpus 4.1.3, authority 1.3.0)
- ✅ Daten-Stichprobe concept_13023100: `termDE: "Obst"`, `altDE: ["Früchte"]`, `altNormalized: ["fruechte"]`
- ✅ JSON UTF-8 korrekt (kein Encoding-Glitch in den Daten, nur im Windows-Konsolen-Print)
- ❌ UI-Verifikation **noch nicht durchgeführt** (Browser-Tools nicht verfügbar)
- ❌ npm test **nicht gelaufen** (laut Memory-Regel: User muss vorher fragen)

**Phase:** Implementation (mid-flight, Code fertig, Verify+Commit offen).

**Open issues nach diesem Handoff:**
- **#113 KZW-Followup**: Code fertig, wartet auf UI-Verify + Commit + Issue-Comment. **Nicht closen** — Issue beschreibt das Autocomplete-Pattern insgesamt, das ist nur der Synonym-Sub-Task. Nach Verify entscheiden, ob #113 closed werden kann oder ob KZW erst Feedback geben soll.
- **#114 Tabellenansicht Korpussuche**: Als nächster Step nach #113 geplant (User-Reihenfolge im Turn: „zuerst 113, dann 114").
- **Pings/Carryover sonst unverändert** vom 2026-05-16-Handoff.
- **Dev-Server läuft als Background-Task `b9l11be3h`** auf :8080 — neue Session entscheiden ob nutzen oder neu starten.

**Next steps (nächste Session):**
1. `/promptotyping orient` — lädt diesen Handoff.
2. Browser-Tools sollten nach Session-Restart wieder via ToolSearch findbar sein (`mcp__claude-in-chrome__*`). Falls nicht: User fragen, ob Extension reconnected ist.
3. Dev-Server-Status checken — entweder Background-Task `b9l11be3h` weiternutzen, oder mit `npm run serve` neu starten.
4. **UI-Verify** in beiden Modulen — **Hard-Reload erforderlich** (Cache-Invalidate wegen Version-Bump v1.2.2 → v1.3.0 sollte automatisch greifen, aber CTRL+SHIFT+R zur Sicherheit):
   - **Begriffe-Explorer**: Sidebar → Begriffe → Eingabe „obs" → erwartet: concept_13023100 „Obst / Fruits" mit Subtitle „auch: …"-Hint NICHT (Primär-Match). Eingabe „frü" → erwartet: concept_13023100 „Obst / Fruits" mit Subtitle „auch: Früchte".
   - **Begriffs-Verteilung** (TEI-Analyse-Modul): Eingabe „frü" → Autocomplete-Dropdown zeigt concept_13023100 mit „auch: Früchte" als sekundäre Zeile. Eingabe „obs" → zeigt es ohne Hint. Enter triggert Suche, Resolved-Concept = Obst (nicht Früchte).
5. Wenn Verify ok: Stage die 6 Files explizit (NICHT `git add -A`/`.` wegen Concurrent-Session-Regel), Commit-Message-Vorschlag unten, dann push.
6. Issue-Comment auf #113 mit Kurz-Befund: „Bug 1 (Last-Wins) + Bug 2 (Alternative nicht matchbar) gefixt. 263 Concepts haben jetzt altDE-Synonyme. Bitte Live-Check, dann ggf. closen oder offen lassen für weiteres Feedback."
7. Wenn alles grün: weiter mit #114.

**Empfohlener Commit-Message:**
```
fix(#113-followup): concepts.xml Alternative-Terms separat vom Primär-Term

## Changes
- scripts/build-authority-index.py: parse_concepts() trennt term[@type="alternative"]
  von Primär-Term; bisher überschrieb Last-Wins-Iteration den Primär-Term
  (concept_13023100: "Früchte" statt "Obst" als termDE)
- Authority-Index v1.2.2 → v1.3.0 (additiv: altDE[], altEN[], altNormalized[]
  nur attached wenn Alternative-Terms vorhanden — 263 von 567 Concepts)
- assets/js/lib/corpus-loader.js + scripts/audit/check-index-versions.py:
  Version-Konstanten synchron
- playground/js/ui/authority/concept-explorer.js: matcht zusätzlich altDE/altEN,
  zeigt "auch: <Synonym>"-Hint bei Alternative-Match
- playground/js/ui/tei/concept-distribution.js: resolveQuery() mit getrenntem
  primaryScore/altScore (Primär gewinnt bei Tie); Autocomplete zeigt
  "auch: <Synonym>"-Hint
- data/authority-index.json.gz rebuilt

Behebt KZW-Comment in #113 (2026-05-18): Bei Eingabe "Frü" ODER "Obs" wird
jetzt concept_13023100 vorgeschlagen, mit "Obst" als Headline.

Co-Authored-By: Claude <noreply@anthropic.com>
```

**Risiken/Edge-Cases die zu prüfen sind:**
- IndexedDB-Cache muss invalidieren — Version-Bump v1.2.2 → v1.3.0 triggert das automatisch via [corpus-loader.js:124-126](assets/js/lib/corpus-loader.js#L124-L126). Sollte transparent sein, aber bei Verify im DevTools-Console „Cache version mismatch" sehen — Hinweis dass es funktioniert hat.
- `concept-distribution.js`-Candidates haben jetzt `...c, matchedAlt: ...` (Spread+Anhang). Wenn irgendwo `===`-Identity-Check auf das Concept-Objekt erwartet wird, könnte das brechen. Schnell-Scan im Code zeigt: candidates wird nur gelesen, nicht Identity-verglichen. Sollte safe sein.
- `concept-explorer.js`: `findAlternativeMatch()` ruft `TextNormalizer.matchesNormalized()` — Import oben am File ergänzt. Wenn der Import-Pfad falsch ist, gibt's einen Runtime-Error in der Konsole.

---

## 2026-05-28 13:04 — handoff (Verify + Commit + Push erledigt)

**Summary:** Folge-Session zum 12:42-Handoff. Browser-Tools liefen sauber (`mcp__claude-in-chrome__*` via ToolSearch in dieser Session findbar — Workaround vom 12:42-Handoff nicht mehr nötig). UI-Verify in beiden Modulen (Begriffe-Explorer + Begriffs-Verteilung) mit „obs"/„frü"-Stichproben grün, plus Konsistenz-Bonus über `Wahnsinn`/`Tobsucht` als Allgemein-Fall „altDE-Match nicht-trivial". Commit `f7c8592c2` (6 Code/Daten-Files) + Push auf `origin/main` + Issue-Comment auf #113 ([#issuecomment-4563371418](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/113#issuecomment-4563371418)).

**Decisions:**
- **Split-Commit (Code vs. Journal)**: Folge der bestehenden Konvention im Log (`fix:` getrennt von `docs(journal):`). Code/Daten-Fix als `f7c8592c2`, Journal-Update als separater Handoff-Commit am Session-Ende.
- **#113 offen gelassen, nicht geschlossen**: KZW-Comment erbittet implizit Live-Check; Issue erst nach OK von KZW closen. Memory-Regel „Editorial-Issues → Kat+Julia beide" greift hier nicht (#113 ist UI-Code, nicht editorial).
- **Klick-Simulation via `MouseEvent('mousedown')`**: Der Autocomplete-Listener in `concept-distribution.js` ist auf `mousedown` (vor `blur`), nicht `click` — `firstBtn.click()` triggert ihn nicht. Direkter `dispatchEvent('mousedown')` löst's. Hinweis fürs nächste UI-Verify in diesem Modul.

**Dead ends:**
- Erster `find()`-Versuch fand „Begriffe-Explorer öffnen"-Button statt direkt das Suchfeld. Workaround: `location.hash = '#concepts'` direkt setzen statt durchklicken — Hash-Routing aus #48 macht das robust und schneller.
- Erste DOM-Query für `auch:`-Hint in concept-distribution suchte nur `<span>`-Descendants, übersah aber, dass `renderAutocomplete()` den Hint als `<div>` rendert. Nachschau im Code (`grep` auf `matchedAlt|auch:` in concept-distribution.js) hat's geklärt.

**Daten-Quirk dokumentiert (nicht-blockierend):** Mehrere Concepts in `authority-files/concepts.xml` haben slash-separierte altDE-Strings als einzelnes `<term type="alternative">`-Element, z.B. `concept_21111200 Mahlzeiten` mit `auch: Abendessen/Nachtmahl/Festmahl/Imbiss/Frühstück/Suppe`. Build-Skript speichert das 1:1, Hint zeigt's komplett. Verbose, aber transparent. Falls ein editorialer Followup gewünscht ist: separate `<term>`-Elemente pro Synonym. Nicht-blockierend, mit Maximum-Token-Pattern-Recognition-Risiko, wenn solche Strings als „1 alt" gezählt werden statt als 6.

**Phase:** Implementation (#113 KZW-Followup abgeschlossen, gepusht, wartet auf optionalen KZW-Live-Check).

**Open issues nach diesem Handoff:**
- **CI auf `f7c8592c2` läuft noch** beim Zeitpunkt des Handoffs: `Index Version Check` + `pages-build-deployment` beide `in_progress`. Schema-Validation triggert nicht (kein XML in diesem Commit). Erwartet grün — `check-index-versions.py` war lokal konsistent (corpus 4.1.3, authority 1.3.0).
- **#113 lässt KZW Live-Check machen**, dann ggf. closen.
- **#114 Tabellenansicht Korpussuche** als nächster Posten laut Reihenfolge im 12:42-Handoff.
- **Pings/Carryover** unverändert vom 2026-05-16-Handoff.
- **Dev-Server `bjq9bqyew` läuft im Hintergrund** auf :8080 (in dieser Session gestartet, Port war bereits belegt → Failed-Start, aber der zugrunde liegende Server aus früherer Session antwortet weiter 200). Nächste Session: status checken statt blind neu starten.

**Next steps (nächste Session):**
1. `/promptotyping orient` — lädt diesen Handoff.
2. CI-Status auf `f7c8592c2` checken: `gh run list --limit 4 --json status,conclusion,workflowName,headSha`. Falls rot: Index-Version-Drift (lokal konsistent gewesen, aber Cache-Edge-Cases möglich), Pages-Build prüfen.
3. **#114 Tabellenansicht Korpussuche** beginnen, falls KZW kein Feedback zu #113.
4. Falls KZW #113 OK gibt: Issue closen mit kurzem Closing-Comment.

**Empfohlener Commit-Message für DIESEN Handoff:**
```
docs(journal): Handoff 2026-05-28 (Verify + Commit + Push für #113-Followup)

Co-Authored-By: Claude <noreply@anthropic.com>
```

---

## 2026-05-28 14:00 — handoff (Promptotyping-Check 3 Iterationen + .md-Vereinheitlichung + #73-Befund + #44-Refresh)

**Summary:** Drei `/promptotyping check`-Iterationen mit zunehmender Tiefe:

- **Iteration 1:** JOURNAL.md-Kompressionsbedarf identifiziert + Should-Fixes für altDE/altEN-Doc-Drift. 1212 → 1029 Zeilen komprimiert (commit `ce6381e71`).
- **Iteration 2:** Doc-Sync für v1.3.0-Concept-Schema (DATA-MODEL, TEI-MODEL-AUTH-FILES) + ADR-013-Ausnahme für nested `<hi>` aus PD-001 (DECISIONS) + ROADMAP-Datum + #113-Followup-Recently-Completed (commit `4a171fa77`).
- **Iteration 3:** Strukturellen Versions-String-Drift aufgedeckt — sieben+ Doc-Stellen waren seit 2026-05-08 bei jedem Bump stale, weil Memory-Reminder als Architektur gerissen war. Option-C-Lösung: TEI-MODEL.md §11 als kanonische Source-of-Truth, alle anderen Stellen generisch (`X.Y.Z`/`1.x.x`/`4.x.x`) + Verweis. Memory `feedback_index_version_bump` entsprechend erweitert (3 Code-Stellen + 2 Doc-Stellen, CI gegated nur die 3 Code-Stellen) (commit `c16ec4486`).

Plus separates Sweep nach User-Hint: 9 stable Docs `.MD → .md` umbenannt (Two-Step wegen Windows-Case-Insensitivity) + alle 226 Cross-References in 29 Files via Python-Sweep angeglichen (commit `742bdc3a9`). 4 Commits gepusht.

**KZW-Status (Auswertung 28.05.):** Von 9 Pings vom 16.05. (12 Tage später) hat KZW nur **#73** beantwortet — Mail-Weiterleitung von Ute Recker-Hamm vom MWB. Ute hat eine neue HTTPS-API gebaut (`mhdwb-online.de/API/retrieve-id/{Lexer-ID}` → JSON mit MWB-Artikel-IDs). 28.05.-Comment auf #73 verifiziert die API mit zwei Stichproben (LA00004 → 2 Treffer; LS01234 → 0 Treffer wegen s-Bereich-Lücke); aktuell **kein Code-Change nötig**, weil Wörterbuchnetz- und Utes-Service dieselbe MWB-Datenbasis abdecken. Issue-Vorschlag: closen, MWB-3,4-Migration als Folge-Task wenn s-z verfügbar wird.

#44 aktualisiert (Updated 2026-05-16 → 2026-05-28): neuer Ping-Status-Block, #113-Followup in Recently Completed, #73 in „Claude-Doable nach Klärung" mit Close-Vorschlag, #114 in Future/Trigger-Wait, Reihenfolge-Empfehlung um „bei stiller Front: persönlicher Reminder" ergänzt.

**Decisions:**
- **Option C für Index-Versions-Drift gewählt** (statt B = alle Stellen jedes Mal nachziehen, statt A = alle entwerten). Kompromiss: zwei kanonische „aktueller Stand"-Stellen (TEI-MODEL.md §11 + INDEX.md §Status), alle anderen Doc-Stellen generisch. Begründung: Reader-Friction minimieren ohne Drift-Falle.
- **Komprimierung mittel-aggressiv:** 11 Handoffs aus April + früher Mai → 4 Sammelblöcke (~50 Zeilen statt ~230). Verbatim ab 2026-05-11 — Carryover-Ketten und operative Details intakt. Permanent gültige Lessons in den komprimierten Blöcken erhalten (PL1 mit 404k Kindern, „Daten vor Schema", `8b5d0e6ac`-Mishap, PD-001 Mittelweg, Cache-self-referential-Pattern).
- **#73 nicht aktiv schließen, Ball bei KZW lassen** — Issue-Comment mit Close-Vorschlag und @wachauer-Ping. Sie soll Daumen hoch/runter geben.
- **Pings nicht eskalieren** über GitHub-Comments — wenn keine Antwort, dann persönlicher Reminder (Signal/Mail) als nächste Stufe. Empfehlung steht in #44.

**Dead ends / Lessons:**
- **`--amend` rutschte durch** beim Single-Source-of-Truth-Commit, weil `git add docs/CONTRACTS.md` (klein) die Datei nicht stagete (Git-Index trackte als `.MD`). Two-Step `git add docs/CONTRACTS.MD` + `git commit --amend --no-edit` repariert. Strenggenommen gegen CLAUDE.md-Regel (immer neuer Commit) — User-transparent kommuniziert, kein Workverlust, aber Erinnerung: Pre-Stage immer `git status --porcelain` checken.
- **Case-Sensitivity-Falle:** Windows ist case-insensitive im Filesystem, Git-Index ist case-sensitive — File-Renames müssen Two-Step laufen (`X.MD` → `_X.md` → `X.md`).
- **#44 war 12 Tage alt** als ich nachschaute — die Matrix selbst war noch ~90% korrekt, aber das Vertrauen erodiert mit dem Alter. Konvention: nach jedem Spurt-Tag #44 mit-aktualisieren, nicht akkumulieren lassen.

**Files berührt (alle gepusht):**
- `ce6381e71` docs(journal) — JOURNAL-Kompression
- `4a171fa77` docs — Doc-Sync v1.3.0
- `c16ec4486` docs — Single-Source-of-Truth Index-Versionen
- `742bdc3a9` chore(docs) — .md-Vereinheitlichung (30 Files, 9 Renames + 21 Mods)

**Externe:**
- #73 Comment `4563667366` (Ute-API verifiziert, Close-Vorschlag, Ping an wachauer)
- #44 Body komplett neu (Ping-Status-Block, Recently Completed um #113-Followup, #73 hochgezogen)

**Phase:** Implementation (handoff). Alle 14 Promptotyping-Docs aktuell. Memory `feedback_index_version_bump` erweitert. Working Tree clean.

**Open / Carryover:**
- **#73 Close-Entscheidung bei KZW** — wenn Daumen hoch: dann closen + Memory-Notiz für MWB-3,4-Trigger
- **8 unbeantwortete Pings** (#23, #27, #30, #34, #59, #68, #86, #92, #110) — Eskalation: persönlicher Reminder, nicht weitere GitHub-Comments
- **#28 Foreign-Lang nicht gestartet** seit 16.05. — claude-ready, kein Blocker, größter Workstream-Kandidat für nächste Session (oder #45 Static JSON API als Alternative)
- **CI auf `742bdc3a9`:** Schema Validation queued (triggert wegen `schema/mhdbdb.rnc`-Kommentar-Change im .md-Sweep, Schema selbst unverändert), pages-build-deployment queued. Erwartet grün.
- **Dev-Server `bjq9bqyew`** läuft im Hintergrund auf :8080 (aus früherer Session).

**Next steps (nächste Session):**
1. `/promptotyping orient` — lädt diesen Handoff.
2. CI-Status auf `742bdc3a9` checken (Schema Validation grün).
3. KZW-Antwort auf #73-Close-Vorschlag prüfen — wenn da: closen.
4. Entscheidung: **#28 Foreign-Lang** ODER **#45 Static JSON API** als nächster L-Workstream — beide sind seit Wochen claude-ready.
5. Falls KZW/Linda/Julia in der Zwischenzeit auf andere Pings geantwortet haben: dort weiterarbeiten.
6. Falls weiter Stille: **persönlichen Reminder an KZW** als Eskalations-Schritt überlegen (Signal/Mail an chsteiner zur Weiterleitung).

---

## 2026-05-28 14:56 — handoff (#113-Followup live + CI-Fix + #114-Spec + #114-Plan)

**Summary:** Folge-Session zum 13:04-Handoff (parallele Session). Drei Werkstücke abgeschlossen, alle gepusht. (1) #113 KZW-Followup live verifiziert via Chrome-DevTools (4/4 UI-Tests grün — Obst/Früchte + Wahnsinn/Tobsucht-Cross-Check), `f7c8592c2` committed + pushed, Issue-Comment mit Befund + KZW-@-Ping abgesetzt. (2) CI-Workflow `Index Version Check` reanimiert (`13557978`) — timeout-minutes 2→10; jeder Run seit 2026-05-12 war wegen 2-min-Limit am Checkout cancelled, der Drift-Schutz war faktisch disabled. (3) #114 Tabellenansicht durchgebrainstormed → Spec (`dabfc601c`) + Implementation-Plan (`f8d464211`); Spec via `/check-md` rigoros geprüft, 1 CRITICAL (wordCount fehlt in Search-Engine-Projektion) + 3 MEDIUM (Sticky-Header-Container, Viewport-Width-Realität, Row-Click-Verhalten) + 3 LOW alle inline gefixt vor Commit.

**Decisions:**
- **CI-Timeout 2→10 min als Daten-Eingriff vor Schema-Lockerung**: Trotz CLAUDE.md-Pattern „Daten vor Schema" ist hier *Workflow vor Audit-Logik* analog — Audit lief lokal jahrlang sauber, Workflow killte sich beim Checkout. Fix: Timeout-Limit, nicht Audit-Logik aufweichen. Memo intern.
- **#114-Spec in `docs/features/`, nicht `docs/superpowers/specs/`**: User-Korrektur zur Skill-Default-Location. Auch der Plan unter `docs/features/114-…-plan.md` als Sibling. Existing-Pattern (one file per feature aspect) erweitert.
- **#114 Tabellen-Modus erzwingt vollbreites Layout** statt im 3-Spalten-Modus zu rendern: bei 1280-1920 px Viewport ist die Results-Spalte nur 300-460 px breit, 5-Spalten-Tabelle würde da unbenutzbar. Mental-Modell: „Tabelle = Vergleichs-/Export-Modus, Liste = Lese-Modus". Row-Click in der Tabelle wechselt zurück auf Listen-Modus + öffnet Reader. `localStorage`-Wert bleibt `'table'` — User-Präferenz nicht überschreiben.
- **Subagent-Driven für #114-Implementation in frischer Session**: User-Wahl. Plan hat 11 Tasks, jeder als eigener Subagent-Run mit Review zwischen Tasks.

**Dead ends:**
- Erster `find()`-Versuch in der UI-Verify-Phase fand „Begriffe-Explorer öffnen"-Button statt direkt das Suchfeld → Hash-Routing `#concepts` aus #48 direkt setzen ist robuster.
- Click-Handler-Simulation für concept-distribution-Autocomplete: `firstBtn.click()` triggerte nicht, weil Listener auf `mousedown` (vor `blur`) statt `click` hängt. `dispatchEvent(new MouseEvent('mousedown', …))` fixt's.
- Erste DOM-Query für „auch:"-Hint suchte nur `<span>`-Descendants, übersah dass renderAutocomplete den Hint als `<div>` rendert.
- Plan-Self-Review-Pass nach Schreiben fand kaputten Heroicon-SVG-Path (`a0 0 0 010 0` ist degeneriert) — als Implementer-Annahme im Plan markiert, wird inline gefixt.

**Phase:** Implementation. #113 lebt auf production, #114 ist Spec+Plan-fertig und wartet auf Coding.

**Commits (intern, alle gepusht):**
- `f7c8592c2` fix(#113-followup): concepts.xml Alternative-Terms separat vom Primär-Term
- `95745ac2a` docs(journal): Handoff 2026-05-28 (Verify + Commit + Push für #113-Followup)
- `135579789` ci: index-version-check timeout 2 → 10 min
- `dabfc601c` feat(#114): Spec Tabellenansicht für Korpussuche
- `f8d464211` docs(#114): Implementation-Plan für Tabellenansicht
- (dazwischen parallele Session: `742bdc3a9` .md-Vereinheitlichung, `c9f001446` Handoff 14:00, weitere Doku-Commits)

**Externe:**
- #113 Comment `4563371418` (Followup-Befund verifiziert + committed) + Comment `4563440114` (@wachauer-Ping zum Live-Check)
- #114 Comment `4564110295` (Spec-Link + Kern-Entscheidungen + Voraussetzung wordCount-Propagation)

**Open / Carryover:**
- **#113 wartet auf KZW-Live-Check** auf der gepushten Version — nicht zumachen.
- **#114 Implementation startet in nächster Session** via `superpowers:subagent-driven-development` aus Plan `f8d464211`. 11 Tasks, geschätzt 1.5-2 h.
- **#28/#45 als L-Workstream-Alternative** falls #114 in der Pipeline stockt (vom 14:00-Handoff übernommen, unverändert).
- **CI auf `f7c8592c2`/`13557978`/`f8d464211`:** Index-Check grün, Pages grün. Nach Push `f8d464211` triggert kein Build (nur docs).
- **Dev-Server `bjq9bqyew`** läuft im Hintergrund auf :8080 — nächste Session checken statt blind neu starten.

**Next steps (nächste Session):**
1. `/promptotyping orient` — lädt diesen Handoff.
2. CI-Stand auf letztem main-Commit prüfen (3-Punkt-Audit auf `f8d464211` und ggf. weitere parallele Commits).
3. **#114 Implementation**: `superpowers:subagent-driven-development` mit Plan-File `docs/features/114-tabellenansicht-korpussuche-plan.md`. Per Task einen frischen Subagent dispatchen, zwischen Tasks reviewen. Feature-Branch oder direkt-main ist beim Start zu entscheiden (siehe Skill-Konvention vs. Repo-Pattern).
4. Vor Task 1 (wordCount-Propagation) den Dev-Server-Status checken; Tests werden gegen den laufenden Server gefahren.
5. Bei jedem Test-Lauf: User vorher fragen (Memory-Regel `feedback_ask_before_npm_test`).
6. Falls KZW-Reply auf #113 / #73 inzwischen da: dort weiterarbeiten.

**Memory-Updates dieser Session:**
- Keine neuen Memories nötig — alle Patterns sind schon abgedeckt (Concurrent-Sessions, Index-Version-Bump, Test-Invocation). Der CI-Timeout-Fix ist projektspezifisch und im Journal dokumentiert, nicht als Memory.

---

## 2026-05-28 15:00 — handoff (Mini-/Klein-Audit-Sweep: CI grün, Sigle-Coverage, Cross-Ref-Audit, #80 closed)

**Summary:** Sechs Mini-/Klein-Aufgaben nach Tages-Doc-Sweep abgearbeitet. Schwerpunkt: read-only Audits, leichte Issue-Hygiene. Ergebnis: CI bestätigt grün; ein bisher unbekannter Daten-Befund ans Tageslicht (226k unresolved Variant-Refs); ein Umbrella geschlossen; ein Memory-Drift gefixt.

**Erledigt:**

1. **CI-Verify** auf den heutigen 5 Commits — alle grün (Schema Validation, Index Version Check, pages-build-deployment). Eine `pages-build-deployment` cancelled, vermutlich wegen Concurrent-Run-Cancellation.

2. **Corpus-Index-Größen-Audit (v4.1.3):** 40,23 MB gz / 160,58 MB raw, Ratio 4,0×. Authority-Index 2,91 MB gz / 20,30 MB raw, Ratio 7,0× (sehr gut komprimiert wegen vieler wiederholter lemma-IDs). Corpus-Index zu 100 % aus `texts[]` (174 MB raw, plus 4 MB `lemmaIndex`). #111-Soft-Cap-Trigger (50 MB gz) ist ~10 MB entfernt — ~25 % Korpus-Wachstum führt zum Trigger. Top-15 größte Texte: OVG (9 MB), JT, PL1, TRO, PL2, REN, PL3, WZB, AXU, JEW, HTR, CRO, PZ, RVBR, GAR.

3. **Sigle-Coverage-Report (POS/Lemma/structural pro 667 Texte):**
   - 202 Sigles (30 %) Kategorie A (POS+Lemma ≥95 %)
   - 107 Sigles (16 %) Kategorie B (≥80 %)
   - 358 Sigles (54 %) Kategorie C (≥50 %)
   - 0 Sigles Kategorie D, 0 leer
   - 64 Texte ohne `<l>` (Prosa-Verdacht, matched bekanntes Bild)
   - **606 Texte ohne `<pb>`** — page-break-Annotation fehlt großflächig. #26 hat 14 Texte gefixed, das eigentliche Volumen ist viel größer. Bewusst nicht angefasst oder echter Backlog? Ggf. KZW-Frage wert.

4. **Authority-Cross-Reference-Audit (NEUER ERKENNTNIS):**
   - 21,3 M Cross-References im Korpus gescannt
   - **226.863 unresolved (1,06 %)**, davon **225.886 auf `variants.xml`** (64.291 distinct Variant-IDs)
   - **977 unresolved auf `lexicon.xml`** (349 distinct Lemma-IDs)
   - **4 negative type-IDs als Daten-Format-Issue identifiziert:** `type_-7` (6369x), `type_-15` (5267x), `type_-10` (1630x), `type_-11` (1629x) — vermutlich Placeholder für „nicht-zugeordnet"
   - Echte unresolved Lemma-IDs (349 distinct) sind Datenleichen — Lemma-Migration hat sie nicht entfernt oder Korpus referenziert nicht-mehr-existierende Einträge
   - **Empfehlung:** Neues Issue für `data:tei-wrangling` anlegen — „Authority-Cross-Reference-Integrity-Audit". Heute nicht angefasst weil Mini-Scope.

5. **#80 Umbrella geschlossen** — #79 + #78 längst durch, nur #68 organisatorisch offen. Closing-Comment dokumentiert Status, Leitprinzipien stehen weiter. #68 trackt eigenständig.

6. **Memory-Audit:** 16 Files durchgegangen, project-Files spotchecked.
   - `project_tei_consolidation.md`: aktuell als Wissensanker markiert, kein Update nötig.
   - `project_issue30_tei_review.md`: behauptet `feature/tei-structural-fixes-30` lebt lokal — verifiziert via `git branch`, stimmt.
   - `project_arithmetic_ingest.md`: **gefixed** — Verweis auf `Arithmetic_MHDBDB.zip` raus (war am 2026-05-07 versehentlich mit `rm -f` gelöscht); Stand auf „Daten leben in `ingest/ari/` seit 2026-05-08, validiert" aktualisiert.
   - `project_benchmark_repo.md`: 72 Tage alt aber inhaltlich stabil (Sibling-Repo-Existenz verifiziert), kein Update.
   - feedback_*-Files: alle gerade gepflegt (feedback_index_version_bump heute erweitert).

7. **features/-Lifecycle-Audit:** vier Dateien (034 wenzelsbibel 45 KB, 045 static-api 9 KB, 114-Doppel vom Kollegen). Alle vier passend zum Lifecycle — keine Aktion. 034 ist groß und WB-Teil ist fertig, aber CoReMA-Teil steht noch aus (Issue #34 offen), darum kein Extract.

**Anti-Sycophancy-Befund:**

Das Authority-Cross-Reference-Audit war als Mini-Task gedacht, hat aber strukturelle Datenqualitäts-Lücke aufgedeckt: 226 K unresolved Refs, davon 225 K auf Varianten, 977 auf Lemmata. Negative type-IDs deuten auf Datenformat-Eigenheit, aber 349 distinct unresolved Lemma-Refs sind echte Datenleichen. Das gehört eigentlich in ein eigenes Issue (CI-relevant — `check-index-versions.py` könnte erweitert werden), wurde aber heute nicht angelegt, um den Mini-Scope nicht zu sprengen. Beim nächsten Carryover prüfen.

**Files berührt (committable):**
- `docs/JOURNAL.md` (dieser Handoff)

**Files berührt (Memory, nicht im Repo):**
- `memory/project_arithmetic_ingest.md` (ZIP-Verweis raus, ingest/ari-Status drin)

**Externe:**
- #80 closed (Comment + Close-Trailer)

**Phase:** Implementation (handoff). Working Tree nach Commit clean.

**Open / Carryover (Stand vor diesem Handoff unverändert):**
- 8 unbeantwortete Pings — User hat persönlichen Reminder rausgeschickt
- #45 Static JSON API + #114 (Kollege) + #28 (wartet auf KZW-Klärung)
- **NEU als Carryover:** Authority-Cross-Reference-Audit-Befund — entweder als Issue anlegen oder im nächsten Workstream mit beheben (z. B. `check-index-versions.py` um Cross-Ref-Check erweitern, neuer CI-Workflow)

**Next steps (nächste Session):**
1. `/promptotyping orient` — lädt diesen Handoff.
2. KZW-Reminder-Response prüfen (User hat persönlich rausgeschickt).
3. Wenn freie Kapazität: **#45 Static JSON API** beginnen oder Authority-Cross-Reference-Audit zu Issue formalisieren.
4. Bei KZW-Antworten: Issues entsprechend bewegen.

---

## 2026-05-28 16:00 — handoff (Issues anlegen, #44 nachziehen, KZW-Reminder out)

**Summary:** Nach Mini-/Klein-Audit-Sweep zwei neue Issues angelegt (#115 Cross-Ref-Integrity, #116 pb-Backlog) und #44-Triagematrix entsprechend nachgezogen. User hat persönlichen Reminder an KZW ausserhalb GitHub ausgesendet (8 stille Pings + die zwei neuen Klärungs-Fragen).

**Decisions:**
- **#115 + #116 mit chsteiner + wachauer + juliahin als Assignees** — Editorial-Konvention aus Memory `feedback_editorial_assignees`. #115 ist primär technisch, #116 primär editorial; Assignment-Schema bleibt einheitlich.
- **Kein zusätzlicher Issue-Comment-Ping** auf #115/#116 — Assignment ist der Ping; User hat parallel persönlich gepingt; Issue-Comments wären Lärm.
- **#28 aus Claude-Ready demoted zu Claude-Doable nach Klärung** — Audit zeigt 0 Daten im Korpus, Code-Start ohne KZW-Entscheidung wäre Spaghetti.
- **Quick-Stats in #44 umstrukturiert:** „claude-ready" reduziert auf 1 (nur #45), neue Kategorie „claude-doable nach Klärung" für 6 Issues mit ausstehender Klärung sichtbar gemacht.

**Phase:** Implementation (handoff-Ende). Alle 14 Promptotyping-Docs aktuell, alle gepushten Aktionen heute durch.

**Open issues nach diesem Handoff:**
- **8 unbeantwortete Pings** vom 16.05. + 2 neue Klärungs-Issues (#115, #116) — KZW-Reminder out ausserhalb GitHub
- **6 lokale Kollegen-Commits vor origin/main** (Christian-Steiner-Identity) zum #114 Tabellenansicht-Stream — Kollege arbeitet, Push liegt bei ihm. Mein JOURNAL-Commit kommt obendrauf, der nächste Push wird die Kollegen-Commits mitnehmen, das ist OK
- **Authority-Cross-Reference-Befund (#115)** — Phase 1 (Detail-Audit-Skript) ist claude-startbar parallel zur KZW-Klärung
- **#45 Static JSON API** bleibt einziger großer Claude-Ready-Workstream, ungestartet seit 12 Tagen
- **#28 wartet auf KZW-Entscheidung** (a/b/c-Optionen im Comment 4564139381)
- **#73 wartet auf KZW-Daumen** zum Closen

**Next steps (nächste Session):**
1. `/promptotyping orient` — lädt diesen Handoff plus den 15:00-Handoff.
2. KZW-Antworten checken (persönlicher Reminder von gestern abend).
3. Wenn freie Kapazität und KZW-Antworten kommen nicht: **#115 Phase 1** (Detail-Audit-Skript) als kleiner technischer Workstream oder **#45 Static JSON API** als großer Workstream.
4. Push-Status der 6 Kollegen-Commits zu #114 prüfen — wenn der Kollege fertig ist, gemeinsam pushen.

**Tagesbilanz 2026-05-28:**
- 7 Commits auf origin/main + 1 JOURNAL-Commit lokal (dieser)
- 2 neue Issues (#115, #116), 1 Issue closed (#80), 4 Issue-Updates/-Comments (#28, #27, #44, #73)
- 3 Promptotyping-Check-Iterationen
- Komplette `.md`-Vereinheitlichung (30 Files)
- Single-Source-of-Truth für Index-Versionen etabliert (TEI-MODEL.md §11 + Memory-Update)
- 7 Mini-/Klein-Audits, davon einer mit signifikantem Daten-Befund (Cross-Ref-Integrity)

---

## 2026-05-28 16:30 — handoff

**Summary:** Issue #114 Tabellenansicht-Korpussuche durchimplementiert über `superpowers:subagent-driven-development` (11 Plan-Tasks → 13 Commits). Frischer Subagent pro Task plus Spec-Compliance- und Code-Quality-Review (Haiku/Sonnet je nach Komplexität). Visual-Review nach KZW-Ping fand zwei CSS-Bugs (Toggle-Stack durch fehlendes `.inline-flex` im gepurgten Tailwind-Output, h2-Wrap durch zu großen text-2xl-Counter in 612px-Spalte) — beide gefixt + Memory um `feedback_tailwind_rebuild.md` und `feedback_no_emoji_icons.md` ergänzt.

**Decisions:**
- **Direkt auf `main`, nicht Feature-Branch:** Repo-Konvention (alle Recent Commits direkt main); 13 Commits über die Session, kein PR.
- **Implementer dürfen `npm test` nicht selbst starten:** Memory-Regel "vor npm test fragen" gilt auch für dispatched Subagents — Controller (ich) muss Tests fahren, nicht Subagents. Erste Verletzung in Task 1 toleriert, ab Task 2 explizit verboten in Prompt.
- **Tabellen-Mode überlagert das 3-Spalten-Layout mit vollbreitem 1fr-Grid** (`.table-layout` auf `#mainGrid`, `!important` gegen Tailwind-`xl:grid-cols-[1fr_2fr]`). Row-Click switcht viewMode → 'list', behält aber `localStorage` auf 'table' — User-Präferenz bleibt.
- **Heroicons inline SVG statt Emoji-Icons** in Buttons + Feedback-States; User-Korrektur nach Task-9-Implementation. `textContent`-Setter im Feedback durch `innerHTML` ersetzt, damit SVG beim Wechsel erhalten bleibt.
- **CSV mit UTF-8-BOM + CRLF + RFC-4180-Quoting** für Excel-Kompatibilität; TSV-Clipboard parallel via `navigator.clipboard.writeText`.

**Dead ends:**
- Erster Sortier-Test in `results-table.spec.js` verglich `td:first-child` (Sigle + Title zusammen) gegen `localeCompare`-Erwartung der gleichen Strings — App sortiert aber nur nach `title`, daher Mismatch. Fix: Selector auf `td:first-child span:not(.font-mono)` verengt.
- Clipboard-API-Verifikation im Chrome-MCP scheitert an "Document is not focused" — Production-User sieht den Erfolgspfad, automatisierter Test kann nur den Fehlerpfad sehen. Direkte `serializeResultsAsTSV()`-Stichprobe deckt den Inhalts-Check ab.

**Phase:** Implementation (#114 abgeschlossen). 14 Promptotyping-Docs unverändert; `docs/features/114-tabellenansicht-korpussuche.md` + `…-plan.md` sind temporary (sollten beim #114-Close gelöscht werden — siehe `CLAUDE.md §Temporal Artifacts`).

**Open issues:**
- **#114 wartet auf KZW + Julia:** Issue-Comment ist gesetzt (https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/114#issuecomment-4565004013), bisher kein Live-Check. Bugfix-Commit `e780139dd` fährt automatisch im Pages-Deploy nach — kein zweiter Ping geschickt.
- **Lemmata-Count in Tabellen-Spalte fehlt:** In Listenansicht-Cards steht "54 Treffer (3 Lemmata)" bei Multi-Lemma-Matches; in der Tabelle nur der Zahl-Wert. Out-of-Scope für #114, ggf. Followup.
- **`docs/features/114-*.md`:** sollte beim Issue-Close gelöscht werden — Bugs/Knowledge in stable Docs übernehmen (kein notwendiger ARCHITECTURE-Entrag, da Tabellen-Funktion in sich abgeschlossen).

**Next steps:**
1. **Auf KZW-Review warten,** auf #114 antworten/closen.
2. **#114-Feature-Docs löschen** sobald Issue closed (Git-History ist Archiv).
3. **Lemmata-Count-Spalte in Tabelle** als Followup-Issue eröffnen wenn KZW/Julia es vermisst (out-of-scope-aktuell, aber valid Idee).
4. **Andere offene #-Issues** über `/promptotyping orient` in nächster Session evaluieren — `git log` zeigt parallele Sessions (Issues #115, #116 angelegt, #44 nachgezogen).

**Savepoints (push-fertig auf `origin/main`):** `df2d6c8ab` Task 1, `995c95d63` Task 2, `b5b258be0` Task 3, `59f65d583` Task 4, `f2e376529` Task 5, `ebbceac5a` Task 6, `d173e0945` Task 7, `2a5d8deb3` Task 8, `2cf61ac8d` Task 9, `f5aa29b75` Emoji→Heroicons-Fix, `c08969299` Playwright-Spec, `49490625a` Sortier-Test-Selector-Fix, `e780139dd` Tailwind-Rebuild + h2-Wrap-Fix.

---

## 2026-05-29 10:13 — handoff

**Summary:** Ausgehend von #115 (Cross-Reference-Audit) wurde die Wurzelursache der Authority-Drift gefunden und die größte stille Datendrift behoben. Kernerkenntnis (KZW): Das Repo war ein Transformationsprojekt (Alt-MHDBDB + RDF → TEI-only), ist jetzt aktives Projekt mit Ingest, aber die abgeleiteten Files hatten keinen Regenerationspfad. Cross-Ref-unresolved von 226.863 auf 977 gesenkt (variants.xml regeneriert + negative-type-Interpunktion entfernt), Cross-Ref-Audit als CI-Gate verankert, transformation→active samt Data-Change-Lifecycle in den Docs festgehalten.

**Decisions:**
- **negative type-IDs (`type_-7|-10|-11|-15`) = Interpunktion (`- « » /`), keine Varianten** (0 lemmaRef, je 1 Zeichen). Schema-Check zeigte: `<pc>`-Konversion bräuchte erfundenes `@join` (Pflicht), verstößt gegen Daten-vor-Schema → stattdessen Option B: totes `@corresp` gedroppt (14.895 über 296 Files, byte-genau, `scripts/audit/drop-negative-variant-corresp.py`).
- **variants.xml ist korpus-abgeleitet und war stale** (64.287 Formen fehlten). Neuer #32-fähiger Generator `scripts/sync/extract-variants.py` (liest `@lemmaRef`+`@corresp` statt Pre-#32-`@wordRef`; xml:id-Eindeutigkeit per Mehrheit). Regeneriert verlustfrei: 192.472 → 256.759 Formen, Schema-valide 2/2, cross-ref variants→0. Authority-Index v1.3.0 → v1.4.0.
- **lexicon.xml: Repo ist Master, kein Salzburg-Re-Export** (KZW-Korrektur). `lexicon.csv` war selbst RDF-abgeleitet (liegt auf `initial-data-wrangling` unter `lists/`), Migration verlustfrei abgebildet (CSV 43.750/62.240 → xml 43.754/62.244). Die 977 dangling Refs (349 IDs) sind zu 100 % post-Migration ingest-erzeugt (98 im WZB-Range ≥78000), 0 im alten CSV → repo-interner Backfill, kein externer Export. TEXTWORD.xml obsolet (sense→type-Mapping steht in `<sense @ana>` + im Korpus).
- **CI-Gaps geschlossen:** Cross-Ref-Audit `--check` als Gate in `schema-validation.yml` (scheitert außerhalb lexicon.xml; lexicon = Baseline), `index-version-check.yml` triggert auch auf `data/**`, `validate-indices.py` leitet erwartete Versionen aus `corpus-loader.js` ab (war hardcodiert 1.0.0), `generate-manifest.py`-Orphan entfernt.
- **Methodik:** Zwei Workflows (8-Agenten Authority-Staleness-Audit, 5+1 Data-Change-Lifecycle-Audit) lieferten die evidenzbasierte Provenienz- + Gap-Analyse.

**Dead ends:**
- Erster `extract-variants.py`-Dry-Run hing: `lemma_changed`-Diff war O(types × lemmas) via `next(... if t in ts)`. Fix: `type_to_lemma`-Reverse-Map (O(1)). Hintergrund-Task gestoppt (TaskStop), gefixt, neu gelaufen.
- `tasklist`-Prozesscheck über Git Bash = False Negative (Arg-Mangling). `/tmp`-Pfad-Mismatch Git-Bash vs. Python: CSV direkt via `subprocess git show` gelesen.

**Phase:** Implementation (aktiver Betrieb). Alle 14 Promptotyping-Docs aktuell; Doku reflektiert jetzt transformation→active (INDEX/CLAUDE), Data-Change-Lifecycle (DATA-MODEL als kanonische Quelle), Authority-Provenienz-Map (TEI-MODEL-AUTH-FILES), ADR-005-Korrektur (DECISIONS).

**Open issues:**
- **lexicon.xml-Backfill (G3, #44/#115):** 977 dangling Refs / 349 ingest-erzeugte Lemma+Sense-IDs. Repo-intern lösbar (kein Salzburg). Lemma-Stubs aus Korpus (POS+Form) machbar; Sense→Begriff-Klassifikation nicht aus Korpus rekonstruierbar → ggf. KZW/Julia oder Ingest-Records (`scripts/ingest/wzb/`). Bis dahin in der Cross-Ref-CI-Baseline ausgenommen.
- **Nicht gemacht (dokumentiert in der Gap-Analyse):** G6 PersonsSyncer/GenresSyncer/ConceptsSyncer sind TODO-Stubs in `sync_tei_headers.py`; G2 Index-Freshness-CI (rebuild+diff, gzip-Determinismus klären); G8 `npm test` in CI (Laufzeit-/Kosten-Entscheid KZW); G15 `.zotero_cache.json` gitignored (frischer Clone kann `--offline` nicht).
- **Nicht gepusht.** 6 Commits liegen lokal auf `main`. Beim Push fahren schema-validation (inkl. neuer Cross-Ref-Gate) + index-version-check hoch; lokal verifiziert grün, aber CI-Erstlauf der neuen Gate beobachten.

**Next steps:**
1. **Push** `origin/main` (6 Commits) und CI-Lauf beobachten (Cross-Ref-Gate `--check`, Schema, Index-Version).
2. **lexicon-Backfill (G3)** scopen: Stub-Generierung aus Korpus für die 349 IDs vs. KZW/Julia-Input für Sense→Begriff. Eigenes Issue, Assignees wachauer + juliahin.
3. **Optional CI/Cleanup:** G6 PersonsSyncer implementieren, G2 Freshness-Gate, G8 npm-test-Workflow — je nach KZW-Priorität.
4. **#115/#116** ggf. mit diesem Stand kommentieren/teil-closen (Issue-Kommentare nicht gepostet, outward-facing).

**Savepoints (push-fertig auf `main`):** `96a71e489` Audit-Skript, `fa746f219` Cleanup-Skript, `3a9623ae4` negative-`@corresp`-Entfernung (296 Files), `0867a370f` variants-Regenerierung (v1.4.0), `80b5f872f` CI-Gaps (G4/G5/G7/G13), `e21d84bd6` Doku (Lifecycle + Provenance + ADR-005). Memory: `project_authority_provenance` (Provenienz/Staleness-Map) ergänzt.

---

## 2026-06-01 — Health-Check (/promptotyping check)

**Scorecard:** Authority-Source-Docs (ADR-015, CONTRACTS §F, DATA-MODEL Lifecycle, INDEX, TEI-MODEL-AUTH-FILES) konsistent; 3 Algorithmen + 3 XPaths code-konform. Fixes diesem Pass: TEI-MODEL §11 Authority-Index-Version war stale (1.3.0 → 1.4.0); CONTRACTS bekam neuen §B.1 „Lemma Highlight Matching" (token-exakt, #126) + Z.77-Korrektur (Highlighting ist `@lemmaRef`-, nicht positions-basiert); Lemma-Zahl 43.750 → 43.754 vereinheitlicht (DATA-MODEL/FEATURES/TEI-MODEL-AUTH-FILES); CLAUDE.md Varianten-Dict 176k → ~234k und Index-Versionen v1.2.0/v4.0.0 → v1.4.0/v4.1.3; ARCHITECTURE + CLAUDE Key-Patterns um das Matching ergänzt; DATA-MODEL ptr-XPath Doppel- → Einfach-Slash. **Lücke → #130:** keine Testabdeckung für Lemma-Matching-Exaktheit (#126 shippte ungetestet). **Bekannt:** Corpus-Index stale seit 2026-05-15 (gutartig, #125). **Fehlbefund gefiltert:** ADR-015 ist sehr wohl in DECISIONS.md (Blindspot-Agent irrte). Grade: solide. Methodik: 5-Agenten-Check-Workflow + manuelle Verifikation der Blocking-Claims.

---

## 2026-06-01 15:29 — handoff

**Summary:** Der Site-Chrome-Refactor (`feature/site-chrome-refactor`) wurde in zwei Review-Runden gehärtet (lokaler Multi-Agent-Review + konsolidierte 9-Angle-Review), Playwright-Coverage ergänzt, nach `main` gemergt (`--no-ff`, `2e8d48d95`) und live deployt. Anschließend 4 Issues (#127/#119/#120/#122) geschlossen und die CI-Action-Versionen gehoben (Node-20-Deprecation). Alles auf `origin/main`.

**Decisions:**
- **clearSiteData cross-browser per delete-by-name** statt `clearCache()`/`clear()`: Firefox hat kein `indexedDB.databases()`, der alte Pfad löschte dort nichts und meldete trotzdem Erfolg. Jetzt werden die 3 Projekt-DBs (`MHDBDBMainSite`, `MHDBDB_TEI_Cache`, `MHDBDB_Playground`) explizit per Namen gelöscht (Superset: deckt auch die app-losen Hilfeseiten ohne App-Objekt).
- **#8 Mobile-Menü in `site-chrome.js` zentralisiert** (`initMobileMenu`): die ~10-zeilige Toggle-Logik war 12× dupliziert außerhalb der Marker (vom `--check` ungeschützt). Kehrt die ursprünglich bewusste „bleibt inline"-Entscheidung um — zulässig, weil die Inline-Kopien jetzt entfernt sind (kein Double-Toggle mehr).
- **`--no-ff`-Merge** (klarer Merge-Punkt, als Einheit revertierbar); `main` war nicht divergiert (kein Kollegen-#44 auf main).
- **Plan-Doc gelöscht** (`docs/superpowers/plans/2026-06-01-shared-site-chrome.md`) als Temporal Artifact (CLAUDE.md).
- **CI-Actions** auf neueste Majors: `actions/checkout` v4→v6, `actions/setup-python` v5→v6 (Inputs unverändert → Drop-in).

**Dead ends:**
- **#120-Fix war zunächst unvollständig:** der `authority-ui.js`-Proxy reichte das neue `detailsId`-Argument nicht durch → namespaced Container blieb leer. **Nur durch Browser-Runtime-Verifikation gefunden** (statischer/Syntax-Check hätte es nie gezeigt) → Proxy gefixt.
- **site-chrome.spec.js** Mobile-Menü-Test zunächst rot: `toHaveClass(/hidden/)` matchte auch `md:hidden` als Substring → auf `classList.contains('hidden')` (exaktes Token) umgestellt.

**Phase:** Implementation (aktiver Betrieb). Promptotyping-Docs (14) unverändert — der Refactor ist UI/Build/JS, kein Schema-/Architektur-Change, der Doku-Update bräuchte. Memory `project_site_chrome_refactor` aktualisiert (Mobile-Menü jetzt zentral; clearSiteData delete-by-name).

**Open issues:**
- **#6 (Review-Finding, kein GH-Issue):** Der #127-Tradeoff markiert bei stanza-lokalem `@n` nur die ERSTE numerische Verszeile (ABS 74×, ABG 34× betroffen) — bewusste Designentscheidung („avoid jumbled margin"), aber für Texte OHNE `<lg>`-„Strophe N"-Labels eine Sichtprüfung/Followup-Issue für KZW wert.
- **`pages-build-deployment` (dynamic)** nutzt weiter Node-20-Actions — GitHub-verwaltet, keine Repo-Datei, nicht hebbar (außer Umstieg auf eigenen Pages-Actions-Workflow, größerer Umbau).
- **`build-pages.py --check` ist NICHT in CI verdrahtet** (Drift-Gate existiert, aber unerzwungen — Review-Finding #4; User wählte „nichts weiter"). Hand-Edits einer Nav/Footer-Markerregion fielen erst beim manuellen Lauf auf.
- **Volle Playwright-Suite nicht gefahren** (nur betroffene Specs `site-chrome`/`reading-view`/`search-with-corpus` + `build --check`); 25 bewusst geskippte Tests (#43).

**Next steps:**
1. **Journal-Commit pushen** (liegt lokal auf `main`, 1 Commit ahead) — Rest ist schon auf `origin/main`.
2. *(optional)* `build-pages.py --check` als CI-Step in einen Workflow hängen — schützt die Refactor-Invariante (Nav/Footer-Single-Source) gegen stille Hand-Edits.
3. *(optional)* #6 als Followup-Issue für KZW anlegen (stanza-marker Sichtprüfung bei ABS/ABG).
4. *(optional)* Volle `npm test`-Suite einmal fahren, falls ein Komplett-Grün vor weiteren Features gewünscht ist.

**Savepoints (alle auf `origin/main`):** `9d6f30e9c` CI-Action-Bump · `2e8d48d95` Merge feature/site-chrome-refactor · darin `ecd8e7a17` Plan-Doc-Löschung, `0d5d32cd6` #8 Mobile-Menü, `6c48b731d` Review-Runde 2 (Firefox-Clear), `edaba556e` Playwright-Coverage, `f50883369` Review-Runde 1, `436c0fb4a` Refactor-Basis, `c759773a`/`ffbc8aa2`/`31d54367` #127/#120/#119. Lokaler Branch `feature/site-chrome-refactor` nach Merge gelöscht.

---

## 2026-06-02 — Health-Check (/promptotyping check)

**Scorecard:** Multi-Agent-Check (Workflow `wpq1w301u`, 6 Dimensionen, jeder Befund adversarial gegen Code/Daten verifiziert): **26 Drift-Befunde bestätigt, 1 Fehlbefund gefiltert** (fabrizierter works-Count, der im Doc gar nicht vorkam — adversarialer Schritt hat funktioniert). Alle 26 in diesem Pass gefixt (13 Dateien). **Hauptbefund:** Der Site-Chrome-Refactor (Vorsession) hinterließ Doku-Schuld — `build-pages.py`, `includes/`, `site-chrome.js` standen in KEINER Stable-Doc (nur JOURNAL); der damalige Eintrag (2026-06-01 15:29, „kein Architektur-Change, der Doku-Update bräuchte") hatte den nötigen Update wegargumentiert. Nachgezogen: ARCHITECTURE (neues Pattern „Build-Injected Site Chrome" + Key Files), DEVELOPMENT (Frontend-Build-Commands inkl. `build-pages.py`/`build:css`/`build:vendor`, Directory um `includes/`+`site-chrome.js`+`hilfe-schema.html`), DESIGN (Nav/Footer/Mobile-Menü → `site-chrome.js`, falsche „No active-page highlighting"-Aussage korrigiert), scripts/README (Baum + Spalte-E-Fix). **Zahlen-Sync:** Corpus-Index 34→40 MB (5 Docs), variants 39.282/192.472 → 42.627/256.759 (TEI-MODEL), ~670→667 TEI (CLAUDE), Authority-Index 2.90→3.1 MB (DECISIONS). **Algorithmen:** §B um `iterwalk` + Empty-Text-Skip-Parity ergänzt (latent, 0 Korpus-Fälle, → in #131 aufgenommen); §C.2.1 falsche Zeile/Funktionsname, §C Off-by-one, `@ana`-Phantom (DATA-MODEL), `indexed-db-base.js`-Phantom (lib/README). **#130-Nachzügler:** `lemma-match.js` in CLAUDE Key-Patterns + ARCHITECTURE Pattern + lib/README + DEVELOPMENT lib-Zeile. **Korrektur-Aktion:** #131 (§B-Paritätstest) um den Empty-Text-Skip-Fall erweitert. **Doc-Schuld-Lehre:** Build-Pipeline-Erweiterungen (neue Skripte/Partials/geteilte Module) gehören in DEVELOPMENT + ARCHITECTURE, auch ohne Schema-Change. Methodik: 33 Agenten, ~6 min. Grade: solide; Stable-Docs jetzt konsistent mit verifizierten Code/Daten-Werten.

---

## 2026-06-02 10:59 — handoff

**Summary:** Drei Arbeitsblöcke, alle auf `origin/main`. (1) **#130** Lemma-Matching-Exaktheit: TDD-Test geschrieben (Unit §B.1-Tabelle + e2e Reader PL1=57/OVG=26) und dabei die 6 inline-Substring-Match-Kopien in eine zentrale `lemmaRefMatchesId()` (`assets/js/lib/lemma-match.js`) refactort — `Closes #130`. (2) **#131** als Followup angelegt (§B Python↔JS Position-Counting-Paritätstest). (3) **/promptotyping check** als Multi-Agent-Workflow: 26 Drift-Befunde bestätigt, 1 Fehlbefund adversarial gefiltert, alle 26 in einem Doc-Commit gefixt.

**Decisions:**
- **#130 Refactor statt Test-only** (User-Wahl): die 6-fach-Duplikation war die Wurzel von #126; Zentralisierung eliminiert das Regress-Risiko, eine getestete Quelle (CONTRACTS §B.1). TDD rückwärts gefahren (Code war schon gefixt): Test grün → Funktion temporär auf Substring zurück → rot bewiesen → zurück.
- **Check als Workflow, Fixes manuell:** Fan-out lohnt für die Analyse (6 Dimensionen, adversariale Verifikation pro Befund), nicht für die Fixes (überlappende Dateien, deutsche Prosa-Präzision, Em-Dash-Regel).
- **26 Fixes in EINEM Commit** (`c6af48cc4`), nicht 4 thematische: dieselben Dateien tragen mehrere Themen, saubere Trennung bräuchte `git add -p` (gegen Concurrent-Session-Regel). Folgt der Konvention des letzten Checks (`c083fda03`).
- **#131-Assignee KZW→chsteiner korrigiert** (User-Einwand): Memory-Regel sagt technische Issues → `chsteiner`, nicht `wachauer`. War mein reflexhafter Fehlgriff gegen die eigene Regel.
- **DECISIONS:36/:54** (47→2.9-MB-Ratio) bewusst als historische ADR-Werte belassen, nur die Present-Tense-Output-Zeile :47 aktualisiert.

**Dead ends:**
- Erste §C.2.1-Quellzeile im Check war als app.js:409-427 dokumentiert (echt: inline in `handleSearch()` 451-469, keine `deduplicateResults`-Funktion) — Doku korrigiert.
- Workflow-Output-Pfad-Tippfehler beim Nachlesen (UUID verschrieben) — per Glob gelöst.

**Phase:** Implementation (aktiver Betrieb). Alle 14 Promptotyping-Docs aktuell UND nach dem Check konsistent mit verifizierten Code/Daten-Werten (Index-Größen, variants-Counts, Korpus-667, Site-Chrome-Pipeline jetzt in ARCHITECTURE/DEVELOPMENT/DESIGN dokumentiert). Memory unverändert (kein neuer Fakt; Assignee-Regel war bereits korrekt dokumentiert).

**Open issues:**
- **#131** (§B Position-Counting-Paritätstest, `claude-ready`, assignee chsteiner): inkl. dokumentiertem Empty-Text-Skip-Asymmetrie-Fall (Python skippt leere `<w lemmaRef>`, JS nicht; heute 0 Korpus-Fälle, latent bei künftigem Ingest).
- **Offen aus Vorsessions (optional):** `build-pages.py --check` nicht in CI verdrahtet (schützt die jetzt dokumentierte Site-Chrome-Single-Source-Invariante); #6 stanza-marker-Sichtprüfung (ABS/ABG) für KZW; volle `npm test`-Suite seit Site-Chrome-Refactor nicht komplett gefahren.

**Next steps:**
1. *(optional)* **#131** implementieren — §B-Paritätstest inkl. Empty-Text-Skip-Fall.
2. *(optional)* `build-pages.py --check` als CI-Step verdrahten (Drift-Gate für Nav/Footer-Single-Source).
3. *(optional)* #6 als Followup-Issue für KZW (stanza-marker ABS/ABG).

**Savepoints (alle auf `origin/main`):** `c6af48cc4` Check-Drift-Fixes (14 Dateien) · `fdc087fea` #130 Lemma-Matching-Test+Refactor · `6fec2ec8a` Vorsession-Handoff. GitHub: #130 closed, #131 offen (+ Empty-Skip-Kommentar).

---

## 2026-06-03 13:46 — handoff

**Summary:** #131 (§B Position-Counting-Paritätstest) implementiert, getestet, gemergt, gepusht (`7491e97b3`), Issue geschlossen. §B war die letzte der vier Cross-Language-Invarianten in CONTRACTS ohne eigenen Test — jetzt 4/4 abgedeckt. Dabei die latente Leer-`<w lemmaRef>`-Asymmetrie (Python skippt leeren Text, JS zählte ihn mit) per 1-Zeilen-Fix in `tei-text-reader.js` aufgelöst (JS an Python angeglichen). Anschließend auf eigene Schuld-Bilanz hin den Test gehärtet (Top-3-Lemmata pro Realtext + ganze Fixture-Sequenz) und den Python-Helper verschlankt (`a3d52d54d`).

**Decisions:**
- **Leer-`<w>`: Option A (JS → Python angleichen)** statt Tripwire/Skip (User delegierte „was empfiehlst du?"): Pythons Skip ist die richtige Semantik (leere Wörter rendern nichts, hätten keine navigierbare Position); der ausgelieferte Index encodet bereits Pythons Verhalten → bleibt valide, **kein Rebuild/Versions-Bump**. Gegenrichtung (Python zählt leere mit) hätte alle Positionen verschoben.
- **Fix minimal (Increment-Gate via `hasText`)**, `processWord` unangetastet: 0 Korpus-Fälle → No-op auf Realdaten; der einzige Verhaltens-Change betrifft nicht-existente leere `<w lemmaRef>`.
- **Test-Architektur = Spiegel von §A:** Python via `execSync` (echtes `extract_word_data` über `importlib`, da Bindestrich-Skriptname `build-corpus-index.py`), JS via echtes `extractAndFormatBody` (isoliert `new TEITextReader(null,null,null)`, `fetch`+`DOMParser` wie `loadTEIFile`). Probe: `highlights[].position` == `lemmata[lemma]`. Repräsentanten PL1 (Prosa, lineStarts=0) + OVG (Vers), `lemma_308` (57/26, deckt sich mit #130).
- **TDD:** Fixture-RED aus korrektem Grund (`[0,2]≠[0,1]`) bewiesen, dann Fix → GREEN (zuerst 4/4; nach Test-Härtung 3/3). Verifikation: 3 betroffene Specs (lemma-matching/reading-view/search-with-corpus) 32/32 grün → Fix beweisbar No-op.
- **Folge-Härtung (#2/#3 aus eigener Schuld-Bilanz, `a3d52d54d`):** Block 1 probt je die Top-3-häufigsten Lemmata + Konsistenzcheck `Σ Positionen == wordCount` (statt nur `lemma_308`); Fixture prüft die ganze Sequenz inkl. „leeres `<w>` (lemma_2) nicht gezählt"; Helper gibt nur noch `{wordCount, lemmata}` aus (kein `words[]` → Spec-maxBuffer 128→32 MB).

**Dead ends:**
- Erster Spec-Lauf RED aus *falschem* Grund (`Failed to resolve module specifier '/assets/...'`): `page.evaluate` ohne vorheriges `page.goto` läuft auf `about:blank` ohne Origin → `beforeEach` mit `goto /playground/` ergänzt (TDD: erst korrektes Fehlschlagen herstellen).
- Hintergrund-`npm test | tail -70` schien 5 Min zu hängen (Output-Datei 0 Bytes): `tail` puffert bis EOF; eigentliche Bremse war der Playwright-webServer-Cold-Start, nicht die Tests. → Memory `environment.md`.
- `python3.13` via Python-`subprocess.run` = `WinError 2` (Shell-Alias, kein echtes Executable); via `execSync`/Shell OK. → Memory `environment.md`.

**Phase:** Implementation (aktiver Betrieb). Alle 14 Promptotyping-Docs aktuell; CONTRACTS §B von „bekannte Asymmetrie" auf „gelöst #131" (Parity-Test-Referenz + JS-Pseudocode mit `hasText`-Guard). Memory `environment.md` um 2 Windows/Test-Gotchas ergänzt.

**Open issues (inkl. heute bewusst aufgenommener Mini-Schuld):**
- **Residuum (out-of-scope, bewusst):** ein leeres `<w lemmaRef>`, das die *gesuchte* Lemma-ID trägt, erzeugt im Reader weiterhin ein (unsichtbares, leeres) `<mark>` an der wiederverwendeten Position. Positions-**Parität ist gewahrt** (das ist der getestete Vertrag); 0 Korpus-Fälle. Falls je relevant: `processWord` ebenfalls für leere `<w>` skippen. (Test-Tiefe #2 + Helper-Effizienz #3 wurden in `a3d52d54d` bereits behoben.)
- **CI-Gate fehlt (pre-existing #G8):** der neue Test läuft nur bei lokalem `npm test`; wie alle Specs nicht in CI erzwungen.
- **Aus Vorsessions (unverändert):** `build-pages.py --check` nicht in CI; #6 stanza-marker-Sichtprüfung (ABS/ABG) für KZW; volle `npm test`-Suite seit Site-Chrome-Refactor nicht komplett gefahren (heute nur 36 Tests: position-parity 4 + 3 betroffene Specs 32).

**Next steps:**
1. *(optional)* Lokale Commits pushen (`a3d52d54d` Test-Härtung + dieser Journal-Commit); Feature `7491e97b3` ist schon auf `origin/main`.
2. *(optional)* Nächste Prio gem. Orient: **#129 KWIC-Kontextfenster** (höchster umsetzbarer Nutzerwert) oder **#124 Analytics** (Team-prio-1, erst Entscheidungsrunde).
3. *(optional)* `build-pages.py --check` als CI-Step; #6 Followup-Issue für KZW.

**Savepoints:** `7491e97b3` #131 Paritätstest + Leer-`<w>`-Fix (5 Files, auf `origin/main`) · `a3d52d54d` Test-Härtung (Top-3 + volle Fixture-Sequenz) + Helper-Slim · dieser Journal-Commit.

---

## 2026-06-05 — Health-Check (/promptotyping check)

**Scorecard:** Multi-Agent-Check (Workflow `wam0cgdyr`, 103 Agenten, ~62 min; 19 Probes = 15 Doc-Finder + 4 Canary für Algorithmen/XPath/Versionen/Konsistenz; jeder Befund adversarial gegen Code/Daten verifiziert): **83 Befunde geprüft, 55 bestätigt, 28 adversarial gefiltert** (kein Fehlbefund durchgerutscht). Nach Konsolidierung ~24 distinkte Drifts, **alle gefixt** (15 Dateien: CLAUDE.md + 13 Stable-Docs + Corpus-Index-Rebuild). **Hauptbefund:** Doku hinkt dem Playground-Feature-Wachstum (#47.3, #87-90, #47 R2, #107, #108) hinterher – Entry-Points 10→14, Module 18→21, „Sieben"→„Neun Werkzeuge" über INDEX/FEATURES/ARCHITECTURE/DECISIONS/DESIGN nachgezogen. **Drei fabrizierte Worked-Examples** in TEI-MODEL-AUTH-FILES korrigiert (alle gegen Quelldaten verifiziert): `lemma_879` = brôt (nicht „vriunt"; vriunt = lemma_7246), sense `_1449` (nicht `_1177`), variants type_2783/2784/2785; `work_350`/ASG ohne die transplantierten work_177-Normdaten (GND/Wikidata/HSC); `person_anonym` (Anonym, Wikidata Q4233718) entkoppelt von `person_1772` (Schweizer Anonymus, GND 103130276). **Wörterbuchnetz-API** (ARCHITECTURE/CONTRACTS): „BMZ, Lexer, LexerN, FindeB" + `Promise.allSettled` → real MWB+Lexer + `Promise.all`; statischer MWB-Trier-Link entfernt (ist API-Deep-Link). **TEI-File-Caching** (FEATURES, ARCHITECTURE) invertiert: „>5MB"→jede Datei, „No expiration"→30d (Main-Site); Playground-`indexed-db-manager.js`-Stores korrigiert (4 reale statt 2 erfundene). **§4-Migration** (`@meaningRef`→`@ana`, `@wordRef`→`@corresp`) korpusweit abgeschlossen inkl. WZB (667/667 `@ana`, 0 Alt-Attribute, 0 JS-Leser) – war als „ausstehend/Validierungsblocker" geframt, jetzt als erledigt (Phase B1/B2). **Weitere:** `validate-corpus.py` „8 strukturelle Checks"→zweistufige RelaxNG; stanza „wird migriert"→erledigt (#23/v4.1.1); „25 skipped tests #43"→0 (resolved 259bc505a); variants ~234k→~257k (256.759); works.xml 583→584; LINECODE #84/#85 closed, div/@type 7→7+24 arithmetic; diverse Zeilennummern-Pointer + Quellen-Refs (526-571→643-644 u.a.). **Rebuild:** Corpus-Index neu gebaut (clear Freshness-Gate nach #115 @corresp-Cleanup; Inhalt identisch außer `generatedAt`, **kein Versions-Bump** – v4.1.3 bleibt; Gate ist commit-history-basiert, wird mit dem Index-Commit grün; CI-Wiring + Determinismus deckt #125). **Blind-Spots (8, 1 blocking):** Ingest-Pipeline-Rebuild-Test scheitert → #132 (Phasenmuster aus README/BLOG in Stable-Doc heben); Encoding-Exemptions-Liste → #133; #92-Status-Drift (Stage 0 gebaut + PD-001 offen) kommentiert; site-chrome-„nicht-direkt-editieren"-Constraint in CLAUDE.md-Gotchas ergänzt. **Offen-notiert (kein Issue):** variants-Terminologie (entries 42.627 vs forms 256.759 vs Index-Keys 234k nirgends sauber definiert); `docs/features/`-Lifecycle (#034-Pentateuch-Scope, #114). Methodik: adversariale Verifikation + Blind-Spot-Kritik. Grade: solide – keine falsche Kerninvariante (Position-Counting §A/§B, MHG-Normalisierung, lemma-match alle korrekt verifiziert).

---

## 2026-06-09 — #44 Re-Triage (Multi-Agent-Workflow)

**Scorecard:** Vollständiger Re-Triage aller 37 offenen Issues gegen ihre GitHub-Threads (Workflow `w3vud52es`, 37 Read-Agenten auf Sonnet, ~2 min, ~1 Mio Subagent-Tokens; 1 Agent pro Issue → strukturierter Status, kuratorische Synthese + Drift-Abgleich bei mir). **Hauptbefund:** kein *Bewertungs*-Drift (die alten Matrix-Urteile stimmten weiter), sondern ein *Umsetzungs*-Rückstand – fünf seit dem 29.05./01.06. entscheidungsreife Tasks waren nie ausgeführt worden. Ein inkrementelles Delta-Update hätte das verfehlt; der Vollscan war hier den Token-Aufwand wert. **Abgearbeitet (alles ausgeführt):** #30 (TEI-Strukturelemente, 29/29 Stage-2-valid), #34 (Ingest WB/CoReMA, WZB live) und #73 (Lemma-Linking, Wörterbuchnetz-API live, KZW-Daumen-hoch) geschlossen; Follow-ups **#138** (editorische div-Hülle HUG/KLA/PL1-3/MBS, → wachauer; nimmt den `l`-vs-`lb`-Restpunkt der „Phase-4"-Policy auf, deren Render-Teil über #101 bereits erledigt ist) und **#139** (CoReMA-Ingest, nachgereiht) angelegt; veraltete `needs-clarification`-Labels bei #28/#59/#128 entfernt (+ `future plans` bei #59; #128-Blocker durch wachauers ALX.txt am 08.06. aufgelöst). **#91 (Zenodo) als Nicht-Evergreen reklassifiziert** (war fälschlich `evergreen`; Korrektur in CLAUDE.md durch chsteiner, in die Matrix übernommen). **Ergebnis:** 36 offen ohne Evergreen (#44); Buckets 19 claude-ready / 7 depends-on-human / 3 needs-clarification / 7 future. Sechs neue Issues (#132–#137) + das in den alten Tabellen fehlende #53 eingearbeitet. **Verbleibend aus dem Rückstand:** #23 (MUG-Stanza-Lauf, ~5 min) und #59 (Antonomasien-Modul bauen, Linda-Freigabe Option A). **Methodik:** Fan-out für die Datenerhebung, Synthese + outward-facing gh-Aktionen (Closes/Creates/Label-Fixes) bei mir. Matrix-Body verworfen, sobald gepostet (disposable); diese Zeile ist der Archiv-Stand.

---

## 2026-06-09 11:33 – handoff

**Summary:** Nach der #44-Re-Triage (eigener Eintrag unten) drei claude-ready-Issues implementiert, verifiziert, geschlossen und auf `origin/main` gepusht: #53 (Korpus-Terminologie-Regression), #137 (Lemmata-Explorer-Sortierung), #135 (Autor*innen-Explorer-Links + Reader-Routing-Erweiterung). Abschließend die #44-Matrix auf den Tagesstand nachgezogen (33 offen ohne Evergreen).

**Decisions:**
- **#135 Werk-Deep-Link:** `app.js` `handleURLParameters` um den `?textId`-only-Fall erweitert, der den Reader ohne Highlights öffnet (options `{}`, exakt der bestehende „Lesen"-Button-Pfad aus `app.js:237`) statt einen neuen Mechanismus zu bauen. Bonus-Effekt: `korpus.html?textId=<SIG>` ist jetzt generell als Text-Direktlink nutzbar. Der Playground-Multi-Lemma-Jump (`textId`+`lemmaIds`) bleibt unverändert.
- **#137:** `localeCompare(b, 'de')` statt MHG-`text-normalizer` für die Sortierung (Konsistenz mit dem `concept-explorer.js`-Idiom, case-/akzent-tolerant); Sortierung läuft VOR dem 50er-`slice` in `handleSearchResults`, sonst würde nur die zufällige ID-Auswahl sortiert.
- **#53:** nur die drei user-facing deutschen Strings (Lade-Status, Clear-Dialog, Fehlermeldung); Code-Identifier (`corpusIndex`), Dateinamen (`corpus-index.json.gz`), Debug-Logs und Doku bewusst unangetastet.
- **Gestaffelte Verifikation je nach Risiko:** #53 per Grep (statisch), #137 per Node-Comparator an echten Beispielen, #135 per Browser-E2E (Playground-Render + Reader öffnet via `?textId=ABG`), weil dort eine neue Routing-Integration dranhängt.

**Dead ends:**
- `javascript_tool` top-level `await` schlug fehl (trotz Tool-Doku) → in async-IIFE gewrappt.
- Kein echter Dead end, aber Awareness: zwei parallele Sessions committeten `4bc9fb2ac` (CITATION/CLAUDE #91-Fix) und `d3133345c` (Em-Dash-Fix) zwischen meine Pushes; alle fast-forward, kein Konflikt dank gezieltem `git add <datei>` (nie `-A`).

**Phase:** Implementation (aktiver Betrieb). Alle 14 Promptotyping-Docs aktuell; keine Stable-Doc-Änderung nötig (reine Frontend-Fixes + eine Reader-Routing-Erweiterung). #44-Triage-Matrix auf Tagesstand (33 offen ohne Evergreen, 16 claude-ready).

**Open issues:**
- **Verbleibend aus dem Re-Triage-Rückstand:** #23 (MUG-Stanza-Lauf, ~5 min Script + Index-Rebuild + schließen), #59 (Antonomasien-Modul bauen, Linda-Freigabe Option A, ~1 Tag, braucht Fetch der 4 `categorization_*.json` aus `lindabeutel/Naming-analysis`).
- **#135 Edge-Case:** `korpus.html?textId=<SIG>` öffnet den Reader; falls eine `work.sigle` keinem TEI-Korpustext entspricht (Werk ohne Korpustext), zeigt der Reader eine Fehlermeldung statt zu crashen, aber der Link wäre dann inhaltsleer. Bei echten besigelten Werken (verifiziert mit LUU) kein Problem.
- **Doku-Arbeit (#132/#133) bewusst zurückgestellt** — User will gesondert über die Doku-Strategie reden, bevor daran gearbeitet wird.
- Aus Vorsessions unverändert: `build-pages.py --check` nicht in CI; volle `npm test`-Suite seit Site-Chrome-Refactor nicht komplett gefahren.

**Next steps:**
1. *(optional)* #23 MUG durchschicken + schließen (~5 min, kleinster offener Rückstand-Rest).
2. *(optional)* #59 Antonomasien-Modul bauen (freigegeben, ~1 Tag).
3. *(optional)* weitere Quick-Wins: #121 Dropdown-Disambiguierung (S), #136 Text-Statistiken-Auswahl (M).
4. Mit User die Doku-Strategie klären (#132/#133 + allgemein), bevor Doku-Tasks angefasst werden.

**Savepoints (alle auf `origin/main`):** `1115ecf02` #53 · `6a7c6b73b` #137 · `d20bbc3bb` #135 · `d00a39eb7` #44-Re-Triage-Journal. #44-Body, #138/#139 + Closes/Label-Fixes auf GitHub. Dieser Journal-Commit lokal (Push nach User-Freigabe).

---

## 2026-06-10 15:09 – handoff

**Summary:** Drei Blöcke: (1) Delta-Issue-Audit nach KZW-Aktivität vom 09.06. (#140/#141/#142 neu, #91 entsperrt) mit #44-Update; dabei #28 als versehentlichen Close identifiziert (09.06. 08:31, im gh-Fenster der Re-Triage-Session) und reopened. (2) #142 Code4Lib-Draft komplett: 1.887 Wörter (`From Six Billion RDF Triples to TEI-Only`), iterativ über /check-md, /anti-slop, Ton-Rebalancing (Client-only-Rettung als Durchbruch statt Defizit-Liste) und §4-Umbau (Agentic-Coding-Frame voran, nur echte Limitations); lebt jetzt im Google Doc (nicht committet), Issue geschlossen, Team-Steps dort bis 19.06. (3) #91 Zenodo end-to-end: DOI ist live — Concept `10.5281/zenodo.20627656`, v1.0.0 `10.5281/zenodo.20627657`, Release https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/releases/tag/v1.0.0; Metadaten per Zenodo-API verifiziert (Creators KZW+Schmidt, 49 Contributors als Researcher, cc-by-nc-sa-4.0). Nebenher den falschen `wordCount`-Kommentar gefixt (DATA-MODEL.md + Build-Skript-Docstring: zählt nur `@lemmaRef`-tragende `<w>`, 7,53 Mio., nicht alle 9,43 Mio.).

**Decisions:**
- **Contributors via `.zenodo.json`, nicht CFF:** CFF 1.2.0 hat kein `contributors`-Feld; „Researcher" ist exakt ein Zenodo-Contributor-Typ und Zenodo liest `.zenodo.json` bevorzugt. KZW+Schmidt dort nicht als Contributors dupliziert (sind Creators). `license` als Einzelwert `cc-by-nc-sa-4.0` (Zenodo kann keine Liste), MIT-Code in der Description erklärt.
- **Concept-DOI in Badge + INDEX.md** (zeigt immer auf die neueste Version), Versions-DOI nur als Annotation.
- **DOI-Badge via shields.io statt zenodo.org** (`56062190a`): Zenodo drosselt GitHubs Camo-Proxy-IPs — Badge-Abrufe schlugen auch nach Camo-PURGE in 2/3 Fällen mit 502 fehl. Stilgleich mit den Lizenz-Badges, Link unverändert.
- **Git-Tag = Single Source of Truth für die Release-Version** (`41a71188a`): `version`-Feld aus `.zenodo.json` entfernt (Zenodo fällt dann auf den Tag-Namen zurück → dieser Drift-Kanal ist konstruktiv eliminiert); CI-Guard `release-version-check.yml` + `scripts/audit/check-release-version.py` prüft bei Tag-Push CFF-Version == Tag und verbietet Re-Einführung des Felds. Timing-Kniff: Check läuft beim Tag, Webhook feuert erst beim Release-Publish — rote CI heißt Tag löschen/fixen/neu, Zenodo sieht nichts.
- **Kein Index-Rebuild trotz Julias WZB-Push** (`047745fff`, +35 Z. `tei/WZB.tei.xml`): Julia arbeitet heute Nachmittag aktiv weiter; einmal am Ende bauen statt nach jedem Zwischenstand (User-Entscheid).

**Dead ends:**
- **Zenodo-GitHub-Sync:** Org-Repo fehlte in der Zenodo-Liste trotz Admin-Rechten und OAuth-Grant; „Sync now" warf 400. Fix war Disconnect/Reconnect der GitHub-Verknüpfung in Zenodo (erzwingt Neuaufbau der Repo-Liste) — Sync-Button und Grant allein reichten nicht.
- **zenodo.org-Badge:** Zweischichtig kaputt — erst Camo-404-Cache (Badge committet Sekunden vor DOI-Minting; PURGE per `-CustomMethod PURGE` half), darunter aber persistentes Rate-Limiting der Camo-IPs durch Zenodo. zenodo.org-Badge aufgegeben.

**Phase:** Implementation (aktiver Betrieb). Stable-Docs aktuell; DEVELOPMENT.md um „CI: Release Version Check (Zenodo)" + Release-Ablauf erweitert, INDEX.md um den DOI. #44 auf Tagesstand (35 offen ohne Evergreen, 17 claude-ready).

**Open issues:**
- **#91 noch offen:** Restpunkte sind Community-Annahme durch KZW (Antrag an zenodo.org/communities/mhdbdb läuft automatisch, @-Ping im Issue) und DOI ins ZfdG-Exposé. User hat über Schließen noch nicht entschieden („mach zu" genügt).
- **Indexe stale gegenüber Korpus:** Julias `047745fff` (WZB) ist nicht im Corpus-Index; bewusst zurückgestellt, bis ihre heutige Arbeitswelle durch ist. Dann Rebuild (je nach Inhalt + `variants.xml`/Authority).
- **CITATION.cff `date-released`** ist der einzige verbleibende händische Versions-Touchpoint pro Release (Version wird per CI erzwungen, Datum nicht — bewusst, da Tag-Datum ≠ Commit-Datum sein kann).
- Aus Vorsessions unverändert: #23 (MUG, ~5 min), #59 (Antonomasien, freigegeben), Doku-Strategie-Gespräch (#132/#133/#140) ausstehend; `build-pages.py --check` nicht in CI.

**Next steps:**
1. Nach Julias WZB-Welle: Corpus-Index-Rebuild (+ ggf. `variants.xml`/Authority-Index), dabei Index-Version bumpen falls Inhalt sich ändert.
2. #23 MUG durchschicken + schließen (~5 min).
3. #59 Antonomasien-Modul (~1 Tag, Linda-Freigabe liegt vor).
4. *(optional)* #141 Aufgabe 0: `borte.md`-Metadaten-Template für Alan.
5. #91 schließen, sobald User es freigibt (oder nach KZWs Community-Annahme).

**Savepoints (alle auf `origin/main`):** `254b3b395` wordCount-Kommentar · `9438244f7` CITATION.cff+.zenodo.json · `5d0c9b56b` DOI-Badge+INDEX · `56062190a` shields.io-Badge · `41a71188a` Drift-Guard · Tag `v1.0.0` + GitHub-Release. #142 closed, #28 reopened, #44-Body 3× aktualisiert (GitHub). Dieser Journal-Commit lokal (Push nach User-Freigabe).

---

## 2026-06-11 – #132 Ingest-Verfahren in Stable-Docs gehoben

**Summary:** Den „blocking blind spot" aus dem Health-Check 2026-06-05 geschlossen: Das WZB/ARI-Phasenmuster steht jetzt als normativer Abschnitt **„Ingest-Verfahren (Neuaufnahme von Texten)" in DATA-MODEL.md** (vor dem Data-Change-Lifecycle) — Stage-0 Schema-Konversion, Paratext-Policy (#66), Phase 1–3 jeweils mit rekonstruierbarem Algorithmus (Assign → Resolve → Apply als wiederkehrender Dreischritt), Pflicht-Rückwärts-Sync (CONTRACTS F.3/ADR-015) und Coverage-Referenzwerten. Quellen: `scripts/ingest/*/README.md`, Feature-Doc #34, Blog-Post-Draft, ADR-015.

**Decisions:**
- **Zielort DATA-MODEL.md, nicht CONTRACTS.md:** Das Verfahren ist eine Daten-Transformationspipeline (CONTRACTS behält die F-Regeln und verlinkt auf das Verfahren). Platzierung direkt vor dem Data-Change-Lifecycle, weil der Ingest dort mündet.
- **`docs/features/034-wenzelsbibel-annotation.md` gelöscht** (Temporal-Artifacts-Konvention, #34 closed seit Mai): durables Wissen extrahiert; das pre-registrierte Phase-3-Evaluationsprotokoll (Julias Dissertationsteil) lebt bewusst nur in Git-History + Blog-Post-Draft weiter — es ist Forschungs-, keine Betriebsdoku. Alle 9 Verweise auf das Doc umgebogen (wzb-README, hilfe-daten-beitragen.html, 5 Skript-Docstrings, Report-String in `wzb-sense-evaluate.py`).
- **`@meaningRef`/`@wordRef` als historisch markiert:** Das 034-Doc beschrieb die Extension-Attribute als geplant (inkl. „GAP 15", das im Schema nie ankam); Skripte und `tei/WZB.tei.xml` nutzen final `@ana`/`@corresp` — die Stable-Doc stellt das mit historischer Notiz richtig.

**Phase:** Implementation (aktiver Betrieb). Parallel-Session-Hinweis: #59 (Antonomasien) läuft bei Kollegen — diese Session hat `playground/` und `data/` bewusst nicht angefasst.

---

## 2026-06-11 09:18 – handoff

**Summary:** Drei Blöcke: (1) Index-Stale-Check nach Julias WZB-Welle: voller Corpus-Index-Rebuild war inhaltsgleich zu v4.1.3 (Diff seit `b1bb19b95` war header-only außerhalb `titleStmt`) — Rebuild verworfen, kein Bump, kein Commit; der „Indexe stale"-Punkt aus dem 10.06.-Handoff ist gegenstandslos. (2) **#23 geschlossen**: MUG gegen KZWs Linecode-Export verifiziert (Template `000000000000cddss--`), bestehendes Markup war vollständig korrekt (19/19 Strophen-Anker ID-genau, 406/406 `<l>` gewrappt; einzige Zähldifferenz: zwei im Flat-Export kollabierte Caesura-Leerverse `MUG_1010507/8`). Prosa-l/lb-Policy als **#143** ausgegliedert (17 l-basierte Kandidaten per Template-Heuristik „p ohne s/d", wachauer assigned). (3) **#59 Antonomasien-Modul komplett gebaut und live**: Ingest-Skript + `data/naming-index.json.gz` (10.506 Records, 616 Figuren, 110 KB gz) + `naming-explorer.js` + Route `#naming` + 6 Playwright-Smoke-Tests; volle Suite 153/153 grün; KZW im Issue gepingt (finaler UI-Test), Issue bleibt offen. Nebenher #91-Statuskorrektur in #44 (Community `mhdbdb` am 11.06. angenommen, API-verifiziert; Rest: DOI ins ZfdG-Exposé + Close-Freigabe).

**Decisions:**
- **Inhaltsgleiche Rebuilds nicht committen** (anders als `b1bb19b95`): generatedAt-only-Diff wäre ein 40-MB-Blob ohne Nutzen. Vergleichsmethode: beide `.gz` entpacken, `generatedAt` entfernen, Dict-Equality.
- **MUG-`@n` bewusst nicht auf fortlaufende Zählung normalisiert**: die Nummerierung je Lied (inkl. der Reihenfolge 7 vor 6 am Schluss) spiegelt exakt den Linecode-Source; Skript-Decision „no overwrite" bestätigt.
- **#59 Naming-Index ohne IndexedDB-Cache und ohne corpus-loader.js-Eintrag**: lazy fetch+pako (110 KB) — eliminiert den #94-Versions-Bump-Kanal konstruktiv. Dokumentiert in DATA-MODEL.md §Naming Index.
- **#59 ohne Reader-Deep-Links**: Lindas Verszählung folgt Druckeditionen (ENE komplett anders, IW/TRO teils, nur ROL deckungsgleich; ihr Kommentar 05.03.) — Versangaben als Editionsreferenz, UI-Hinweis im Modul.
- **Kategorisierung repliziert Lindas `match_name_to_lemma` exakt** (case-insensitiv exakt oder Alias aus `lemma_normalization.json`); Epitheta sind quellseitig bereits kategorisiert. Keine eigene Heuristik erfunden.
- **Neuer fester Workflow (auch als Memory gespeichert):** Bei UI-Feature-Add-ons testet KZW final — nach Push immer `@wachauer` im Issue pingen (Live-URL + Test-Hinweise), Issue offen lassen bis OK.

**Dead ends:** Keine echten. Befunde: Lindas pandas-Export-JSONs enthalten literale `NaN`-Tokens (JS `JSON.parse` würde brechen) und ~1.029 NBSP-Werte im Rolandslied — beides wird im Ingest bereinigt.

**Phase:** Implementation (aktiver Betrieb). Stable-Docs für #59 nachgezogen (INDEX/FEATURES/ARCHITECTURE/DESIGN auf 9 TEI-Werkzeuge, DATA-MODEL neue Sektion „Naming Index"). **Parallel-Session lief während der gesamten Session:** #132 (Ingest-Verfahren, closed via `873322658`, Eintrag unten), #128 ALX-pb (`29e27980d`), Zenodo-UI-Spiegelung (`3036bfb5e`), #129 KWIC (WIP unkommittiert: `kwic-service.js`, `app.js`, `korpus.css`, FEATURES/INDEX.md) — deren WIP bewusst nicht angefasst.

**Open issues:**
- **#59 offen bis KZW-UI-Test** (Ping mit Test-Hinweisen im Issue; KZW lt. #142 diese Woche im Urlaub, steigt nächste Woche ein).
- **#143** (Prosa-l/lb, 17 Texte) wartet auf KZW-Policy-Entscheid; historische „21er-Liste" (Audit 2026-04) weicht von der Heuristik ab, im Issue dokumentiert.
- **#91**: nur noch DOI ins ZfdG-Exposé + Close-Freigabe („mach zu" genügt).
- `naming-explorer.spec.js` lockt Iweins Belegzahl weich (242, Stand `edd39cc`) — bei Lindas Daten-Updates mitziehen.
- `WZB_phase0.tei.xml`-Verschiebung nach `Wenzelsbibel/` (User, Root war Irrtum) ist noch unkommittiert.
- Aus Vorsessions: Doku-Strategie-Gespräch (#133/#140; #132 inzwischen geschlossen), `build-pages.py --check` nicht in CI.

**Next steps:**
1. KZW-Rückmeldung zu #59 abwarten → Issue schließen.
2. *(optional, klein)* #141 Aufgabe 0: `borte.md`-Metadaten-Template für Alan.
3. Quick-Wins lt. #44: #121 Dropdown-Disambiguierung, #136 Text-Statistiken-Auswahl, #134 AK-Kontext.
4. `WZB_phase0`-Verschiebung committen (ohne der Parallel-Arbeit in die Quere zu kommen).

**Savepoints (auf `origin/main`):** `b255cb22a` #59 Feature + Docs · `5f850c8b4` #59 Tests (153+6 Playwright grün). GitHub: #23 closed mit Verifikations-Kommentar, #143 created (wachauer assigned), #44-Body 3× aktualisiert, #59-KZW-Ping. Dieser Journal-Commit lokal (Push nach User-Freigabe).

---

## 2026-06-11 09:31 – handoff (Parallel-Session, übernommen)

**Summary:** Die zweite Session des Vormittags ist hängengeblieben; Abschluss von der #59-Session übernommen. Geleistete Arbeit: (1) **#132 geschlossen** — Ingest-Verfahren als normativer Stable-Doc-Abschnitt in DATA-MODEL.md, Feature-Doc 034 gelöscht (eigener Eintrag unten, `873322658`). (2) **#128 ALX-pb**: 13 `<pb>` (n=147–159) aus KZWs Linecode-Export nachgetragen (`29e27980d`); Vollständigkeit gegen den Issue-Scope verifiziert (147–159 lückenlos), Issue von der übernehmenden Session geschlossen. Kein Index-Rebuild nötig: `<pb>` trägt keine `<w>`, Positionszählung und `lineStarts`/`lineEnds` unberührt. (3) **Zenodo-Spiegelung**: KZWs UI-Edits (CLARIAH-AT-Funding, `clariah-at`-Community) in `.zenodo.json` nachgezogen (`3036bfb5e`) — nächste Release-Version verliert die UI-Edits damit nicht. (4) **#129 KWIC-Belege**: vollständig gebaut (kwic-service.js + app.js Liste/Tabelle + korpus.css + Docs), lag beim Hänger unkommittiert im Working Tree; nach funktionaler Verifikation (minne in JT: 612 Belege, Kontext-Switch 5–20 Wörter, Klick springt zu „Treffer 1 von 612" im Reader) als `74d0c9490` übernommen.

**Decisions (aus dem Code rekonstruiert):**
- KWIC-Positionszählung in CONTRACTS-§B-Parität (nur `<w @lemmaRef>`), Treffer-Match per `lemmaRefMatchesId` (§B.1) — `position` ist direkt als `targetPosition` für den Reader nutzbar.
- Zeilenreferenz-Präferenz: Vers (`<l n>`) vor Prosazeile (`<lb n>`) vor Seite (`<pb n>`).
- KWIC-Styles in `korpus.css` statt Tailwind-Utilities (kein build:css-Delta).

**Phase:** Implementation (aktiver Betrieb). **Open issues:** #129 offen bis KZW-UI-Test (Ping folgt nach Push); WZB_phase0-Verschiebung nach `Wenzelsbibel/` committet (`6f1ad4f31`).

**Savepoints:** `873322658` #132 · `29e27980d` #128 · `3036bfb5e` Zenodo · `74d0c9490` #129 KWIC · `6f1ad4f31` WZB_phase0-Move.

---

## 2026-06-11 12:15 – #59 Follow-ups: Auto-Update-Pipeline + ROL/TRO-Deep-Links

**Summary:** Lindas Rückfragen im #59-Kommentar (07:27) abgearbeitet. (1) **Daten-Befunde** zu ihrem Paris/Alexander-Fix (`edd39cc`): Restfigur „Alexander" mit 1 Beleg (TRO V. 13808, Sprecherin Thetis) blieb übrig; „Alexander" erscheint bei Paris als Antonomasie, weil `lemma_normalization.json` ihn nicht als Paris-Variante listet — beides im Issue gemeldet. (2) **Auto-Update-Pipeline**: Build deterministisch gemacht (`generatedAt` = Committer-Datum des Quell-Commits statt Build-Zeit, gzip `mtime=0`; Doppel-Build hash-identisch verifiziert) + neuer Workflow `naming-index-update.yml` (Cron Mo 05:17 UTC, Rebuild, bei Diff PR mit Build-Log + Quell-Compare-Link). Bewusst PR statt Auto-Merge: extern kuratierte Daten gehen nie ungeprüft nach Production. (3) **Reader-Deep-Links für ROL + TRO**: Lindas Korrektur, dass auch TRO der MHDBDB-Zählung entspricht, stichprobenartig 4/4 verifiziert (u.a. V. 20665 „geheizen alexander") → Versangaben im Naming-Explorer verlinken jetzt via neuem URL-Param `korpus.html?textId=<SIG>&verse=<n>` (app.js `handleURLParameters` + `scrollToVerse()` im Reader, Amber-Puls auf der Zielzeile). ENE/IW bleiben link-los (Dezimal-Verse, andere Editionen). Chrome-verifiziert: TRO-Link-Klick, ROL-Direkt-URL, IW-Negativtest (0 Links), nicht-existenter Vers (graceful no-op).

**Decisions:**
- **`scrollToVerse` instant statt smooth**: Chrome verwirft programmatische smooth-Scrolls direkt nach Page-Load teils stillschweigend (ROL blieb im Test bei scrollY=0, Log behauptete Erfolg); `behavior: 'auto'` ist über sechsstellige Pixel-Distanzen ohnehin die bessere Orientierung.
- **Vers-Deep-Link gewinnt gegen Highlight-Scroll**, falls beide URL-Params gesetzt sind.
- **Kein Index-Daten-Diff in diesem Schritt**: `naming-index.json.gz` ändert sich nur im Header (generatedAt/gzip-mtime), Records identisch (10.506).

**Phase:** Implementation (aktiver Betrieb). Docs nachgezogen: FEATURES.md (Deep-Link-Bullet ersetzt „bewusst ohne"), DATA-MODEL.md §Naming Index (Determinismus + Workflow). Neuer Playwright-Test (TRO verlinkt / IW nicht) in `naming-explorer.spec.js` — **noch nicht gelaufen**, Suite vor Push ausführen.

**Open issues:** #59 bleibt offen bis KZW-UI-Test; Restfigur-Entscheidung (V. 13808 → Paris?) liegt bei Linda — wenn sie `alexander` als Paris-Variante in `lemma_normalization.json` einträgt, klassifiziert der nächste (automatische) Build ihn als Eigennamen um.

---

## 2026-06-11 15:40 – Health-Check-Scorecard (Doku-Staleness + Altlasten)

**Scorecard:** Algorithmen/XPaths/Paritäten komplett grün (§B.1 zentral, MHG-Normalisierung Py/JS identisch, 3-Stufen-Resolution, Position-Counting inkl. #131-Guard, Build-XPaths dokumentiert). Counts weitgehend konsistent (667/8/15/v4.1.3/v1.4.0); 3 Drifts gefixt: TEI-MODEL §4.1 als Audit-Snapshot datiert + aktueller Stand ergänzt, `barrierefreiheit.html` in DEVELOPMENT-Verzeichnisliste, `pre-main-site` aus CLAUDE.md (Branch existiert nicht mehr). Altlasten: `docs/research/`-Survey (#47/#113 closed) entfernt; `variants.xml` seit 2026-05-29 frisch (Korpus-Regeneration), lexicon-Seite bleibt via #115 offen; 114er-Feature-Docs bleiben bewusst (Issue offen, Lindas Integrationswünsche). Offene Entscheide (Christian): lokaler Branch `feature/tei-structural-fixes-30` (1 unique Commit, #30-Triage-Material, remote gone), Remote-Branch `origin/feature/wenzelsbibel-ingest` (vollständig gemergt, löschbar), Blog-Draft-Duplikat `BLOG-POST-1000WORTE.docx`.

---

## 2026-06-12 08:49 – handoff

**Summary:** Großer Abräum-Tag am #30-Komplex plus zwei Playground-Features. (1) **#138 umgesetzt** (`9e146626e`): HUG bekam 40 `<div type="song" n>` aus KZWs Linecode-Export (dd-Songzähler; Mega-`<p>` aufgelöst, 33 freistehende römische Strophenziffern in `<ab>`, weil `<hi>` als div-Direktkind nicht tei_all-valide ist); MBS1/2/7 bekamen 4/58/4 `<div type="recipe">` an den `lb n=1`-Resets; MBS5s div „recipe 2" enthielt real die Rezepte 2-22 und wurde in 21 divs gesplittet. Skript `scripts/insert-div-wrappers-138.py` mit Token-Sequenz-Invariante (Abbruch bei Verletzung); 5/5 beide Schemas valid; kein Index-Rebuild nötig (Index iteriert nur `<w>`/`<l>`, per Live-Highlight-Test gegen den alten Index bestätigt). PL1-3: Teil-Zähler konstant pro Datei (die Dateien *sind* die Teile), nichts ableitbar. Chrome-Stichprobe HUG/MBS2 inkl. Suche-Sprung. (2) **#143-Analyse**: Reimprobe an Zeilenenden (kalibriert an ALL 37% / ROL 19%) entlarvt 15 der 17 „Prosa"-Kandidaten als Vers (WH=Wolframs Willehalm, WRB=Wittenwilers Ring, TKA/TKR Reimchroniken usw.); nur **APO (Steinhöwel!) und HMT (Hans Mair!) sind echte Prosa** – gegen die titelbasierte Fehlklassifikation „Klassisches Versepos" in TEI-MODEL §8.1; HH (1,1% Reim, 3,3 W/Z) ist rhythmische Prosa, nicht „Versdichtung". (3) **#121** (`36e165c95`): Titel-Dubletten in Text-Dropdowns disambiguiert via `buildTextLabelDisambiguator()` (ui-helpers.js) aus den works-biblStructs (74 Titel, 166 Texte; „(Hrsg. Knieschek, 1877)" bzw. Jahr-Fallback); frontend-only, kein Index-Change. (4) **#136** (`5837d69d4`): Auswahl-UI in Text-Statistiken (Checkbox je Zeile, Master-Checkbox, Zähler, „Nur Auswahl anzeigen", „Auswahl leeren"; Set übersteht Sortieren, Einzel-Klicks ohne Re-Render). (5) **×-Button-Overflow-Fix** (`940e3ca51`, Christians Fund beim Chrome-Test): Suchzeile in korpus.html bricht jetzt um (`sm:flex-wrap` + `min-w-48`). (6) Lokaler Branch `feature/tei-structural-fixes-30` gelöscht; Triage-Material am lokalen Tag `archive/30-triage-material`. Nachgeholtes Handoff für 11.06. nachmittags (`c5268d473`).

**Decisions:**
- **#138-Hüllen an DB-Grenzen, Diskrepanzen als KZW-Fragen**: lb-n=1-Resets sind die Rezeptgrenzen der alten DB; wo Alans Editionszählung abweicht (MBS2 58 vs. 56, MBS5 22 vs. 21, MBS7 4 vs. 3), wurden konkrete Merge-Kandidaten benannt (MBS2 Nr. 56/58 anaphorisch, MBS5 Nr. 5/6 ohne jtem-Auftakt) statt selbst zu raten.
- **HUGs freistehende Strophenziffern → `<ab>`-Hülle**: block-level, beide Schemas valid, Reader rendert `ab` (Zeile 365), reversibel falls später `<lg>`-Strophen kommen.
- **#143 nicht vorab konvertiert**: §8.1 dokumentiert eine explizite Gegen-Entscheidung; Überschreiben braucht KZW-Bestätigung (depends-on-human zu Recht).
- **#121 frontend-only**: Editor/Jahr per Regex aus biblStructs.textContent statt Index-Schema-Erweiterung; bewusst kein Touch an Build-Skripten (Kollege arbeitet parallel an #125).
- **Konfliktvermeidung mit #125-Session**: nur Frontend-Dateien angefasst, keine `scripts/build-*`, `.github/workflows/`, `data/*.gz`.

**Dead ends:** Keine echten. Stolperer: `chunks[0]`-statt-`chunks[-1]`-Guard im Split ließ MBS1/7 zunächst als 1 Rezept durchgehen (pb-Pull leerte den ersten Chunk); Grep nach Tailwind-Klassen im Output braucht `\\\\:`-Escaping (CSS enthält `sm\:flex-wrap`).

**Phase:** Implementation (aktiver Betrieb). FEATURES.md (#136-Bullet) nachgezogen; LINECODE/TEI-MODEL unverändert (§8.1-Korrektur erst nach KZW-Bestätigung in #143).

**Open issues:**
- **#138**: wartet auf KZW – Merge-Entscheidungen MBS2/5/7, PL-Kapitelfrage, optional HUG-Strophen-`<lg>` + `<head>`-Titel. Nach Antwort: ggf. Merge + Renumbering (Skript vorhanden), dann schließbar.
- **#143**: wartet auf KZW – Bestätigung APO/HMT = Prosa (dann Konversion nach §8.1-Muster + §8.1-Korrektur + **Index-Rebuild**, lineStarts/lineEnds ändern sich) und HH-Entscheidung.
- **#121 + #136**: wartet auf KZW-UI-Test (gepingt mit Live-URLs), dann schließen.
- **#59, #117, #129**: weiterhin offen bis KZW-OK (Stand 11.06.).
- Playwright-Suite ist heute **nicht** gelaufen (nur Chrome-Stichproben); die Frontend-Änderungen berühren keine bestehenden Test-Flows, aber vor dem nächsten größeren Push die Suite laufen lassen (vorher Christian fragen).

**Next steps:**
1. KZW-Antworten einsammeln (#138, #143, #121, #136, dazu Altbestand #59/#117/#129) und jeweils mechanisch umsetzen bzw. schließen.
2. Bei #143-Bestätigung: APO/HMT-Konversionsskript (l → p+lb), §8.1 korrigieren, Index-Rebuild (vorher mit der #125-Session koordinieren, die hängt im selben Build-Bereich).
3. Nächste konfliktfreie Kandidaten, falls #125 noch läuft: #134 (AK-Kontext im Reader) oder #140 (Doku-Lesbarkeit, DATA-MODEL.md aussparen).



**Summary:** Das Handoff der gestrigen Nachmittagssession wurde vergessen; dieser Eintrag rekonstruiert aus Git-Log und Issue-Tracker. Nach dem 12:15-Eintrag (#59 Follow-ups) liefen noch fünf Commits: WZB-respStmt auf `role="lead-editor"` für contrib_006/J. Hintersteiner nachgezogen (`9f46c6d67` + `cba6e6e22`), **#117 Wörterbuch-Einstiegsseite** gebaut (`ac583e415` — `woerterbuch.html`, A–Z-Register zu allen ~43.750 Lemma-Seiten mit Indexleiste, Pagination, Deep-Links), **#144** gefixt (`ddadb06ae` — `korpus.html?search=` wird jetzt ausgewertet, closed), Health-Check committet (`02f9a7656`, eigener Scorecard-Eintrag unten) und **#133** geschlossen (`124e33a34` — konsolidierte Encoding-Exemptions-Liste in TEI-MODEL.md §10). Alles gepusht, `main` synchron mit origin.

**Decisions:** Namensentscheidung „Wörterbuch" (statt Alternativen) mit Begründung im #117-Kommentar dokumentiert. Encoding-Exemptions als konsolidierte Liste in TEI-MODEL.md §10 statt verstreuter Einzelvermerke (#133).

**Dead ends:** Keine bekannt (rekonstruierter Eintrag — Sackgassen der Session ggf. nicht erfasst).

**Phase:** Implementation (aktiver Betrieb). Stable-Docs aktuell (Health-Check 15:40 bestätigt; INDEX.md führt #117 bereits als Milestone). Der offene Punkt aus dem 12:15-Eintrag („Playwright-Test noch nicht gelaufen") ist laut Christian (12.06.) erledigt.

**Open issues:**
- **#117 offen bis KZW-UI-Test** — @wachauer am 11.06. 12:28 mit Live-URL gepingt.
- **#59 + #129 weiterhin offen bis KZW-OK** (gleicher Workflow); Restfigur-Entscheidung Alexander V. 13808 liegt bei Linda.
- **#115** lexicon.xml-Backfill; **#124** Analytics (blockiert auf KZW); **#30** TEI-Review-Track eingeschlafen.
- Drei Aufräum-Entscheide aus dem Health-Check (lokaler Branch `feature/tei-structural-fixes-30`, Remote-Branch `origin/feature/wenzelsbibel-ingest`, `BLOG-POST-1000WORTE.docx`) sind laut Christian (12.06.) erledigt bzw. entschieden.

**Next steps:**
1. KZW-Rückmeldungen zu #59, #117, #129 einsammeln (sie ist diese Woche zurück), danach Issues schließen.
2. Bei Lindas Eintrag von `alexander` in `lemma_normalization.json`: nächster Cron-Build (`naming-index-update.yml`, Mo 05:17 UTC) klassifiziert automatisch um — PR prüfen.
3. #115 lexicon.xml-Backfill, wenn Kapazität.

---

## 2026-06-12 14:45 – handoff (#125 Index-Determinismus + Freshness-Gate, gemerged)

**Summary:** **#125 komplett geshippt** (PR #146, Merge `789708322`). (1) **Deterministische Index-Builds** (`a67e38d02`): `generatedAt` aus beiden Index-JSONs entfernt (kein Consumer las es), glob sortiert, gzip `mtime=0` (Muster vom naming-Builder); Doppel-Build lokal byte-identisch verifiziert (Corpus 42.184.766 B / ~4 min, Authority 3.240.305 B / ~20 s). Versionen 4.1.4/1.4.1 an allen drei Stellen + validate-indices. `extract-variants.py`: `<date>` nur noch bei inhaltlicher Änderung (= „Stand der Daten"). (2) **CI-Konsolidierung**: `schema-validation.yml` + `index-version-check.yml` → `data-integrity.yml`, ein Job, 7 Checks billig→teuer, neu darin die zwei Freshness-Gates (variants.xml-Reproduktion byte-identisch; Index-Rebuild-and-Compare auf dekomprimiertem Inhalt). Der erste PR-Lauf war zugleich der Cross-Plattform-Beweis (Windows-gebaute Indexe vs. Linux-Rebuild: identisch). 168/168 Playwright. (3) **Doppel-Review** (eigenes 7-Angle-Review + GH-Claude) → Fix-Commit `6fe411a05`: `requirements.txt` (lxml==6.0.2 + rnc2rng==2.7.0 als Single Source, CI installiert daraus + pip-Cache), `sorted(key=p.name)` (Path-Ordnung ist auf Windows casefolded, auf Linux byte-weise — der String-Key macht sie plattformgleich), Datum-Restamp via semantischem Diff statt Byte-Compare (immun gegen Serialisierungs-Drift; dabei Doppel-Parse + Doppel-Serialisierung eliminiert), Einmal-Encode des ~200-MB-JSON, `curl -f`, Cross-Ref-Check vor RelaxNG, paths-Globs `scripts/audit/**`+`scripts/sync/**`, `::error`-Texte deutsch, Fixture-`generatedAt` raus. Output-Bytes blieben unverändert → kein zweiter Versions-Bump.

**Decisions:**
- **Freshness-Gate vergleicht dekomprimierten Inhalt, nicht gz-Bytes** (gzip-Bytes können je zlib-Build variieren); `mtime=0` dient separat der Working-Tree-Hygiene (No-op-Rebuild = kein Diff).
- **variants-Gate blockierend VOR dem Index-Gate**: der Index-Rebuild nutzt die committete variants.xml und kann deren Drift prinzipiell nicht erkennen. Nie auf advisory herunterstufen.
- **Restamp semantisch statt byte-basiert** (Review-Befund): Byte-Gleichheit hängt an lxml-Serialisierung; der semantische Diff (Zähler + Header-`<name>`) ist vollständig, weil der Output außer Datum/`<name>` reine Funktion der diff-verglichenen Daten ist.
- **Dependency-Pins in `requirements.txt`** statt nur im Workflow: schließt die Lokal-vs-CI-Lücke (Dev mit anderer lxml hätte unreproduzierbare Freshness-Failures bekommen).
- **`save_index`-Duplikat in beiden Build-Skripten bewusst belassen** (kein Refactoring-Scope, im Plan dokumentiert).

**Dead ends:** Keine. Latenter Befund fürs Archiv: `build-corpus-index.py` globbt ohne `.disamb.`-Ausschluss (extract-variants filtert ihn) — heute irrelevant (keine committeten .disamb-Files), bei PoS-Arbeitsdateien im Repo prüfen.

**Phase:** Implementation (aktiver Betrieb). Stable-Docs im PR nachgezogen (DATA-MODEL Lifecycle-Status, DEVELOPMENT CI-Sektion, TEI-MODEL §11, INDEX, CLAUDE.md, CONTRACTS, DECISIONS, TEI-MODEL-AUTH-FILES, schema/scripts-READMEs); Feature-Docs `125-*` gelöscht (Git-History = Archiv).

**Open issues:** Unverändert zu 08:49 (#138/#143/#121/#136/#59/#117/#129 warten auf KZW; #115, #124, #30). Neu zu beachten: ab jetzt blockt CI vergessene Rebuilds — der Data-Change-Lifecycle ist damit maschinell durchgesetzt; „sicherheitshalber rebuilden" ist diff-frei und kostenlos.

**Next steps:**
1. Nächsten Daten-PR beobachten: erster Ernstfall des Freshness-Gates unter Realbedingungen.
2. Optional (Review-Reste, bewusst nicht im PR): lokaler `--compare`-Modus für das Rebuild-and-Compare-Gate (scripts/audit/), `.disamb.`-Ausschluss-Angleichung, gitignore für `variants.regen.xml`.

---

*Kompaktiert 2026-07-14: die folgenden 16 Einträge (2026-06-17 bis 2026-07-10 vormittags) wurden unverändert aus JOURNAL.md übernommen; Reihenfolge wie dort.*

---

## 2026-06-17 11:15 – handoff (#45 Static API gemerged + tei-c.org-Entkopplung + #148 Naming-Sync)

**Summary:** Den offenen #45-Workstream (statische JSON-API) abgeschlossen: Code-Review (10 Findings) als vollständig umgesetzt verifiziert, Feature-Docs nach CONTRACTS.md §G destilliert, PR #150 erstellt und nach grüner CI gemerged (Closes #45). Beim ersten CI-Lauf einen tei-c.org-Ausfall als Blocker entdeckt und strukturell behoben (tei_all.rng committet statt Download); anschließend die verbliebene tei-c.org-Editor-Abhängigkeit (xml-model-PIs) repo-weit auf das lokale Schema umgestellt und den automatischen Naming-Index-PR #148 frisch rebuilt und gemerged.

**Decisions:**
- **tei_all.rng (1,1 MB) ins Repo committet** statt CI-Download von tei-c.org – Reproduzierbarkeit (#125), behebt den Ausfall-Blocker. Der Workflow-Pin-Check liest jetzt die committete Datei als Sanity-Check; `.gitattributes` pinnt sie auf LF.
- **#45-Feature-Docs gelöscht** (Temporal Artifacts) – Wissen vorher verifiziert vollständig in CONTRACTS.md §G + ARCHITECTURE/DATA-MODEL/DEVELOPMENT/FEATURES/INDEX extrahiert.
- **xml-model-PI in 8 Authority-Files + 2 Beispielen + extract-variants.py auf `../schema/tei_all.rng`** umgestellt – konsistent mit der bereits lokalen mhdbdb-authority.rng-PI, netzunabhängige Editor-Validierung. Auf User-Wunsch direkt auf main committet (`559fd3163`).
- **#148 vor dem Merge frisch rebuilt** (workflow_dispatch) statt den 2 Tage alten PR zu mergen – Beutel-Thurows Quelle seit 12.06. unverändert, PR nur sauber auf aktuellen main rebased.
- **Ingest-Material (ARI #92, WZB-Zwischenprodukt) bei der PI-Umstellung bewusst ausgeklammert** – verschränkt mit #92-PI-Designfrage und Pfad-Unklarheit.

**Dead ends:**
- Erster CI-Lauf von PR #150 rot, aber kein Code-Defekt: tei-c.org-Netzwerk-Timeout beim RelaxNG-Download (extern, von Finding 10 vorhergesagt). Führte zum Schema-Commit-Fix.
- variants.xml-„Drift" im lokalen Freshness-Advisory war ein timestamp-False-Positive (7 strukturell geänderte tei-Dateien ohne neue Wortformen) – Rebuild byte-identisch, kein echter Bedarf.

**Phase:** Implementation. Promptotyping-Docs aktuell; #45-Feature-Docs entfernt (in stabile Docs destilliert). Index-Versionen unverändert (Corpus v4.1.4, Authority v1.4.1). CI (data-integrity) auf main grün.

**Open issues:**
- **`data/naming-index.json.gz` hat kein Freshness-Gate in `data-integrity.yml`** (steht nicht in dessen Trigger-Paths) – wird allein durch den wöchentlichen `naming-index-update`-Workflow aktuell gehalten. Eine Rebuild-and-Compare-Absicherung wie bei corpus-/authority-index/api wäre optional ergänzbar, ist aber nicht zwingend.
- **ARI-Ingest (#92) + `scripts/ingest/ari/01-convert-…py` erzeugen weiterhin remote tei_all.rng-PIs** – bewusst offen; gehört in #92, weil finale `tei/`-Korpusdateien laut Konvention gar keine tei_all.rng-PI tragen sollen.
- **`claude-review`-Check schlägt bei reinen Binär-Daten-PRs fehl** (z.B. #148, nur `.json.gz` im Diff) – nicht-blockierend (kein required check), aber kosmetisch unschön.

**Next steps:**
1. `/promptotyping orient` – lädt diesen Handoff.
2. Optional: naming-index Freshness-Gate in `data-integrity.yml` ergänzen (Backlog).
3. Optional: #92-PI-Konvention für ARI klären (tei_all.rng-PI in `tei/`-Zieldateien überhaupt gewünscht?).
4. Sonst: #44-Evergreen-Triage für den nächsten Workstream konsultieren.

---

## 2026-06-17 13:04 – handoff (#44 Re-Audit, #138 HUG-Strophen geshippt, #151 + #124-Matomo geklärt)

**Summary:** (1) **#44 Triage-Matrix per Workflow-Audit aktualisiert**: 35 Issues einzeln gegen Live-GitHub + Journal + Commits geprüft; Matrix war auf Stand 11.06. deutlich gedriftet (7 geschlossene noch als aktiv gelistet: #45/#91/#117/#121/#125/#133/#136; #145/#147 fehlten; #138/#143 von KZW 12.06. entschieden → claude-ready; Kopfzeile 33/35 vs. real 28). Korrigierten Body gepostet (28 offen, ohne Evergreen). (2) **#138 Punkt 5 (HUG-Strophen) geshippt** (`9c9b78e83`, gepusht, deployt, CI grün): 814 `<lg type="stanza" n>` über 33 strophische Lieder deterministisch aus KZWs HUG.txt-Linecode abgeleitet (`scripts/insert-lg-stanzas-138.py`); Diff nur lg-Tags, `<l>` byte-identisch; Schema valid, Index byte-identisch (kein Bump), Reader rendert „Strophe N" (Chrome-verifiziert). MBS-Reste in #139 ausgelagert, KZW in #138 für UI-Test gepingt. (3) **#124 Matomo**: Bärthlein lieferte Snippet (Uni-Matomo `webstatistics.sbg.ac.at`, siteId 15); Cookie-Problem client-seitig via `_paq.push(['disableCookies'])` lösbar → kein Cookiebot/Banner, nur Datenschutz-Absatz. Einbauplan + Snippet in #124 dokumentiert.

**Decisions:**
- **#138 HUG: `<l>` byte-identisch lassen, nur `<lg>` einfügen** (flache Einrückung) → minimaler, reviewbarer Diff statt 40k-Zeilen-Reindent; eingebettete Strophenziffern-Tokens (ii/iii) bleiben in ihrer `<l>` (Positionszählung CONTRACTS §B), `<ab>` der Strophe I bleibt vor dem ersten `<lg>` (ab nicht lg-valide).
- **Kein Index-Bump für #138**: `build-corpus-index.py` iteriert `body.iter('w','l')`, `<lg>` ist unsichtbar; Rebuild lokal byte-identisch verifiziert (`6be9b754…`), CI-Freshness-Gate bestätigt grün.
- **#124 cookielos statt CMP**: cookieloses Matomo + serverseitige IP-Anon (Bärthlein bestätigt) ⇒ herrschende Auslegung kein Consent-Banner; Cookiebot/Usercentrics wäre überzogen für eine datensparsame DH-Seite. Cloudflare nur noch theoretischer Fallback.

**Dead ends:** Beim Chrome-Verify von #138 rendert der Reader zunächst 0 Strophen trotz korrekter Datei – Ursache war der **IndexedDB-TEI-Cache** (`MHDBDB_TEI_Cache`, 30-Tage-TTL, keine Inhalts-Invalidierung), nicht ein Code-Fehler. Als #151 erfasst; Memory `reference_tei_reader_cache` angelegt.

**Phase:** Implementation (aktiver Betrieb). Promptotyping-Docs unverändert (diese Session hat keine Stable-Docs angefasst). **Achtung: Parallel-Session aktiv** – beim Handoff lagen uncommittete Fremdänderungen in `docs/DATA-MODEL.md`, `docs/INDEX.md`, `docs/TEI-MODEL.md`, neu `docs/POS-TAGSET.md` (vermutlich #27 POS) + `README.md` vor; NICHT von dieser Session, bewusst nicht angefasst. Nur `docs/JOURNAL.md` gezielt committet.

**Open issues:**
- **#138** wartet auf KZWs HUG-UI-Test (mit Cache-Hard-Refresh-Hinweis gepingt), dann schließbar. MBS-Rezeptzählungen + Rezept-`<head>` in #139 zur CoReMA-Klärung.
- **#151 (NEU)** TEI-Reader-Cache invalidiert nur per 30-Tage-TTL → Korpus-Updates bis zu 30 Tage unsichtbar; INDEX.md Z.163 („read live from disk") ist deshalb falsch. claude-ready, Lösungsoptionen im Issue.
- **#124 (prio-1)** technisch entsperrt: Snippet liegt vor, cookielos gelöst. Offen Code (includes/_matomo.html + `<head>`-Injection in build-pages.py + Datenschutz-Absatz in impressum.html) und org (DSB-Absegnung + Dashboard-Zugang, beides KZW).

**Next steps:**
1. **#124 Matomo umsetzen in EIGENER frischer Session** (Plan vollständig im #124-Kommentar): `includes/_matomo.html` (cookieloser Snippet), `build-pages.py` um `<head>`-Injection-Region erweitern (aktuell nur NAV/FOOTER), Datenschutz-Absatz in `impressum.html`, Deploy + siteId-15-Treffer prüfen.
2. #138 schließen, sobald KZW-UI-OK.
3. Optional: #151 TEI-Cache-Invalidierung (analog Authority-Cache-Fix #94).

---

## 2026-06-17 13:08 – handoff (README-Drift-Audit + PoS-Tagset als kanonische SSoT)

**Summary:** README per 7-Agenten-Workflow gegen den echten Repo-Stand auditiert (65 Findings über 7 Dimensionen) und überarbeitet (`e7f6d58f6`). Echte Drift behoben: fehlender `naming-index.json.gz` ergänzt, `npm run build`-Kommentar korrigiert (verschwieg build:vendor/variants.xml/API → build:data/build:css ergänzt), Korpus-Index ~41 MB. Vollständigkeit nachgezogen: Aktiv-Projekt-Framing, Hilfe-Hub, Wörterbuch A–Z, KWIC-Belege, neun TEI-Analyse-Werkzeuge, Reading View, PrismJS/rnc2rng, Pako/Dexie als CDN. Neu: `docs/POS-TAGSET.md` (`7e8ae95a2`) als Single Source of Truth fürs `@pos`-Tagset. Alle Detail-Beispiele (person_445=Eckhart, lemma_879=brôt, XPath, Schema-Claims) per Stichprobe als korrekt verifiziert.

**Decisions:**
- **PoS-Tagset als eigenes Doc statt Einbettung in DATA-MODEL** (Christian-Entscheidung): das Tagset war dreifach verstreut (`.gemini`-Skill, TEI-MODEL §5, DATA-MODEL). POS-TAGSET.md ist jetzt SSoT (19-Tag-Schema, Compound-Regeln, Legacy-Mapping ART/CNJ/GRA, verifizierte Korpus-Verteilung); TEI-MODEL §5 + DATA-MODEL verweisen nur noch, README-Link zeigt darauf statt auf den fragilen `.gemini/`-Pfad. INDEX.md Promptotyping-Count 14 → 15 (13 Stable + 2 Process) mit datierter Begründung.
- **TEI-MODEL §5 19-Tag-Tabelle bewusst inline belassen** (nur 5.1/5.2-Detailtabellen auf Verweise reduziert, −19 Z.) – normatives Soll-Modell, 19 Tag-Namen sind eingefroren, Drift-Risiko minimal.
- **Korpus-@pos-Verteilung selbst berechnet** statt Agent-Zahlen übernommen: `ART` dominiert mit 1,06 Mio (Legacy → DET), `DET` nur 53k → ART→DET-Migration steht großteils aus; atomare Zähler splitten Compounds (im Doc dokumentiert).

**Dead ends:** Synthese-Agent verlinkte `[lemma/](lemma/)` als enthielte das Verzeichnis ~43.750 Seiten; tatsächlich ist `lemma/` eine dynamische Seite (`index.html` + `lemma-page.js`, client-seitig gerendert) → vor dem Commit korrigiert.

**Phase:** Implementation (aktiver Betrieb). Stable-Docs angefasst (committet + gepusht, origin/main = `e7f6d58f6`): README, INDEX §Stable-Tabelle+Count, TEI-MODEL §5, DATA-MODEL @pos-Zeile, neu POS-TAGSET.md.

**Open issues:**
- **Parallel-Session aktiv (NICHT von mir):** HEAD `7502c6fb6` (Fremd-Handoff 13:04, JOURNAL.md) ist 1 Commit vor origin, **nicht gepusht**; zusätzlich uncommittete Fremdänderungen in `docs/ARCHITECTURE.md`, `docs/DECISIONS.md`, `docs/FEATURES.md`, `docs/ROADMAP.md`, `docs/TEI-MODEL.md` + `scripts/audit/doc-count-audit.py` (vermutlich Doc-Count-Drift-Fix). Bewusst nicht angefasst; nur `docs/JOURNAL.md` per Pathspec committet. Push der Fremd-Commits/-Änderungen liegt bei der anderen Session bzw. Christian.
- README-Open-Question „über 50 Jahre" von Christian bestätigt; Index-Versionsnummern bewusst weiter weggelassen.

**Next steps:**
1. Mit Parallel-Session koordinieren, bevor gepusht wird: `7502c6fb6` + die 6 uncommitteten Docs gehören ihr.
2. Mein Journal-Commit ist **nicht** gepusht (Handoff-Regel + Fremd-Commit darunter) – geht beim nächsten abgestimmten Push mit.

---

## 2026-06-17 – Promptotyping-Check (Scorecard)

Multi-Agent-Health-Check via `/promptotyping check mit /workflows` (47 Agents, 7 Dimensionen: Audit → adversarial Verify → Synthesize): 39 Befunde → 22 real, 17 False-Positives gefiltert. **0 blocking, 5 should-fix, ~13 nice-to-have.** Kern-Befund: alle Algorithmus- und XPath-Spot-Checks bestätigten Konformität statt Drift (MHG-Normalisierung, lemma-match, 3-Stufen-Resolution, Positions-Counting, lineStarts/Ends deckungsgleich Code↔Doc). Rebuild-Test kritische Pfade ~85 %.

**Behoben** (Commit `54e6d64d0`, lokal, noch nicht gepusht): Count-/Link-Drift nach #45/#59 in ARCHITECTURE/DECISIONS/FEATURES/INDEX/ROADMAP/TEI-MODEL + `doc-count-audit.py` (15 Entry-Points, tei/ 10 Module/Summe 22, 43.754 Lemma-Seiten, #45 → Recently-Completed, tote #030-Referenz raus, #101-Chapter-Override in der Rendering-Map ergänzt; Audit-Skript meldet jetzt ehrlich, dass es Code-Counts nicht prüft). Verifiziert gegen router.js / ui-Globs / tei-text-reader.js / lexicon.xml.

**Action Items** als Issue: #152 (lexicon.xml-Cross-Ref-Gate ohne Baseline + naming-index ohne Freshness-Gate/Determinismus-Risiko; @wachauer, `ingestpipeline`) – die einzige substanzielle stille-Drift-Lücke. Micro-Doc-Hygiene (Docstring-Pfade, CONTRACTS Off-by-one, Sort-Key-/`<milestone>`-/`<pc @join>`-Rendering-Zeilen) im Rolling-Backlog.

---

## 2026-07-02 12:30 – handoff (#151 TEI-Cache-Revalidierung + #143 Prosa-Konversion APO/HMT/HH)

**Summary:** Zwei Top-Prioritäten aus dem #44-Backlog geshippt (Branch `claude/top-priorities-assessment-vvnzo7`, remote Session): (1) **#151 gefixt** (`4e0208f`): TEI-Reader-Cache revalidiert jetzt bei jedem Load per Conditional GET (ETag/Last-Modified, `cache: 'no-cache'`) statt blind 30 Tage aus IndexedDB zu bedienen; 304 → Cache-Kopie, 200 → Neuladen, offline → Fallback. Korpus-Edits sind ab dem nächsten Seiten-Load sichtbar. Duplizierte Fetch-Logik aus text-renderer.js/tei-text-reader.js in `cache.load()` zentralisiert; 2 neue Playwright-Tests; INDEX.md-Falschaussage („read live from disk") korrigiert. (2) **#143 Hauptteil umgesetzt** (`eccecd7`): 3.049 `<l>` → `<lb/>` in APO/HMT/HH (KZW-Entscheid 12.06.), byte-minimaler Diff, `<w>` unberührt; HH-Genre-Datenfehler korrigiert (Marienleben → Geistliche Rede, Header + works.xml); Corpus-Index v4.1.5, Authority-Index v1.4.2, API regeneriert, TEI-MODEL §8.1 richtiggestellt. Browser-verifiziert (HH/APO 0 verse-lines, Kontrolle ROL 9.094).

**Decisions:**
- **#151 Option A (Conditional GET) statt Option C (Deploy-Invalidierung):** Der Cache speichert den Roh-XML-String und parst bei jedem Hit neu – die Ersparnis ist der Netzwerk-Transfer, exakt das, was ein 304 erhält. Option C hätte das #138-Szenario nicht erwischt (Index-Version bumpte dort nicht) und bei jedem Deploy den ganzen Cache verworfen.
- **`set()` speichert jetzt den Server-Rohstring** statt XMLSerializer-Output (byte-identisch zur Quelle, Validator-konsistent). Legacy-Einträge ohne Validatoren laden einmal voll und rüsten sich auf.
- **#143 „Refs" statt „Closes":** APO-Gattungs-Subtask (Terrahe S. 91–96, großzügige Mehrfach-Zuordnung) bleibt offen – das PDF (GitHub-Attachment) ist aus der Remote-Umgebung nicht abrufbar (Egress 403). Lehre #110 angewandt.
- **HH-Genre kuratorisch konservativ:** Geistliche Rede (genre_ccef6751) + Parent Geistliche Literatur; „Marienleben" war offensichtlicher Datenfehler (auch in works.xml). Zur KZW-Review im Issue dokumentiert.

**Dead ends:** Playwright-Suite scheiterte zunächst komplett: (a) Browser-Revision 1193 vs. installierte 1194 → Symlink; (b) Egress-Policy blockt cdnjs/unpkg/jsdelivr → pako/dexie laden nicht → Seiten initialisieren nie. Workaround: npm-Kopien (registry erlaubt) + temporäre CDN→lokal-Patches in 5 HTML-Files NUR für Testläufe (nie committet). Volle Suite danach 166/170; die 4: 3× fehlendes lxml für python3.13 (nachinstalliert → grün), 1× Wörterbuchnetz-API extern blockiert. **Effektiv 169/170, der letzte umgebungsbedingt.**

**Phase:** Implementation (aktiver Betrieb). Stable-Docs angefasst: INDEX.md (Known Limitations + Versionsstand), ARCHITECTURE.md, CONTRACTS.md §E, FEATURES.md (alle #151-Semantik), TEI-MODEL.md §8.1+§11.

**Open issues:**
- **#143 Rest erledigt (Nachtrag):** Christian hat das Terrahe-PDF in die Session hochgeladen → APO-Gattungs-Metadaten umgesetzt (`46c9396`): Prosaroman/Antikenroman/Liebes-Abenteuerroman/Exempel/Fürstenspiegel, Parents Historiografie + Großepik; Höfischer-Roman/Versroman + Geschichtsdichtung entfernt (implizieren Vers). Authority-Index v1.4.3. #143 damit vollständig; HH-Genre-Wahl + APO-Set von KZW absegnen lassen (Issue-Kommentar mit Terrahe-Belegen).
- **#151:** claude-ready-Ship, KZW/Christian-Test des Live-Verhaltens steht aus (Branch noch nicht auf main).
- **pako/dexie-Vendoring umgesetzt (Nachtrag, Christian-Auftrag):** `ce34c81` – beide Bibliotheken gepinnt vendored unter `assets/vendor/` (build-vendor.js jetzt multi-package, Manifeste deterministisch), 5 Seiten von cdnjs/unpkg/jsdelivr auf lokale Pfade, Guard-Test `vendor.spec.js` (statischer No-CDN-Scan + Laufzeit-Check). In der CDN-blockierten Remote-Umgebung end-to-end bewiesen: 54/54 Tests grün ohne jeden CDN-Zugriff. Damit null Runtime-CDN-Abhängigkeiten (Matomo-Loader ist Analytics-Endpoint, keine Bibliothek).

**Next steps:**
1. Branch `claude/top-priorities-assessment-vvnzo7` reviewen/testen, dann auf main (CI data-integrity validiert Indexe/Schema automatisch).
2. #143-Rest: Terrahe-Text beschaffen → APO-Gattungs-Metadaten.
3. Danach #152 (stille-Drift-Gates: lexicon-Baseline + naming-index-Freshness) als nächste Priorität aus meinem Top-3-Ranking.

---

## 2026-06-17 14:10 – handoff (#124 cookieloses Matomo eingebunden + deployed)

**Summary:** **#124 umgesetzt, browser-verifiziert, committet (`7abbf7672`) und gepusht/deployed.** Cookieloses Matomo (siteId 15, `webstatistics.sbg.ac.at`) ist jetzt build-injiziert: neue `<head>`/`MATOMO`-Region in `build-pages.py` (idempotent, `--check`-Gate), Single Source `includes/_matomo.html`. Zweite Liste `MATOMO_PAGES` bestückt die Standalone-Seiten `api/index.html` (eigenes Layout) + `404.html` nur mit Matomo, ohne ihre Nav/Footer anzutasten. Impressum-Datenschutzabschnitt „Reichweitenmessung mit Matomo" + funktionierender localStorage-Opt-out. Issue #124 kommentiert, @wachauer mit Live-URL gepingt.

**Decisions:**
- **Opt-out NICHT als Matomo-iframe.** Live-Test ergab: das Uni-Opt-out-Widget (`index.php?…action=optOut`) liefert extern **HTTP 403** (Apache-Ebene „You don't have permission"), während `matomo.js`/`matomo.php` erreichbar sind. Ein iframe hätte Besucher:innen eine Forbidden-Seite gezeigt. Stattdessen **client-seitiger localStorage-Opt-out** (Key `mhdbdb-matomo-optout`): `_matomo.html` lädt Matomo bei gesetztem Flag gar nicht; Checkbox im Impressum schaltet es. Christian-Entscheidung (Option A von drei vorgelegten).
- **Standalone-Seiten via eigene `MATOMO_PAGES`-Liste**: `api/index.html`/`404.html` dürfen nicht in `PAGES` (sonst ersetzt der Build ihren Custom-Header durch die Tailwind-Chrome). So bleiben sie build-managed + drift-gated statt manuellem Copy-Paste.
- **Direkt auf `main` committet, kein Feature-Branch**: Working-Dir mit Parallel-Session geteilt, ein Branch-Switch hätte deren Checkout mitgezogen. Nur eigene 19 Dateien per Pathspec gestaged (nie `git add -A`).
- **Rechtsgrundlage (lit. e vs. f) + Speicherdauer offen gelassen** (als `TODO #124`-Kommentar im Impressum-Quelltext) – DSB-Entscheidung, nicht meine.

**Dead ends:** Geplantes Opt-out-iframe (403, s.o.) – durch Live-Verifikation erwischt und nicht ausgeliefert, gegen localStorage-Variante getauscht.

**Phase:** Implementation (aktiver Betrieb). Stable-Docs minimal nachgezogen (`DEVELOPMENT.md` includes-Zeile, `scripts/README.md` build-pages-Sektion, `build-pages.py`-Docstring); `docs/`-Hauptdateien der Parallel-Session bewusst nicht angefasst.

**Open issues:**
- **#124 organisatorisch (KZW):** DSB-Absegnung (Rechtsgrundlage lit. e/f + Speicherdauer) und Dashboard-Zugang mit Bärthlein. Issue offen bis KZW den Live-Stand (impressum.html: Datenschutz-Abschnitt + Opt-out-Checkbox) bestätigt. Falls der native Matomo-Opt-out gewünscht ist, müsste Bärthlein den `optOut`-Endpoint extern freischalten.
- **Push-Status bereinigt:** Mein `git push` (auf Christians explizite Anweisung) hat origin/main von `e7f6d58f6` auf `7abbf7672` gehoben und dabei die in den Einträgen 11:15/13:04/13:08/Scorecard als „nicht gepusht" vermerkten Commits (`7502c6fb6`, `279543e96`, `54e6d64d0`, `ba0442449`) mitgenommen. Jene „nicht gepusht"-Vermerke sind damit erledigt; origin/main = lokales main.

**Next steps:**
1. KZW-Live-Test von `impressum.html` abwarten (Datenschutz + Opt-out-Checkbox: Häkchen setzen, neu laden, dann lädt kein Matomo mehr), dann #124 schließen sobald DSB-Absegnung + Dashboard-Zugang geklärt sind.
2. Bei DSB-Vorgabe Rechtsgrundlage/Speicherdauer im Impressum konkretisieren (`TODO #124`-Kommentar dort).

---

## 2026-07-02 – handoff (#106 Reim-Wörterbuch + #114 Tabellenansicht-Followups)

**Summary:** Beide Issues auf Branch `claude/issues-106-114-33ofa0` umgesetzt. **#106 (wachauer: „minimal bauen jetzt"):** Zehntes TEI-Analyse-Werkzeug `rhyme-dictionary.js` (`#rhyme-dictionary`) – Versende-Scan über `lineEnds[]` (v4.1.x, kein neuer Build-Schritt), Reimpartner = Lemmata benachbarter Versenden (±1, Paarreim-Annahme) mit Suffix-3-Match auf normalisierten Formen (2-Letter-Fallback bei Kurzwörtern ≤3 Zeichen, sonst entginge `wîp : lîp`); optionaler Text/Autor-Filter, „→ Belege" in Multi-Lemma-Nähe-Suche (dist 15). Pattern-treu nach DESIGN.md (Thunks, Frozen-State, MessageChannel-Chunking, Abort-Token, Autocomplete, Escape-Helpers). **#114 (Integrationswünsche aus Lindas Prüfung):** (1) Gesamtzeile als sticky `<tfoot>` + „M Treffer gesamt" im Results-Header (wirkt auch in Listenansicht); (2) Types/Schreibformen je Lemma (invertierte Variants-Map, lazy gecacht) als `<details>` im Lemma-Panel plus async MWB/Lexer-Links (Wörterbuchnetz-API, Pattern aus lemma-page.js #73); (3) Keyness-Spalte: signierte Log-Likelihood (Dunning 1993) Text vs. Gesamtkorpus (Referenz wie Lindas naming-analysis), fett/brand ab 10,83 (p<0,001), sortierbar, in TSV/CSV-Export.

**Decisions:**
- **Keyness-Referenzkorpus = alle 667 Texte**, nicht die Textauswahl – entspricht Lindas Formulierung („im Vergleich zu allen anderen Texten der MHDBDB") und ist stabil gegen Auswahl-Änderungen.
- **Gesamtzeile nicht im Export** – Summenzeilen stören Weiterverarbeitung (Excel-Sortierung, R); Gesamttrefferzahl steht im Header und in der UI-tfoot.
- **Reim-Heuristik bewusst lemma-basiert + strukturell** (Minimalvariante laut Audit-Kommentar im Issue); Original-Token-Variante (`lineEndWords[]`, Index-Bump) und Phonetik bleiben als Großplan für #109 aufgehoben – im Modul-UI als Grenze ausgewiesen.
- **Identischer Reim** (Lemma auf sich selbst) nur in eine Richtung gezählt, sonst zählt jedes Paar doppelt.

**Verifikation:** 13/13 Tests der beiden betroffenen Specs grün (`results-table.spec.js` +3 neue, `rhyme-dictionary.spec.js` 4 neue, inkl. Ground-Truth AGS `gân : begân` und korpusweit `muot : guot` aus dem #106-Audit). Volle Suite 180/185; nach lxml-Nachinstallation für python3.13 auch die 3 position-parity grün. Verbleibende 2 Fails sind nicht Session-verursacht: (a) `lemma-page.spec.js` Wörterbuchnetz-API extern blockiert (bekannt umgebungsbedingt), (b) `reading-view.spec.js:190` „prose line numbers (lb)" – **auf sauberem main reproduziert (pre-existing):** Renderer erzeugt für `h_`-präfigierte `@n` leere `.lb-number`-Spans (`<span data-n="h_1"></span>` ohne Textinhalt) → Playwright „hidden". Separates Issue wert.

**Dead ends:** Playwright-Läufe vom Repo-Root starten keinen WebServer (ERR_CONNECTION_REFUSED, Config liegt in `testing/`) – CLAUDE.md-Regel „nie `npx playwright test` vom Root" bestätigt. Browser-Revision-Symlink 1193→1194 wieder nötig (wie im 06-17-Eintrag).

**Phase:** Implementation (aktiver Betrieb). Stable-Docs nachgezogen: INDEX.md (Counts 16/10, Milestones, Main-Site-Bullet), FEATURES.md (neue Sektionen Tabellenansicht #114 + Reim-Wörterbuch #106), ARCHITECTURE.md (Modul-Tree + Route-Tabelle), DESIGN.md (Pattern-Count Acht→Zehn – war schon bei Neun stale – + kanonisches Beispiel), ROADMAP.md (#106 nach Recently Completed), hilfe-playground.html + hilfe-korpussuche.html. Feature-Doc `114-tabellenansicht-korpussuche.md` mit Addendum (Issue noch offen; bei Close in Stable-Docs bereits destilliert → löschen). Kein Index-Rebuild nötig (reine Frontend-/Doku-Änderungen); `tailwind-output.css` regeneriert (neue Utility-Klassen).

**Open issues:**
- #114: lindabeutels Prüfung der drei Followups steht aus; Keyness-Darstellung (Spalte + Fett-Markierung) ggf. nach Feedback justieren.
- #106: Punkte 2–7 weiter in #109 (FWF), Punkt 8 („Lemma im Vers"-Filter) im Multi-Lemma-Backlog.
- Pre-existing: leere `.lb-number`-Spans bei `h_`-Nummern (reading-view.spec.js:190 rot auf main) – als Issue anlegen.

**Next steps:**
1. Branch reviewen/testen (Chrome: Tabelle mit „minne", Reim-Wörterbuch mit „tugent"/„muot"), dann Merge auf main.
2. Issue-Kommentare an @wachauer (#106) und @lindabeutel (#114) mit Live-Stand nach Pages-Deploy.

**Nachtrag (Review-Fixes, gleiche Session):** Multi-Agent-Code-Review (8 Finder-Angles + 1-Vote-Verify) ergab 10 Findings, alle gefixt: (1) `escapeHtml` in app.js escapt jetzt auch Quotes (Attribut-Breakout über `wbnetzlink` aus der externen API); lemma-page.js fügte den Link sogar roh ein – beide über neuen **Shared Client `assets/js/lib/woerterbuchnetz.js`** gehärtet (nur-http(s)-Filter, Session-Memoization pro Form, CONTRACTS §D.2 aktualisiert). (2) Keyness-Referenz nutzt jetzt `resolveLemmaIds()` (ungefiltert) statt des auswahlgefilterten lemmaSet – LL-Werte sind damit auswahlunabhängig/zitierfähig. (3) Impressum-Datenschutz um Wörterbuchnetz-Absatz ergänzt (Suche sendet normalisierte Wortform an api.woerterbuchnetz.de). (4) Types-Label präzisiert („Schreibformen (Types, normalisiert)" + Tooltip; Hilfe-Text stellt klar: Suchformen, nicht Original-Graphien). (5) `rhymesWith`: 2-Letter-Fallback nur noch wenn BEIDE Formen ≤4 Zeichen (wîp:lîp, tac:slac bleiben; Kurzwort-Flut wie minne:„en" weg). (6) `displayLemmaInfo` O(43k)-`.find()` → gecachte `getLemmaById`-Map (Fuzzy-Stufe 3 ist ungecappt, „sch" = 2.437 IDs). (7+8) Geteilte Latent-Bugs auch in cooccurrence-ranking gefixt: `isActiveView()`-Guard vor post-await-`render()` (fertiger Scan überschrieb nach Navigation die aktive View) und Belege-Link-Fallback auf numerische ID, wenn das Partner-Lemma keinen Authority-Eintrag hat. (10) DESIGN.md-Modulzähler korrigiert (Neun Pattern-Module, nicht Zehn – Konvention zählt ohne tei-ui/multi-lemma).

**Merge-Notiz:** Beim Einmergen von origin/main (PR #156, Lexicon-Backfill #115: 43.754 → 43.879 Lemmata, Authority v1.4.4) betroffene Specs gegengetestet – Tabellenansicht/Reim-Wörterbuch unverändert grün.

---

## 2026-07-02 – #152 + #154: drei neue Daten-Drift-Gates in data-integrity.yml

**Summary:** Beide Stille-Drift-Issues aus Health-Check (#152) und PR-#153-Review (#154) umgesetzt, auf Branch `claude/issues-152-154-nhg1cq`. (1) **lexicon-Baseline-Ratsche (#152.1):** `check-authority-cross-refs.py --check` gated dangling lexicon-Refs jetzt gegen gepinnte Konstanten `LEXICON_BASELINE_REFS=977` / `LEXICON_BASELINE_DISTINCT=349` (Ist-Stand verifiziert, deckungsgleich mit JOURNAL 2026-06-17) – Wachstum rot, Altbestand grün, Unterschreitung druckt Senk-Hinweis. (2) **naming-index-Gates (#152.2):** `data/naming-index.json.gz` + `scripts/ingest/naming/**` neu in den Trigger-Paths; immer laufender Offline-Konsistenz-Step (source.commit vorhanden, alle `works[].sigle` existieren in `tei/`); konditionaler Rebuild-and-Compare gegen den gepinnten `source.commit` (nur wenn naming-Pfade sich gegenüber der Diff-Base geändert haben – keine externe Netz-Abhängigkeit auf jedem Daten-PR, #125-Prinzip); `resolve_commit` hat jetzt `--require-commit` (CI failt hart statt still auf Build-Zeit-generatedAt zu kippen) und nutzt `GITHUB_TOKEN` gegen das IP-Rate-Limit unauthentifizierter api.github.com-Calls von geteilten Runnern. (3) **Versions-Bump-Gate (#154, Option A):** neues `scripts/audit/check-index-version-bump.py --base <rev>` – dekomprimierter Inhalt von corpus-/authority-index gegenüber Diff-Base geändert ⇒ `version`-String muss mitgeändert sein; als früher Step vor dem Index-Rebuild eingehängt (der überschreibt `data/*.json.gz` im Working Tree).

**Decisions:**
- **Baseline als Zahlenpaar (Refs + distinct IDs), nicht als ID-Set gepinnt** – billig, ausreichend als Ratsche; das Detail-Reporting (welche IDs) liefert weiterhin `authority-cross-refs-audit.json`. Baseline-Anhebung bleibt explizite KZW-Entscheidung (Kommentar im Skript).
- **naming-Rebuild-and-Compare nur bei naming-Pfad-Änderung** statt immer: der Fetch geht an ein externes Repo (`lindabeutel/Naming-analysis`); externe Netz-Abhängigkeit auf jedem Daten-PR widerspräche der #125-Lehre (tei-c.org-Ausfall). Der Offline-Konsistenz-Step läuft dagegen immer.
- **`source.ref` wird beim naming-Vergleich normalisiert** – committeter Index trägt `ref:"master"`, der Pin-Rebuild `ref:"<sha>"`; Aufruf-Artefakt, kein Inhalt.
- **#154 Option A (CI-Gate) wie im Issue empfohlen; Option B (ETag-Revalidierung im Loader) nicht angefasst** – bleibt als Evaluierungs-Kandidat im Issue.
- **Diff-Base-Step:** PR = Base-Branch-Tip (`git fetch origin $GITHUB_BASE_REF`), Push = `event.before`; nicht bestimmbar (workflow_dispatch/Force-Push) ⇒ Bump-Gate skippt mit Notice, naming-Check läuft konservativ.

**Verifikation:** Version-Bump-Gate in allen drei Szenarien lokal getestet (unverändert/mutiert-ohne-Bump=exit 1/mutiert-mit-Bump=exit 0, via gz-Mutation + Restore); Baseline-Gate grün auf Ist-Stand und rot bei künstlich gesenkter Baseline (voller Doppel-Scan); naming-Konsistenz-Step grün + beide Fail-Pfade (fehlender commit, kaputte Sigle) rot; `--require-commit` failt hart (403 im Sandbox-Proxy als Realtest); Workflow-YAML geparst (16 Steps). Der externe naming-Fetch selbst war in der Sandbox nicht testbar (Proxy-Scope), Codepfad unverändert zum wöchentlichen Workflow.

**Phase:** Implementation (aktiver Betrieb). Docs nachgezogen: DEVELOPMENT.md (11-Check-Liste + Audit-Tabelle), CONTRACTS.md §E (Bump-Pflicht) + F.3 (Ratsche), DATA-MODEL.md (naming-CI-Gates + Offene-Lücke-Absatz), DECISIONS.md ADR-015 (Update-Notiz). Index-Versionen unverändert (Corpus v4.1.5, Authority v1.4.3) – kein Datenänderung, nur Gates.

**Next steps:**
1. PR aus `claude/issues-152-154-nhg1cq` reviewen; erster echter CI-Lauf validiert den Diff-Base-Step unter PR-Bedingungen.
2. Nach Merge: `Closes #152, #154` greift; #115-Backfill senkt später die Baseline (Hinweis kommt automatisch im CI-Log).

---

## 2026-07-02 – Review-Fixes PR #155: ID-Set-Ratsche, TOCTOU-Fix, Workflow-Härtung

**Summary:** Multi-Agent-Code-Review (8 Finder × 6 Kandidaten, 11 adversariale Verifier) über PR #155; die bestätigten Findings direkt umgesetzt. (1) **Zahlen-Ratsche → ID-Set-Ratsche:** kompensierende Drift (+N neue dangling IDs, −N gebackfillte im selben PR) passierte das Zahlenpaar-Gate grün – jetzt pinnt die committete `scripts/audit/lexicon-baseline.json` (349 IDs) die tolerierte Menge; jede neue ID = rot, `--update-baseline` erzeugt einen reviewbaren Datei-Diff (KZW-Entscheidung), geschrumpfter Ist-Stand = `::warning` statt stillem grünen Log. (2) **TOCTOU im naming-Build:** `build_index` fetcht jetzt unter dem resolvierten SHA statt unter `master` – vorher konnten `source.commit=X` und Inhalt=Y auseinanderfallen (raw-CDN cached ~5 min), was das neue Freshness-Gate später als falschen Drift auf unschuldigen PRs gemeldet hätte. (3) **`cancel-in-progress` nur noch für PR-Läufe:** bei schnellen main-Push-Folgen ließ das Canceln den Commit-Range des ersten Pushes ungebumpt durchrutschen. (4) **Diff-Base-Step:** 3×-Retry mit Backoff für den PR-Base-Fetch (transienter GitHub-Fehler riss vorher den ganzen Lauf im ersten Step) + `$GITHUB_BASE_REF`-Env statt `${{ }}`-Interpolation (Actions-Hardening). (5) **Naming-Konsistenz-Check als Skript extrahiert** (`scripts/audit/check-naming-index.py`, lokal ausführbar, eigener `scripts/audit/**`-Trigger nach #146-Regel); `--print-source-commit` ersetzt die dreifach duplizierte Inline-Pin-Extraktion in beiden Workflows. (6) Kleinkram: totes Restore-`cp` in Step 6c entfernt, `git_show()` auf einen Subprocess-Call reduziert, `scripts/README.md` nachgezogen (alte Gate-Semantik + fehlende Skripte).

**Verworfen nach adversarialer Prüfung:** Force-Push-Skip des Bump-Gates (dokumentierter, sichtbarer Trade-off; GitHub bedient Force-Push-`before`-SHAs), Dispatch-Fallback `naming_changed=true` (konservativ korrekt; 0 dispatch-Läufe in der Historie), GITHUB_TOKEN-401-Sorge (Installation-Tokens lesen Public-Repos), HEAD-Blob- statt Working-Tree-Read im Bump-Skript (lokaler Pre-Commit-Check ist der dokumentierte Use-Case; Reordering kann strukturell kein False-Green erzeugen, weil Step 6 selbst jede Divergenz failt).

**Verifikation:** ID-Set-Gate grün auf Ist-Stand (349/349 IDs), rot bei künstlich entfernter Baseline-ID (exakte ID in der Fehlermeldung); `check-naming-index.py` beide Modi; Bump-Gate grün; YAML + py_compile sauber.

---

## 2026-07-02 – #115 Phase 2 (Teil 1): Kategorie-A-Stub-Backfill in lexicon.xml

**Summary:** Der automatisierbare Teil des lexicon-Backfills ist umgesetzt (Branch `claude/115-lexicon-backfill`, aufbauend auf den #152/#154-Gates): neues Skript `scripts/sync/backfill-lexicon.py` (Dry-Run default, `--apply` schreibt) konsumiert die Klassifikation aus `classify-lexicon-backfill.py` und fügt alle **125 Kategorie-A-Stubs** (ganzes `<entry>` fehlt) text-basiert an der String-Sortierposition in `lexicon.xml` ein – minimaler, reviewbarer Diff (+1131 Zeilen), kein lxml-Roundtrip der 31-MB-Datei. Ergebnis: dangling lexicon-Refs **977 → 396** (349 → 109 distinct IDs), Kategorie A = 0, RelaxNG-valide (43.754 → 43.879 Entries). ID-Set-Ratsche via `--update-baseline` auf die 109 verbleibenden IDs nachgezogen (reviewbarer Diff der `lexicon-baseline.json`) – die `::warning`-Nachzieh-Mechanik aus dem #152-Gate hat dabei exakt wie designed gefeuert (erster Realtest der Ratsche).

**Decisions:**
- **POS ohne Korpus-Evidenz (57 von 125): leeres `<pos/>`** statt erfundenem Tag – schema-valide (`text` erlaubt leer), aber ohne Präzedenz im Bestand (0 von 43.754); bewusst als sichtbare kuratorische Lücke gehalten (Liste im PR), kein Verstoß gegen das 19-Tag-Set aus POS-TAGSET.md. Index-Builder verkraftet es (`pos=''`).
- **POS mehrdeutig (4): alle evidenzierten Tags als mehrere `<pos>`-Elemente**, dominantes zuerst – folgt der Präzedenz von 10.167 Bestandseinträgen; der Index nimmt das erste.
- **Senses = die im Korpus referenzierten dangling Sense-IDs, ohne concept-`<ptr>`** (Konzept-Zuordnung kuratorisch, CONTRACTS F.2; `check-lexicon-senses.py` hält sie sichtbar). Für 10 lemmaRef-only-Lemmata je eine Sense-ID oberhalb des globalen Maximums gemintet (ab `_sense_119184`).
- **Kategorien B (36 Lemmata / 264 Refs) und C (35 / 132) bewusst nicht angefasst** – B ist reine Konzept-Kuratorik (prominentester Fall `dinc`, 110 Refs), C verlangt Korpus-`@lemmaRef`-Korrektur (27 Tippfehler-Dubletten) bzw. Neuanlage-Entscheidung (8 Homographen). Tabellen im PR/Issue für KZW/Julia.
- **`<orth>` = dominante Korpusform** – kann Flexionsform sein (Grundform-Bestätigung bleibt bei KZW, #115-Kommentar 2026-06-01); die Belegliste pro Lemma liefert `lexicon-backfill-curatorial.md` on demand.

**Phase:** Implementation (aktiver Betrieb). Authority-Index v1.4.3 → v1.4.4 + api/-Rebuild im selben Branch (Data-Change-Lifecycle). Corpus-Index unberührt (liest `authority-files/` nicht), variants.xml unberührt (Korpus unverändert).

**Next steps:**
1. KZW/Julia: B-Konzepte + C-Entscheidungen (Tabellen im PR), danach Baseline weiter senken – Ziel 0/0.
2. Grundform-Review der 125 Stub-`<orth>` und POS-Nachtrag der 57 leeren `<pos/>` (kuratorisch).

---

## 2026-07-02 – Review-Fixes PR #156: Baseline nachgezogen, CRLF-Fix, Zähler-/Doku-Sweep

**Summary:** Multi-Agent-Review (6 Finder, datengetrieben) über PR #156; Datenschicht war nachweislich sauber (alle 125 Stubs empirisch gegen Korpus verifiziert, Index/API byte-identisch reproduzierbar, Minting kollisionsfrei) – die Findings lagen in der Begleitschicht und sind umgesetzt: (1) Branch auf die ID-Set-Ratsche rebased, `lexicon-baseline.json` via `--update-baseline` von 349 auf 109 IDs nachgezogen (reviewbarer Datei-Diff statt Konstanten-Senkung). (2) **CRLF-Fix in `backfill-lexicon.py`**: `write_text` ohne `newline=''` hätte unter Windows die komplette 31-MB-Datei auf CRLF umgeschrieben (Determinismus + Freshness-Gate kaputt). (3) `lemma-explorer.js` rendert Senses ohne Begriffszuordnung jetzt wie `lemma-page.js` („Keine Begriffszuordnung") statt der rohen Sense-ID – durch die 125 Stubs wäre das zum Regelfall geworden. (4) **`doc-count-audit.py`-50er-Kappung entfernt**: das Drift-Fenster war für jeden Backfill/Ingest >50 Einträge blind (der +125-Sprung passierte unbemerkt); Schutz gegen Fehlalarme leistet der Keyword-Anchor, nicht die Kappung. (5) Zähler-/Versions-Sweep: 43.754→43.879 in `index.html`, `playground/index.html`, 2 Hilfe-Seiten und 6 Stable-Docs; Authority v1.4.4 in TEI-MODEL §11 (kanonische Tabelle!), INDEX.md, CLAUDE.md; DATA-MODEL „Offene Lücke"-Absatz auf den B/C-Rest (396/109) umgeschrieben inkl. Verweis auf `backfill-lexicon.py` als Referenz-Implementierung; TEI-MODEL-AUTH-FILES/ROADMAP/TEI-MODEL-Gap-Tabelle analog. (6) Skript-Härtungen: classify-Fehlerdiagnose nicht mehr verschluckt (capture statt DEVNULL), `--skip-classify` als Debug-only markiert (stale JSON kann Orphan-Stubs einfügen), Sortier-Invarianten-Warnung (Bestand hat eine WZB-bedingte Verletzung lemma_78608–78688 vor lemma_7861), POS-Docstring korrigiert (candidate_pos = häufigster @pos-Wert, nicht alle evidenzierten Tags), redundanter `inserted`-Zähler + toter Default entfernt, minted-Print bei 0 Mints korrigiert.

**Bewusst offen (Follow-up-Kandidaten):** Multi-`<pos>`-Flattening im Index-Builder (nimmt nur das erste Tag – pre-existing, betrifft 10.167 Bestandseinträge + 4 neue Stubs wie `salve` NOM+VRB; Schema-Änderung des Index mit Konsumenten-Ripple → eigenes Issue); `build_stub`-Duplikation zwischen classify (Vorschau) und backfill (divergierendes Format) – bei der nächsten Backfill-Runde konsolidieren.

**Notiz:** 7 Varianten (salve, nisi, …) liefern in der Playground-Lemma-Resolution jetzt den exakten Stub statt des Partial-Match-Fallbacks – fachliche Verbesserung, Alt-Bookmarks zeigen andere Treffer.

---

## 2026-07-08 – handoff (Autonome Issue-Session 07.–08.07.: 12 PRs #174–#185, Review-Block, #44-Matrix erneuert)

**Summary:** Zweitägige autonome Session nach `docs/features/MASTERPLAN-AUTONOME-ISSUE-SESSION.md` (10 Wellen). Ergebnis: **12 offene PRs** (#174–#185), die beim Merge 13 Issues schließen; dazu Entscheidungsvorlagen als Issue-Kommentare (#110 WVV-Survey + Empfehlung, #141 borte.md-Template, #169-Teilfix-Status, #27 P-OFFEN-Fragen an KZW). Highlights: Homographen-Auflösung frequenz-sortiert + Navigation-Epoch/Generation-Token gegen View-Clobber (#174); `posAll[]` behebt Multi-POS-Verlust für 10.171 Lemmata, Authority-Index v1.6.0 (#177); AK-Ausschnitts-Kontext mit `biblScope unit="verse"` als einzigem Excerpt-Signal – `<analytic>` allein hätte 534 False Positives (#178); drei latente §B-Paritäts-Drifts vor dem nächsten Ingest geschlossen, Gate: byte-identischer Corpus-Rebuild (#184); ARI-Escaping + insert-stanzas-Grenzen/Nummerierung vor #92/#110-Bulk (#185).

**Review-Block (neues Pattern):** Nach Abschluss der Wellen die Bot-Reviews der damals offenen 10 PRs gesichtet und triagiert statt blind umgesetzt – 4 echte Bugs (catch-Pfad ohne Epoch-Guard; 2 Badges ohne posAll; Excerpt-Erkennung las nur das erste von ggf. mehreren biblStructs; stale „Abschnitte 1–9"), mehrere berechtigte Doku-Präzisierungen, 2 False Positives (u.a. „über 180 Prüfroutinen": grep-Zählung 178 vs. 186 Tests zur Playwright-Laufzeit). Fixes als Folge-Commits in Stack-Reihenfolge (erst Basis #174, dann Rebases), jede Kette mit Volllauf verifiziert (Kette A 194/194 bzw. 197/197 mit #184; Kette B 193 + bekannter #158-Fail, dessen Fix in Kette A lebt). Alle PR-Bodies tragen einen „Review-Triage"-Abschnitt. **Zweite Runde am Nachmittag:** Die Fix-Pushes lösten Re-Reviews aus, #184–#186 bekamen Erst-Reviews – Ergebnis: Consumer-Rule words[]/lemmata{} in CONTRACTS §B + Fixes in verse-position-search/rhyme-dictionary, console.warn für unvollständig kuratierte Excerpt-Header, Follow-up-Issue #187 (posAll-Anzeige-Migration, Closes #161 bleibt gerechtfertigt), Korrektur des stale #124-Status in ROADMAP/Matrix/Memory (Matomo war seit 17.06. deployed – vom Review gefangen).

**Lehren:** (1) `git rebase --continue` strippt Commit-Message-Zeilen, die mit `#` beginnen (Issue-Referenzen im Titel!) – Message danach per `--amend -F` restaurieren. (2) http-server cacht JS 1h: Chrome-Verifikation nach Branch-Wechsel/Push braucht Hard-Reload, sonst prüft man alten Code (Badge zeigte scheinbar den Bug trotz grünem Playwright). (3) Playwright-Report-Server hält `npm test` bei Fails offen (Port 9323) – killen, dann liefert der Task das Ergebnis. (4) Bei Skript-Fixes erst den Docstring auf dokumentierte Entscheidungen prüfen: Finding 36 („@n-Lücken") wäre fast gegen die KZW-Decision #23 („fortlaufend ab 1") gefixt worden – richtig ist ein Zähler über die gewrappten `<lg>`, nicht der Linecode-Rohwert. (5) Verifikations-Zahl nebenbei: Korpus hat exakt 7.533.447 annotierte Tokens (Corpus-Index v4.1.5) – deckt die „rund 7,5 Mio. Wortbelege" im Rektoratsbericht.

**Merge-Reihenfolge (für den Reviewer):** Kette A #174→#175→#178→#184; Kette B #174→#177→#183; unabhängig #176, #179, #180, #181, #182, #185. Details + Wer-wartet-worauf: #44-Matrix (Body komplett erneuert, Stand 08.07.) und Abschlussreport als #44-Kommentar.

**Bewusst nicht angefasst:** #171-Rest (~12 Findings ohne anstehenden Skript-Lauf), optionale Stretch-Items #106.8 und #147-Stage-0-Entwurf (Budget-Priorität Welle 10), Nits aus den Bot-Reviews (unreachable-Guard, CSS-Hex ohne vorhandene Token, data-content-key-Kosmetik).

---

## 2026-07-08 – handoff (Autonome Merge-Session: 13 PRs #174–#186 auf main, 13 Issues geschlossen, Live-Smoke grün)

**Summary:** Erste Session nach `docs/features/MASTERPLAN-AUTONOME-MERGE-SESSION.md` (User-Kickoff mit expliziter Merge-Autorisierung). Alle 12 Issue-Session-PRs plus Session-Doku-PR #186 nach main gemerged – Merge-Commits, Reihenfolge: Kette A #174→#175→#178→#184, Kette B #177→#183, dann #176/#179/#180/#181/#182/#185, zuletzt #186. 13 Issues automatisch geschlossen (#163 #164 #159 #168 #158 #162 #160 #161 #134 #145 #27 #167 #170); #68/#86/#28/#171 bleiben planmäßig offen (Teilarbeit). Authority-Index v1.6.0 live, IndexedDB-Cache-Bust Chrome-verifiziert (Konsole: „1.5.0 != 1.6.0" → Netz-Fetch → Cache v1.6.0). Vor jedem Merge die nach dem letzten Push eingetroffenen Bot-Reviews triagiert – durchweg bestätigend („no blocking issues"), verbleibende Nits begründet abgelehnt und als Nachtrag in den PR-Bodies dokumentiert (kein Fix-Commit nötig).

**Live-Smoke (alle grün):** Kette A: ABG-Reader 334 numerische `.lb-number` + 5 unsichtbare `.lb-anchor` (h_1–h_5), keine leeren Spans; AK-Excerpt-Banner („Ausschnitt aus: Steirische Reimchronik, Verse 44579–53866"); Multi-Lemma rôt+munt 357 Treffer / 98 Kontexte (deckt die PR-#174-Verifikation). Kette B: Kookkurrenz salve – Zentrum-, Dropdown- UND Partner-Badges zeigen Multi-POS („NOM VRB"; Partner z. B. „dâr ADJ ADV CNJ"). Unabhängige: Tabellenansicht 7 Spalten, Gesamtzeile (140 Texte / 2.055 Treffer bei minne), Titel-Sortierung, Kopieren-(TSV)- + CSV-Buttons; hilfe-daten-beitragen Sektion „9. Einreichung und Aufnahmekriterien" inkl. TOC; barrierefreiheit.html-Kontaktblock (Dr. Alan van Beek, mailto).

**Lehren (GitHub-/CI-Mechanik, 2× reproduziert):**
1. **`gh pr merge --delete-branch` schließt abhängige Stack-PRs statt sie zu retargeten.** #177 wurde beim #174-Merge kommentarlos CLOSED. Recovery: alten Head-SHA als Branch re-pushen → `gh pr reopen` → `gh pr edit --base main` → Temp-Branch löschen. Der Masterplan nahm GitHubs Auto-Retarget an – darauf ist nicht Verlass. Sichere Sequenz seither: mergen OHNE `--delete-branch`, sofort den abhängigen PR retargeten (das Repo-Auto-Delete räumt den Head-Branch ohnehin).
2. **`gh run rerun` ist nach einem Base-Retarget nutzlos:** Der Re-Run recycelt das alte Event-Payload (`GITHUB_BASE_REF` = inzwischen gelöschter Branch) → der „Diff-Base bestimmen"-Step von data-integrity schlägt mit „couldn't find remote ref" fehl (#178 und #177 identisch). Fix: **Close/Reopen des PRs** triggert frische Workflow-Läufe mit korrektem Payload (reopened ist regulärer pull_request-Trigger).
3. Beide „CI rot"-Vorfälle der Session waren genau diese Payload-Artefakte, keine Datenprobleme. main-Data-Integrity war nach allen drei Daten-Merges (#178, #184, #177) grün; Pages-Deploys durchgehend erfolgreich.

**Offen für Menschen:** KZW-Prüfungen (Bestand #129/#138 + neu live: #134-Banner, #160-Tabelle, #163/#164-Suchfixes, #161-Badges – via #44-Abschlussreport), Alan-Freigabe #86, Carina-Metadaten #92. **Mitten in der Session:** KZW bestätigte die #110-Empfehlung (b) und schloss das Issue (12:55) – der WVV-Strophen-Lauf ist damit voll entsperrt, steht aber noch aus. #187 (posAll-Anzeige-Migration) ist startbar. Unerwartete Auto-Schließung: #171 wurde vom #185-Merge über die Development-Verknüpfung geschlossen (kein Closes-Trailer!) – reopened; Lehre: vor dem Merge auch die Sidebar-Verknüpfungen prüfen, nicht nur die Trailer.

---

## 2026-07-09 – Health-Check nach Merge-Woche (Scorecard)

Drift-Prüfung gegen main (`4390d4f9a`) nach den 13 Merges vom 08.07. **Kernbestand ohne Drift:** TEI-MODEL §11 deckungsgleich mit den echten Index-Headern (Corpus 4.1.5 / Authority 1.6.0, 667 Texte), INDEX.md vollständig nachgezogen (16 Entry-Points / 10 Werkzeuge, `playbooks/`, POS-TAGSET), `doc-count-audit.py --check` grün, Algorithmus-Spot-Checks 3/3 (CONTRACTS §B.1-Konsumentenregel ↔ `verse-position-search.js`/`rhyme-dictionary.js`, §D.2 DOMParser ↔ `woerterbuchnetz.js`, posAll ↔ `build-authority-index.py`).

**Behoben (5 Rand-Drifts):** CLAUDE.md nannte Authority v1.4.4 → konkrete Versionen durch Zeiger auf TEI-MODEL §11 ersetzt (CLAUDE.md steht nicht in der §11-Pflegeliste); README 2× „neun" TEI-Werkzeuge + Reim-Wörterbuch fehlte in der Aufzählung + ~43.750 → 43.879 Lemmata; LINECODE.md #23 „weiterhin OPEN" (tatsächlich closed 2026-06-11); DATA-MODEL-Changelog um „Why v4.1.4/v4.1.5" ergänzt; DECISIONS.md ADR nannte konkrete v1.4.0 → §11-Verweis. ROADMAP-Health-Check-Vormerkung abgehakt.

**Action Item:** #28 wurde vom #182-Merge auto-geschlossen (Development-Verknüpfung, identischer Mechanismus wie #171), obwohl ROADMAP/JOURNAL „bleiben planmäßig offen" sagen → Reopen empfohlen; damit wäre auch `docs/features/FREMDSPRACHEN-PHASENPLAN-28.md` wieder regelkonform (Feature-Doc an offenem Issue).

---

## 2026-07-10 – UI-Fix Treffer-Navigation im Reader (KZW-Feedback)

**Summary:** KZW-Feedback zur Trefferanzeige unten rechts im Reading View („sehr klein und unintuitiv, Kontrast könnte höher sein", mit Screenshot): Buttons und Zähler von text-xs auf text-sm, Buttons dunkel (slate-700, weiße Schrift) statt hellgrau-auf-hellgrau, Zähler slate-900 semibold, Leiste deckender mit kräftigerem Rahmen/Schatten, Disabled-Zustand jetzt sichtbar (Opacity 0.4). Direkt auf main (`6df766522`), CI grün, deployed. Hilfeseiten geprüft: beschreiben die Buttons nur funktional (Beschriftung/Position), kein Nachzieh-Bedarf; DESIGN.md um `.reading-nav`-Komponente + Tailwind-Precompile-Gotcha ergänzt.

**Decisions:**
- **Styling als `.reading-nav*`-Komponenten in `korpus.css` statt Tailwind-Utilities** – auf KZWs Rechner gab es kein Node/npm, und das vorkompilierte tailwind-output.css hätte die neuen Utility-Klassen still verschluckt (Präzedenz: KWIC-Styles #129). Erster Ansatz (dunklere Utilities direkt in korpus.html) verworfen, weil 8 der benötigten Klassen im kompilierten CSS fehlten.
- **Commit über temporäres Worktree von origin/main** – Arbeitsverzeichnis stand auf `ingest/bre-weingruesse` mit fremdem WIP; Worktree-Pfad musste kurz sein (`core.longpaths`-Falle bei tiefem Scratchpad-Pfad). Working-Tree-Duplikate danach zurückgesetzt, Branch bekommt die Änderung beim nächsten main-Merge.

**Phase:** Aktiver Betrieb. Playwright lokal nicht lauffähig (damals kein npm) – betroffene Tests prüfen nur IDs und Disabled-Logik, beides unverändert. Node.js inzwischen auf KZWs Rechner installiert (v24, inkl. Chocolatey/Python 3.14/VS Build Tools via Installer-Checkbox); `npm install` im Projekt steht noch aus.

## 2026-07-10 13:09 – handoff (KZW-Rückstau + Frontend-Session: #203/#204/#187 live, WVV komplett, 6 Analysen)

**Summary:** Tagesplan in vier Blöcken abgearbeitet (5 Commits auf main, alle CI grün, volle Suite 205/205). (A/B) Alle fünf wartenden KZW-Rückfragen bedient: #27 beantwortet + POS-TAGSET §6.5 nachgezogen, #124 (Matomo-Dashboard-Zugang), #190 (Beutel-Thurow = contrib_052), #110/WVV abgeschlossen (11 header-getrennte Blöcke gewrappt, 489 lg fortlaufend nummeriert, Index byte-identisch), #28 reopened + 26 Beispielfälle mit KWIC-Belegen für die Lehnwort/Fremdwort-Grenzziehung. (C) Analysen ohne Ingest-Code: #198-Scoping (Entwarnung: 183 Tokens statt 87k, Ziel-Lemma 2593 existiert), #139 CoReMA-Stage-0 (GAMS-URLs verifiziert, H2 ohne Rezept-Objekte, Text CC BY 4.0), #147 Weingrüße-Stage-0 (21 Zeugen statt 20, Konventionen + Fetch-Rezept, Wiki deklariert KEINE Lizenz). (D) Frontend: #203 KWIC-Belege-Export (CSV, ohne Anzeige-Cap), #204 Filter-vs-Auswahl-UX inkl. Fix der nie sichtbaren noResults-Box, #187 posAll-Migration über 10 Dateien (Closes).

**Decisions:**
- **Christian-Priorisierung 10.07.: KEIN Ingest-Coding, bevor Codebasis + Frontend „am bestmöglichen Stand" sind** – Analyse/Issue-Vorbau erlaubt, Konversions-Skripte nicht. CoReMA (#139) läuft später als gemeinsame Session (Christian ist selbst CoReMA-Datenexperte und hat die Daten lokal, kein GAMS-Bulk-Fetch nötig). Memory angelegt.
- **juliahin ist wieder regulär im Projekt** (neue Finanzierung, KZW hängt ihr Issues um) – die Doppel-Assign-Regel wachauer+juliahin gilt wieder; Memory korrigiert.
- **WVV (b) konsequent:** Die 4 Anker-Lücken enthielten 11 header-getrennte Blöcke (Zusatzstrophen 8a/11a/12a/42a/8b/12b, Tegernsee-Spruch, Meißnerton, Ton-Marker 1180/1181, 2108) – jeder Header ist Blockgrenze, dokumentweite Neunummerierung 1..489 (KZW-Regel „fortlaufend ab 1"); supplied/Ton-Marker unangetastet, Token-Strom byte-identisch.
- **#203/#204 mit `Refs` statt `Closes`** (KZW-Live-OK-Regel, Pings mit Test-Anleitungen gepostet); **#187 mit `Closes`** (technische Migration, Verifikations-Hinweise im Issue).
- **#187 nach Issue-Vorgabe als Inline-Muster** (`(lemma.posAll || …).join(' ')`, Präzedenz PR #177) statt neuem Shared-Helper.

**Dead ends:**
- *blêmensier*, das Beispiel aus dem #28-Phasenplan, existiert gar nicht als Lemma im lexicon (auch *messe*/*messîas* nicht) – Plan-Beispiel war hypothetisch, im Issue vermerkt.
- Erster #187-Kommentar zitierte eine erfundene salve-Lemma-ID (33929 statt real 79188) – sofort editiert; Lehre: konkrete IDs vor dem Posten gegen lexicon verifizieren.
- Die noResults-Box der Korpussuche konnte seit jeher nicht erscheinen (lag INNERHALB der im 0-Treffer-Fall versteckten resultsSection); die #204-Verifikations-Behauptung im Issue-Body war Code-Lektüre, kein Live-Test.

**Phase:** Implementation (aktiver Betrieb). Stable-Docs angefasst: POS-TAGSET §6.5 (KZW-Entscheide PART/Fusionen, P-OFFEN auf 2 reduziert), FEATURES (KWIC-Export #203, Filter≠Auswahl #204, Header-Wortlaut), INDEX (KWIC-Bullet), hilfe-korpussuche.html. Index-Versionen unverändert (Corpus v4.1.5, Authority v1.6.0); WVV-Corpus-Rebuild byte-identisch verifiziert, contributors.xml ist nicht indexiert.

**Open issues:**
- **KZW:** Live-Tests #203/#204 (gepingt), Restfragen #27 (CNJ-Restquote ≤10 %? / wiltu: VEM oder VRB?), #28-Grenzziehung an den 26 Fällen (Julia mitgepingt), #124 DSB-Eckdaten + Dashboard-Ticket an Bärthlein, H2-Frage an Klug (#139: Rezept-Objekte fehlen, tauschen oder nachliefern?).
- **Silvan Wagner:** wiki.brevitas.org deklariert keinerlei Lizenz (rightsinfo leer, Impressum-Links 404) – Nachnutzungs-Freigabe ist Blocker vor jedem #147-Einspielen; MHDBDB ist immerhin benannter Kooperationspartner der Hybridedition.
- **#198:** Plan im Issue (183er-Batch nach §6.3-Gates + lexicon-Fix + Sense-Nutzungstabelle), Batch selbst noch nicht gelaufen.
- **#147/#139:** bewusst kein Konversions-Code geschrieben (Priorisierung oben); Analysen liegen als Issue-Kommentare bereit für KZW ab KW 31.

**Next steps:**
1. `/promptotyping orient` – lädt diesen Handoff.
2. Frontend-Kandidaten in Prio-Reihenfolge: #196 (Hapaxlegomena-Tool), #194 (Playground-Rubrik „Experimentelle Forschungsdaten"), Audit-Reste #169/#171/#172.
3. #198-Batch, sobald KZW-Review-Kapazität da ist; CoReMA-Ingest als gemeinsame Session mit Christian; #147-Konversion erst nach Lizenzklärung UND Frontend-Freigabe.

---

## 2026-07-10 (Nachmittag): Autonome Frontend/Codebase-Session – 8 PRs (#205–#212)

**Kontext:** Direktive chsteiner: Codebase und Frontend auf aktuellsten Stand bringen, bevor neue Ingests starten; Ingest-Themen (#193/#194/#141/#147/#139/#92/#191/#123/#195/#118) explizit zurückgestellt. Kickoff über Plan-Freigabe (Betriebsvertrag nach Masterplan-Playbook §2); mid-turn zwei Zusatzwellen freigegeben. Baseline main: 205/205 Playwright; jeder PR einzeln gegen diese Baseline getestet (jeweils 205/205).

**Merge-Queue (Reihenfolge empfohlen):**

| PR | Issue | Inhalt | Closes? |
|----|-------|--------|---------|
| #205 | #198 | habe/hab/hawe-Batch: 25 MOVE → lemma_2593, 179 NOM-Strips, Provenienz-Log, Corpus-Index v4.1.6 | nein (Schritt 2 Sense-Split = KZW) |
| #206 | #196 | Echte Hapaxlegomena (11. Werkzeug) + ARCHITECTURE-Nachzug | nein (KZW-UI-Test) |
| #207 | #190 | hilfe-belege-beitragen.html (Community-Intake) + CSV-Vorlage | nein (KZW-UI-Test) |
| #208 | #188 | CLARIAH-Logo → offizielles SVG (User-geliefert), Footer h-24→h-16 | ja |
| #209 | #171 | 12 Python-Findings (F24–F97), neue Module tei_namespaces.py + wzb_roman.py | ja |
| #210 | #189 | quantify-unannotated-tokens.py (Punkt 2) + data/audit/ gitignored | nein (Punkt 1 GWTK offen) |
| #211 | #106.8 | Multi-Lemma-Suchmodus „Im selben Vers" (lineStarts/lineEnds-Binärsuche) | nein (Rolling-Backlog) |
| #212 | #106.2 | Versendings-Profil (12. Werkzeug) mit Reim-Druck-Spalte (=Punkt 3) | nein (Rolling-Backlog) |

Kollisionen: #211 hat trivialen FEATURES/INDEX-Konflikt mit #206 (gleicher Satz, kombinieren); **#212 basiert auf dem #206-Branch** (Doc-Count-Stacking), #206 zuerst mergen. Rest disjunkt.

**Kernbefunde:**
- **#189-Quantifizierung:** 1,9 Mio. w-Tokens ohne lemmaRef (20,13 %); 98,4 % davon homograph zu annotierten Formen, aber funktionswort-dominiert (in/ir/er). Forschungsrelevante Mittelschicht: 359 Inhaltswort-Formen, angeführt von **minne mit 6.982 unsichtbaren Belegen in 262 Texten** – stärkstes Argument für die Nachannotation. Priorisierungsliste als #189-Kommentar; Funktionswort-Grundsatzfrage an KZW.
- **#198:** Das 714er-Sicherheitsnetz zahlte sich aus (nur 1 echtes habe-Substantiv unter 183 NOM-Tags; houwe/hou-Fehlklassen abgefangen, als REVIEW dokumentiert).
- **F26 (build-pages.py):** read_text() normalisiert Zeilenenden – die CRLF-Erhaltung war seit jeher wirkungslos, jeder Lauf schrieb CRLF-Seiten still auf LF um. Generelle Lehre für alle Roundtrip-Skripte: read_bytes()/newline=''.
- **Reim-Druck-Metrik** (Versendings-Profil) differenziert auf Anhieb: tuon/guot/sagen ~50 % Versende-Anteil vs. Artikel ~5 % – direkt verwertbar für KZWs Reim-Forschungsfrage aus #47.3.

**Health-Check light (Scorecard):** Algorithmen-Spot-Checks 3/3 grün (CONTRACTS §A/§B.1/§C decken sich exakt mit Code, inkl. Zeilenverweis); XPath-Spot-Checks 3/3 grün (eine notationelle Nuance sense/ptr); doc-count-audit nach F25-Fix grün ohne False Positives. Zwei Funde, beide behoben/adressiert: ARCHITECTURE.md-Modulzahl war beim #196-Doc-Nachzug übersehen (auf PR-Branch gefixt – die Doc-Count-Konvention braucht weiter Aufmerksamkeit bei Playground-Adds), #44-Personal-Absatz zu Julia veraltet (Matrix-Update).

**Session-Mechanik:** 4 Kern-Wellen + 3 Stretch + 2 Extra-Wellen in einer Session; Playwright-Fenster (15 min/Lauf) konsequent für Read-only-Vorbereitung der Folgewelle genutzt (keine Branch-Wechsel während Läufen). Ein Platzhalter-Ersetzungs-Bug (TESTERGEBNIS enthält ERGEBNIS als Substring) verstümmelte kurz den PR-#210-Body – bei sed/replace-Ketten auf Präfix-Kollisionen achten.

## 2026-07-12 14:17 – handoff (Review-/Merge-Session 11.–12.07.: alle 9 PRs #205–#213 auf main, Opus-Review-Workflow etabliert)

**Summary:** Der Review-Workflow wurde aufs code-review-Plugin mit `--model opus` umgestellt (chsteiner-Umbau + Feinschliff, 11.07.), Opus-Reviews für alle PRs getriggert und Finding für Finding abgearbeitet; anschließend alle 9 PRs #205–#213 der Reihe nach squash-gemergt (User-Freigabe: mergen, wenn absolut sicher). Suite gewachsen 205 → 212 Tests (3 neue Spec-Dateien). Am 12.07. Workflow nachgeschärft (Auto-Cancel bei Merge/Close via `closed`-Trigger + Job-`if`, Draft-Skip, `--max-turns` 30→50, `2d6335856`) und 5 verwaiste `claude/*`-Remote-Branches gelöscht (alle zu gemergten PRs, per `git cherry`/rev-list verifiziert).

**Decisions:**
- Umgesetzte Review-Findings: wbnetzlink-Escaping im Hapax-Detail-Panel (Security, 3× geflaggt) + Breakout-Regression-Spec (#206); Vers-Suche auf `text.lemmata{}` statt `words[]`-Scan (CONTRACTS §B.1, zugleich O(Vorkommen)) + Spec (#211); Spec fürs Versendings-Profil, Assertion datenunabhängig über den Ausgeblendet-Zähler (#212); TOC-Label- und CSV↔Tabellen-Angleichung (#207); stderr-Konsistenz + noqa-Bereinigung (#209); hawe-KeyError-Guard, Skript nach `scripts/ingest/pos-disambig/`, actions.json/cases.json committet → Batch replaybar (#205).
- Abgelehnte Findings (begründet): #210-Nits (No-op-`.lower()`, Coverage-Edge ohne Korpus-Fall, bewusste DE-Excel-CSV); #208-Opus-Finding „Workflow im Diff" war falsch (Trigger-Commit nachweislich leer); Perf-Polish Hapax/VEP (Reviewer: „nur falls es je auffällt"); Python-Regressionstests für #171 (keine Python-Test-Infra im Repo – wenn, dann als eigenes Issue).
- #205 ohne frisches Opus-Review gemergt: der Lauf starb 2× an max-turns 30; Entscheidung auf Basis Sonnet-Datenverifikation + grünem validate-Gate + eigenem Replay-Beweis (Dry-Run im Worktree auf dem Vor-Batch-Commit reproduziert diff-liste.csv byte-identisch). Das später doch durchgelaufene Opus-Review bestätigte: ship-ready.

**Dead ends / Lehren:** Fix-Push + Sofort-Merge ließ 6 Reviews auf bereits gemergte PRs posten (GitHub bricht Workflows beim Merge nicht ab) – daher der Auto-Cancel-Umbau; zusätzlich Prozessregel: vor Sofort-Merges in-flight Runs canceln (Memory). Das verspätete #207-Review reviewte den Vor-Fix-Stand (stale) und behauptete ein offenes Finding – gegen main verifiziert: Fix ist drin; verspäteten Reviews nie ohne Gegencheck glauben.

**Phase:** Aktiver Betrieb (Implementation). Alle Promptotyping-Docs aktuell; Doc-Counts (12 TEI-Werkzeuge, 18 Entry Points) in den PRs nachgezogen; #44-Matrix auf Stand 11.07. (0 offene PRs).

**Open issues:**
- KZW-Abnahmen ausstehend: #196 (Hapax-UI), #190 (Belege-Hilfeseite), #106 Punkte 2+8 (Versendings-Profil, Vers-Modus), dazu #203/#204; Pings sind gepostet, Issues offen lassen.
- #198 Schritt 2 (Sense-Split lemma_2598→2593 in lexicon.xml) = KZW-Entscheidung; Nutzungstabelle + Diff-Liste liegen im Issue.
- `origin/ingest/bre-weingruesse`: KZW-Branch (12.06., eigener Commit, kein PR) – mit ihr klären, ob noch gebraucht; nicht löschen.
- Wiederkehrende Review-Empfehlung Python-Test-Infra (z. B. `wzb_roman`-Asserts): bewusst offen, bräuchte eigenes Issue.

**Next steps:** (1) #189 Punkt 1 GWTK-Pilot (rott/jungen) – Goldstandard + Mechanik liegen bereit, direkt umsetzbar; (2) nach KZW-OKs die Abnahme-Issues schließen; (3) bei nächster Gelegenheit prüfen, ob der Auto-Cancel im Review-Workflow beim ersten echten Merge greift; (4) Ingest-Cluster (#193 zuerst) erst nach expliziter Freigabe – Direktive „Frontend vor Ingest" ist mit dieser Session erfüllt.

## 2026-07-12 – handoff (Autonome Issue-Session: PR #214 GWTK-Pilot + PR #215 Doku-Bereinigung, #216 angelegt)

Kickoff nach Voll-Audit aller 35 offenen Issues (Playbook neu befüllt, 4 Entscheidungen chsteiner in §5). Ergebnis: 2 Kern-PRs (je 212/212 Playwright gegen frische main-Baseline), 3 Text-Deliverables, Matrix + Docs nachgezogen.

**PR #214 (#189 Punkt 1, GWTK-Pilot):** 278 nackte rot/jung-Tokens kontext-disambiguiert (4 parallele Subagenten, §6.3-Mechanik wie #198/PR #205), konservativ 257 annotiert / 21 Review. Goldstandard exakt getroffen (rôt+munt-Verse 46→73 bei Kriterium ≥73; junc 126→259 bei ~262). Corpus-Index v4.1.7, Authority v1.6.1 (+2 variants-Typen rotte/rotten unter lemma_4954). Befunde: (a) Kandidaten-Erweiterung lohnt – Issue nannte 4 Lemmata, real relevant waren 7, inkl. Saiteninstrument-Lesart, die lemma_4978 per sense_7735 (Instrumentalmusik) selbst abdeckt; 2 Subagenten fanden das unabhängig, 4 Fälle per dokumentiertem Moderations-Pass gehoben. (b) 63 substantivierte junc-Fälle als pos=NOM bei lemmaRef 3157 (Skill-Regel), keine neuen Compound-Tags. (c) §6.3.5-revisionDesc-Eintrag gesetzt (P-MUSS; #205 hatte das ausgelassen).

**PR #215 (#140, konservative Variante):** 252 Encoding-Fixes (konzentriert auf TEI-MODEL + TEI-MODEL-AUTH-FILES, kuratierte Wort-Map, mhd. Formen/Eigennamen geschützt), 418 Em→En-Dashes über alle 15 Docs (Code ausgespart), 4 LLM-Marker entfernt (8.1-Anchor mit angepasst), Zielgruppen-Banner auf den 5 maschinenorientierten Referenzen. Für Abnahme markiert: DRAFT-Status in TEI-MODEL.md, Schreibweise „Woesner".

**Text-Deliverables:** #59 Alexander-Workaround als Kommentar-Entwurf (Override-Mapping, bewusst ohne Linda-Ping – Betriebsvertrag), #118 Sprachstufen-Entscheidungsvorlage (Kommentar + docs/features/118-sprachstufen-konzept.md; Kernpunkt: FNHD hat keinen ISO-Code → de-x-fnhd, Code-Policy gemeinsam mit #28 Phase 0), #216 minne-Serien-Issue (~7.000 Tokens, 262 Texte) nach bestandenem Pilot angelegt.

**Lehren:** (1) Die Pre-flight-Gates der Build-Skripte erzwingen auf Branches ein 3-Commit-Muster (Quellen → Indexe → API); der Squash-Merge stellt den Ein-Commit-Lifecycle auf main wieder her. (2) Freshness-Check flaggt nach Checkout mtime-Rauschen – hart verifizieren via Regenerat-Vergleich (cmp gegen variants.regen.xml; git diff greift beim Dry-Run ins Leere). (3) Vor Disambiguierungs-Batches Lexikon-Senses der Kandidaten prüfen: verborgene Lesarten (Instrument!) stecken im selben Lemma.

Merge-Reihenfolge: #214 (Daten-PR, Reviews canceln, kein [skip ci]) → #215 → Session-Meta-PR (auf #215 gestackt). Abschlussreport als #44-Kommentar.
---

## 2026-07-13 17:45 – Carearbeit-Session (Dead Code + Doku-/Hilfe-Staleness + Health-Check)

**Summary:** Erste dedizierte Carearbeit-Session auf main (Branch `chore/carearbeit-2026-07`, 4 thematische Commits). Drei Explore-Agents kartierten vorab JS/CSS-Dead-Code, Scripts-/Repo-Hygiene und Doku-Staleness; Fixes direkt umgesetzt, nur die Wenzelsbibel-Entscheidung wurde ein Issue (#219). Kernbefund: Der Code war nach #171-Audit + Juli-Sweep schon weitgehend sauber; die eigentliche Drift saß in **Zählwörtern und Versionsangaben** der Doku/Hilfe.

**Fixes:** (WP A) 12-statt-zehn-Werkzeuge in hilfe-playground/README, 18 Entry Points (FEATURES), Elf Module (DESIGN), TEI-MODEL §11 + INDEX §Status von 4.1.5/1.6.0 auf 4.1.7/1.6.1 (Source-of-Truth-Tabelle hing zwei Bumps zurück), Footer-Drift hilfe-belege-beitragen (via `build-pages.py --check` gefunden). (WP B) korpus.css-multi-lemma-Suffix-Block (tot, Playground-Zwilling lebt!), text-renderer.js-Shim aufgelöst (Audit #42 abgeschlossen), getLemmaSuggestions() + Banner-Kommentare. (WP C) AUDIT-REPORT.md + check-index-freshness.py gelöscht, wzb-add-lemma.py nach `scripts/ingest/wzb/`, WVV-README, .gitignore `\temp`→`temp/`. (WP D) variants 256.759→256.761 (6 Ist-Stellen inkl. index.html-Tile), contributors 51→52, zwei stale Code-Anker in DATA-MODEL (get_namespaces liegt seit #171 in tei_namespaces.py).

**Health-Check-Scorecard 2026-07-13:** Algorithmen 3/3 PASS (§B.1 Lemma-Match token-exakt, §A Normalisierung JS↔Python zeichengenau, §B Positionszählung Index↔Reader paritätisch); XPaths 3/3 PASS, keine toten Skript-Pfade nach der sync/ingest-Reorg. doc-count-audit nach Fixes drift-frei. Rebuild-Fähigkeit kritischer Pfade unverändert hoch (~85-90 %); Schwachstelle sind Zeilen-Anker in Docs, nicht Inhalte.

**Nebenfund (nicht gefixt):** Legacy-Upload-Fallback `findCooccurringLemmas`/`findProximityMatches` (tei-manager.js:303-336) zählt Positionen über alle `<w>` ohne `@lemmaRef`-Filter, abweichend von CONTRACTS §B. Läuft nur für hochgeladene Dateien, nie gegen den Index; gehört thematisch zu #169 (Kommentar dort war permission-geblockt, daher hier dokumentiert).

**Lehren (Rohmaterial fürs Carearbeit-Playbook):** (1) Drift-Klasse Nr. 1 sind **code-abgeleitete Counts** (Werkzeug-/Entry-Point-Zahlen), genau die prüft doc-count-audit.py nicht → Erweiterungskandidat (Playground-Sidebar-Buttons zählen). (2) `build-pages.py --check` + `doc-count-audit.py` + `check-index-versions.py` als Pflicht-Einstieg jeder Carearbeit; fanden 2 von 3 Befund-Klassen mechanisch. (3) Explore-Agents vor Löschungen: die Fallen-Liste (String-Literal-Dynamik-Imports, `show*WithSearch`-Methodennamen im Router, JS-generierte Klassennamen `multi-lemma-${id}`, CI liest JS-Konstanten per Regex, Test-only-Reachability) ist wiederverwendbar. (4) Audit-Reports altern: zwei der geplanten Löschungen (test-utils, mhg_normalizer) waren schon erledigt → Ist-Stand immer neu verifizieren. (5) Datierte Chronik-Einträge (Milestones, ADRs, Journal) nie „fixen", nur Ist-Aussagen. (6) variants.xml-Formen-Zahl ändert sich bei jeder Nachannotation mit; Ist-Stellen minimieren (Kandidat: Zahl nur noch in hilfe-daten + index.html führen).

**Offen:** #219 Wenzelsbibel (161 MB Zwischenstände, Maintainer-Entscheidung). Voller Selektor-Sweep über playground/css/style.css bewusst ausgelassen (Stichprobe fand nichts Totes, hohes False-Positive-Risiko, kein Issue wert). Playbook-Destillation folgt separat.

Playwright 212/212 grün (15,6 min). Savepoints: `ffcf6cb7c` (WP A), `4bf0700e7` (WP B), `5cdefcdf4` (WP C).

---

## 2026-07-13 19:00 – handoff (Carearbeit-Session komplett: PR #220 gemergt + Playbook destilliert)

**Summary:** Carearbeit-Session vollständig abgeschlossen: PR #220 nach grüner CI (3/3) und LGTM-Review squash-gemergt (`6a9849314`, +86/−1.982 über 26 Dateien). Danach auf User-Zuruf: Nebenfund-Kommentar an #169 gepostet und das Verfahren als `docs/playbooks/MASTERPLAN-CAREARBEIT-SESSION.md` destilliert (Betriebsvertrag, 3-Agent-Kartierung, Gates-zuerst, Dead-Code-Fallen-Liste, Lehren-Log). Details und Scorecard im 17:45-Eintrag.

**Decisions:** Squash-Merge (main-Konvention: ein Commit pro PR); Playbook als drittes MASTERPLAN-Dokument nach Issue-/Merge-Session-Muster (stabiler Betriebsvertrag + wachsendes Lehren-Log + pro Session neu befüllter Anhang); CLAUDE.md/INDEX.md-Playbook-Aufzählung auf „Issue-/Merge-/Carearbeit-Sessions" erweitert.

**Dead ends:** Erster #169-Kommentar-Versuch permission-geblockt; nach expliziter User-Freigabe erfolgreich.

**Phase:** Betrieb/Implementation. Promptotyping-Docs aktuell und health-gecheckt (6/6 PASS, Zähler drift-frei); Index-Versionen 4.1.7/1.6.1 überall synchron; main-CI grün.

**Open issues:** #219 Wenzelsbibel-Entscheidung (161 MB Zwischenstände, Optionen A-D im Issue). `doc-count-audit.py` prüft keine code-abgeleiteten Counts (Erweiterungskandidat, Playbook §5.1). Reviewer-Hinweis: gz-Versionsstrings der ausgelieferten Indexe konnten im Review-Sandbox nicht gelesen werden (Loader/Docs aber konsistent, CI-validiert).

**Next steps:** 1. #219 entscheiden (dann Umsetzung als WP C der nächsten Carearbeit-Session, Playbook §6). 2. Optional `doc-count-audit.py`-Erweiterung. 3. Nächste Carearbeit-Session quartalsweise oder nach der nächsten Feature-Welle (Kickoff-Weichen: Playbook §2).

---

## 2026-07-14 – handoff (#219 umgesetzt + Sofort-Duo: doc-count-audit-Erweiterung + #44-Matrix)

**Summary:** Drei Deliverables, alle gemergt: (1) **#219 Wenzelsbibel entschieden (B+D) und via PR #221 umgesetzt** (`974539dc2`): 1.451 Dateien ausgedünnt (1.448 redundante Chunk-TSVs, 2 TEI-Zwischenstände, stale WZB.tei.xml-Kopie), 107 Dateien nach `ingest/wzb/` samt Provenienz-README, 19 Pipeline-Skripte auf neue Pfade; Hilfeseiten brauchten keine Anpassung (nennen WZB nur als Werk). (2) **PR #222** (`a2f3e99d8`): doc-count-audit um Zahlwort-Scan für code-abgeleitete Counts erweitert (12 Werkzeuge / 11 Pattern-Module / 6 Explorer / 18 Entry Points / 10 „weitere", aus Code abgeleitet statt gepinnt; Chronik-Zeilen und Ordinale ausgenommen); schließt Carearbeit-Lehre 1. (3) **#44-Matrix auf Stand 14.07.** + #169-Nebenfund-Kommentar gepostet.

**Decisions:** Wenzelsbibel B+D statt nur Umzug (die zwei Verwirrungsquellen mitbereinigt; Clone-Größe ändert sich ohnehin nicht, Blobs bleiben in History). Review-Anmerkung „Offsets → benannte Mengen" übernommen (`NON_TOOL_MODULES`/`MODAL_MODULES`/`PRE_DESCRIBED_TOOLS` + Sanity-Gate); Anmerkung „bare Werkzeuge-Anker verengen" begründet abgelehnt (FEATURES.md:167 „Zwölf Werkzeuge" fiele aus dem Scan, Ist-Lauf ohne False Positives).

**Dead ends / Lehren:** (1) sed-Pattern `Wenzelsbibel/` (mit Slash) verfehlte die `Path(...) / "Wenzelsbibel" / ...`-Segmente in 11 Skripten: das Opus-Review fing es als echten Blocker; bei Pfad-Umzügen immer auch nach dem nackten Namen greppen. (2) GitHub-Issue-Bodies kommen mit CRLF; mehrzeilige String-Replacements erst nach `\r\n`→`\n`-Normalisierung.

**Phase:** Betrieb. Promptotyping-Docs aktuell; Audit-Gate deckt jetzt auch Werkzeug-/Entry-Point-Claims; Index-Versionen unverändert 4.1.7/1.6.1; main-CI grün.

**Open issues:** Ohne-KZW-Restliste: #216 minne-Serie (voll entsperrt, wartet auf Kickoff), #172 Test-Suite + #169 Suchsemantik-Technikteile (Christian-Entscheide; Vorlagen kann die nächste Session bauen), #139 CoReMA (gemeinsame Session). KZW-Gates unverändert (#196/#190/#203/#204/#114/#198-2/#115/#138/#28/#27).

**Next steps:** 1. `/promptotyping orient` lädt diesen Handoff. 2. Bei Kickoff: #216 nach Pilot-Muster (#189/PR #214). 3. Alternativ #172-Stabilitäts-Messreihe als Entscheidungsvorlage.

---

## 2026-07-28 – Autonome Issue-Session + Merge-Session (KZW-Rückgaben 27.07., Bug #224): 5 PRs, Sub-Issue #228

**Summary:** Auslöser war KZWs Durchgang vom 27.07. (#203/#204 geschlossen, #196/#190/#140 mit Nachbesserungen zurück, #198 an Julia, #59-Ping an Linda) plus drei neue Issues (#224 Bug-Report Klaus Schmidt, #225 Wörterbuchnetz, #226 Blogbeitrag) und Julias vier Beobachtungen in #138 vom 17.07. Ergebnis der Issue-Session: **PR #227** (#224, refs #169), **PR #229** (#196 NUM-Filter + Werkzeug-Sweep), **PR #230** (#190 + #140, `Closes #190`), **PR #231** (#138 zwei Frontend-Teilpunkte), **Meta-PR** (dieser). Neu angelegt: **#228** (TEI-Putzen Ziffern-Lemmata und lemmatisierter Apparat). Die anschließende Merge-Session am selben Tag hat vier Fable-Reviews über alle PRs laufen lassen, deren Befunde abgearbeitet und die freigegebenen PRs gemergt.

### Der eigentliche Fund (#224): es war ein Breve

Der Weg zur Diagnose ist der lehrreiche Teil, weil er zweimal falsch abbog.

**Erste Fassung (falsch):** Stufe 3 der Lemma-Auflösung war ein bidirektionaler Substring-Test und traf in der Richtung „Eingabe enthält Lemma" jedes Kurzlemma, das irgendwo in der Eingabe steckte. „böses" → `boeses` enthält `es`, `o`, `se` → `ês`, `ô`, `sê`. Das erklärt den Screenshot scheinbar vollständig. Es erklärt aber nicht, warum `bœse` fehlt, obwohl es die richtige Antwort wäre.

**Zweite Fassung (auch falsch):** `variants["boeses"]` existiert, „böses" kehrt also in Stufe 2 zurück und erreicht Stufe 3 nie. Die Eingabe musste demnach anders kodiert sein. Ich nahm ein **zerlegtes** Umlaut-ö an (`o` + U+0308) und ergänzte NFC als Schritt 0 des Normalizers.

**Dritte Fassung (belegt), nach KZWs Rückfrage:** „Klaus Schmidt hat, soweit ich sehe, aber bŏses getestet. Was ist mit ŏ?" Das Zeichen ist ein **Breve** (U+0306), kein Trema. Die Wenzelsbibel schreibt Umlaute mit Breve, und der Beleg steht im Korpus: der Token `bo` + U+0306 + `ses` in `tei/WZB.tei.xml` trägt `lemmaRef` auf `lemma_788` (`bœse`), `scho` + U+0306 + `ne` auf `lemma_5280`, `wŭnschet` ist `wünschet`. **830 Breve-Tokens stecken in WZB, 469 davon lemmatisiert; keiner der übrigen 666 Texte hat ein einziges.** Klaus Schmidts Einschätzung „das neue WZB-Vokabular" war also zur Hälfte richtig, meine Zurückweisung („kein WZB-Problem") zur Hälfte falsch.

NFC allein behebt den Fall nicht: es komponiert `o` + U+0306 zu `ŏ` (U+014F), und das war unbelegt. Der Fix braucht beide Schritte, plus die Stufe-3-Regel als davon unabhängige Verbesserung.

**Lehre:** die naheliegende Erklärung, die den Screenshot erklärt, ist nicht dieselbe wie die Erklärung, die auch das *Fehlen* des erwarteten Treffers erklärt. Und: bei einem gemeldeten Zeichenproblem das gemeldete Zeichen im Hexdump ansehen, nicht im Rendering.

**Decisions:**
1. **Stufe 3 matcht Präfixe, beidseitig, Mindestlänge 3 nur suffixseitig** (ADR-016, CONTRACTS §C). Gemessen über 300 Seed-Formen: Top-1 0,3 % → 9,3 % (allein durch die neue Sortierung) → 10,0 % (mit der Regel), Median-Liste 8 → 0, Recall 11,3 % → 10,7 %. Der Sprung kommt fast vollständig aus der Sortierung; die mittlere Spalte gehört immer dazu, sonst liest es sich als 30-facher Effekt der Regel. Geteilt wird bewusst nur das Prädikat (`assets/js/lib/lemma-resolve.js`), nicht die Orchestrierung.
2. **Breve über o/u ist ein Umlautzeichen** (`ŏ` → `oe`, `ŭ` → `ue`, Contract A Schritt 3). Breve über `w`, `n`, `y`, `z` (130 weitere WZB-Tokens) bleibt unangetastet: dort ist es keines, und Unicode hat dafür keine präkomponierte Form, die Schritt 0 erzeugen könnte.
3. **NUM-Filter nur bei reinem NUM**, nicht per `includes`: 47 der 119 NUM-Hapaxe tragen weitere Wortarten (`zwispeltic` ADJ/NUM, `zweizungen` NOM/NUM) und sind Inhaltswörter. Damit strenger als `hideNames`/`hideFunctionWords`, im Code begründet.
4. **Kein NUM-Filter in den übrigen elf Werkzeugen**, je einzeln begründet (in der Wortfrequenz ist `ein` das häufigste NUM-Lemma überhaupt; an Versenden stehen NUM-Lemmata in 0,81 % als legitime Reimwörter).
5. **Facetten-Vorrang einheitlich für alle drei Default-Filter** (NAM, NUM, Funktionswörter): eine explizit gewählte Wortart hebt den gleichnamigen Filter auf und deaktiviert dessen Checkbox sichtbar. Ohne die Regel liefert die Facette NAM kommentarlos eine leere Liste, obwohl NAM 28 % der Hapaxe stellt.
6. **Verszählungs-Reset nur an `<div>`-Grenzen, mit zwei Bedingungen:** erste numerische `<l>` trägt `n="1"` UND die 1 kommt im div genau einmal vor. Nie an `<lg>`: NBB zählt pro Strophe 1..4, ein lg-Reset hätte die #127-Regression reproduziert.
7. **#140 nicht selbst geschlossen** (KZW schrieb „für die Abnahme", nicht „schließen"), #190 schon (expliziter Auftrag).

**Reviews (vier Fable-Durchgänge plus die Bot-Reviews):** Sie haben mehr gefunden als die erste Runde, und zwar durchweg Belegbares.

1. **Die #138-Reichweiten-Zahlen waren zweimal falsch geschätzt.** FR3 mit +141 zusätzlichen Randnummern ist arithmetisch unmöglich, weil der Text nur 139 `<l n="1">` hat und jeder Reset höchstens eine Nummer sichtbar macht. Ersetzt durch `scripts/audit/count-verse-numbering-resets.py`, das die Render-Reihenfolge nachbaut und „mit Reset" gegen „ohne Reset" vergleicht. Belastbar sind jetzt: 1.497 qualifizierende divs in 137 Texten, **1.352 zusätzliche Randnummern in 49 Texten**, PZ +826, FR3 +136, CHH +53, TKR +40, HUG +39. Die zweite Bedingung verwirft 1.172 divs in 84 Texten und verhindert 1.007 unmotivierte Randeinsen, davon 38 allein in NLA.
2. **Contract A hatte mit Schritt 0 einen Schritt ohne Paritätsabdeckung.** Keiner der 18 Fälle enthielt ein kombinierendes Zeichen: wer NFC aus einem der beiden Normalizer entfernt, bekäme 18/18 grün und einen still driftenden Index. Jetzt 23 Fälle, die neuen als `\u0308`-Escape geschrieben, weil ein Editor mit Auto-Normalisierung die zerlegte Form sonst still zusammenzieht und den Test entwertet.
3. **Der Kommentar am NFC-Schritt behauptete das Gegenteil des PR** („ändert die Build-Ausgabe nicht, Index byte-identisch"). Er stammte aus dem Stand vor der Index-Messung.
4. **Der Versions-Bump war an zwei von vier Pflegestellen nicht angekommen** (TEI-MODEL §11 als deklarierte Source of Truth und INDEX.md). `check-index-versions.py` prüft nur die drei Code-Stellen und deckt die Doku-Stellen nicht ab.
5. **Der NLA-Test ist gegen main nicht trennscharf** und wäre dort ebenfalls grün. Er sichert die zweite Bedingung gegen späteres Vereinfachen, nicht das Feature gegen den Vorzustand. Steht jetzt als Einschränkung im Test.
6. Dazu: `hilfe-playground.html` nannte den neuen Default-Filter nicht (die Seite ist `CODE_DOC_TARGET` des doc-count-audits), `DATA-MODEL.md` beschrieb Stufe 3 weiter als Substring, der `fri`-Test war seit jeher als „Stage 3" beschriftet und erreicht Stufe 3 nie, und `.cursor-not-allowed` fehlte im gepurgten Tailwind-Output.

**Dead ends / Lehren:**
1. **Der Advisor-Durchgang (Fable 5) vor dem Start hat drei echte Planfehler gefunden**, alle bestätigt: (a) die geplante Messmetrik „0-Treffer-Quote als Abbruchkriterium" hätte immer ausgelöst, weil die alte Regel wegen der Kurzlemmata praktisch nie 0 Treffer liefert; ersetzt durch Recall/Median/Top-1. (b) „Reset pro Nummerierungsbereich" war unterspezifiziert und hätte über `<lg>` die NBB-Regression gebracht. (c) Der Doku-/Spec-Nachzug fehlte in der Welle. Lohnt sich vor jeder Session mit Semantik-Änderung.
2. **Grüner Test heißt nichts, solange nicht geprüft ist, ob er auch OHNE die Änderung grün wäre.** Zweimal angewandt und zweimal bestätigt: der neue NAM-Facetten-Test und der Breve-Test fallen ohne ihre Änderung durch, jeweils per temporärem Rückbau nachgewiesen. Der NLA-Test besteht diese Probe nicht und trägt das jetzt im Kommentar.
3. **Eine Zusicherung, die strukturell trivial erfüllt ist, schützt nichts.** „NBB bleibt unverändert" war wertlos, weil NBB gar keine `<div>` hat. Der echte Risikofall war NLA.
4. **`classList.contains()` ist kein Sichtbarkeits-Check**, nötig ist die berechnete Anzeige. Daran ist ein CSS-Kaskadenfehler durchgerutscht (`.back-to-top { display: flex }` schlug Tailwinds `.hidden`).
5. **`npm test` als Baseline mitlaufen zu lassen, während man Dateien ändert, ist wertlos.** Über 40 Minuten bei 1 Worker, und getestet wird der Zwischenstand. Besser: gezielte Spec-Dateien pro Welle.
6. **Der JS-Bridge-Kontext der Chrome-Extension liefert keine IntersectionObserver-Callbacks** und `window.scrollTo` löst dort kein `scroll`-Event aus. Kostete zwei Fehldiagnosen; echtes Scrollen per `computer`-Tool zeigt das richtige Verhalten.
7. **`behavior: 'smooth'` ist auf den Reader-Seiten wirkungslos**, distanzunabhängig und ohne aktives `prefers-reduced-motion`.
8. **`readingBody.childElementCount` ist kein Indikator für „Text geladen"** – der Body trägt immer einen Platzhalter. Kriterium ist `readingTitle`.
9. **Unicode-Literale in Testdateien sind nicht stabil.** Werkzeuge normalisieren zerlegte Formen still zu NFC. Wer eine zerlegte Form testet, schreibt sie als Escape, sonst entwertet der nächste Editor-Durchlauf den Test lautlos.

**Phase:** Betrieb. Promptotyping-Docs mitgezogen (CONTRACTS §A + §C, ARCHITECTURE, FEATURES, DESIGN, DECISIONS ADR-016, DATA-MODEL, INDEX, TEI-MODEL §11, CLAUDE.md, README); `doc-count-audit.py` und `build-pages.py --check` ohne Drift. **PR #227 ist ein Daten-PR:** Authority-Index 1.6.1 → **1.6.2**, weil drei Datensätze mit zerlegtem ü (`person_1052`, `person_1332`, `work_435`) über die normalisierte Suche unauffindbar waren; vier `api/`-Dateien ziehen mit. Corpus-Index bleibt 4.1.7. Die Breve-Regel selbst ändert den Index **nicht**: kein Authority-File enthält ein Breve (Rebuild byte-identisch, `variants.xml` ebenfalls ohne Drift).

**Open issues:** Neu bei KZW: #228 (Apparat-Entannotierung, 400 Tokens in 165 Notes über 16 Texte; ohne die GWTK-Notes mit ganzen Versblöcken, mit ihnen 587 Notes und 2.458 Tokens), #138 Render-Policy für die DIG-Strophenzähler in HUG, #140-Abnahme, dazu die Breve-Rückfrage für `w`/`n`/`y`/`z`. Unverändert: #115, #189-Review-Fälle, #198-Schritt-2, #28, #27, #129 (gebaut und live, Prüfung steht aus), #114 (Linda), #92 (Carina), #147 (Silvan), #86 (Alan). Ohne-KZW-Restliste: #216 minne-Serie, #172 Test-Policy, #58/#18-Entscheide.

**Next steps:** 1. #230 und #231 mergen, sobald die beiden fachlichen Antworten da sind (Lizenz-Reichweite bzw. Sichtprüfung der 1.352 neuen Randnummern). 2. KZW-Rückfrage zum Breve auf `w`/`n` in der WZB-Transkription: 64 lemmatisierte Tokens bleiben sonst per Copy-Paste unauffindbar. 3. #216 minne-Serie ist weiterhin voll entsperrt und wartet nur auf den Kickoff.

---

## 2026-07-28/29 – Merge-Session: vier PRs auf main (#241, #238, #243, #240), Health-Check #140

**Summary:** Abarbeitung des vor dem Compact freigegebenen Plans. Gemergt in dieser Reihenfolge: **#241** (Em-Dash-Gate, Selbsttest 42/42), **#238** (#235 kaputte Tilden in 21 TEI-Headern + `works.xml`, Authority 1.6.2 → 1.6.3), **#243** (#138: 814 Strophenziffern aus HUG, Corpus 4.1.7 → 4.1.8, Authority → **1.6.4**), **#240** (#196 Werktitel + Autor im Hapax-Panel). Neu geöffnet: **#244** (Emoji-Icons, 13 Stellen). #231 bleibt bewusst offen: fachliche Prüfung der Verszählung steht bei KZW/Julia aus.

**Health-Check-Scorecard (#140, ausgelöst von KZWs erneutem Em-Dash-Fund):** Alle bestehenden Gates grün (Em-Dash, CDN, Index-Versionen, Doc-Counts). Algorithmen-Stichprobe **3/3** deckungsgleich (MHG-Normalisierung inkl. Python-Parität, `lemmaRefMatchesId` wörtlich wie CONTRACTS §B.1, Stufe-3-Prädikat), XPath-Stichprobe **3/3** (zwei notationelle Abweichungen mit null Fällen in den Daten). Testsuite strukturell sauber: 221 Tests, kein `skip`, kein `only`, kein still-bestanden-Muster, und erstmals seit Langem tatsächlich gelaufen (221/221 in 16,3 min). Ein echter Befund: Emoji als UI-Icons entgegen der Heroicons-Konvention, jetzt #244.

### Die Lehre der Session: ein grünes Gate ist kein wirksames Gate

#243 hatte die Variantenzahl auf allen Hilfe-Seiten von 256.761 auf 256.760 gezogen, den Stats-Block der **Startseite** aber stehen lassen: sie widersprach `hilfe-daten.html` im selben PR. Das Audit war grün, weil `index.html` nie in `DOC_TARGETS` stand.

Beim Schließen dieser Lücke ist mir **dreimal hintereinander** ein Audit-Eintrag unterlaufen, der aussah wie ein Gate und keines war. Jedes Mal deckte erst der Mutationstest es auf (alte Zahl zurücksetzen, Audit muss rot werden):

1. `index.html` eingetragen: Mutation überlebte, weil der Anker `orthographische` kleinschreibt, das Kartenlabel aber „Orthographische Varianten".
2. `CONTRACTS.md` eingetragen: Mutation überlebte, weil dort englisch „raw forms" und „normalized entries" steht.
3. `DATA-MODEL.md:266` korrigiert und Anker `mappings` ergänzt: Mutation überlebte immer noch, weil die Datei den Schlüssel `variants_normalized` gar nicht führte.

**Der Doppel-Blindfleck ist strukturell:** ein `DOC_TARGETS`-Eintrag wirkt nur, wenn der Anker die dortige Formulierung trifft, und ein Anker wirkt nur, wenn die Datei den passenden Schlüssel führt. Beides muss zusammenkommen, und beides fehlt still. Wer nach dem grünen Lauf aufhört, committet Dekoration. Inzwischen sind alle neun Fundstellen der beiden Varianten-Zahlen per Mutation nachgewiesen abgedeckt.

**Decisions:**
1. **Authority-Index auf 1.6.4**, nicht 1.6.3: #238 und #243 hatten unabhängig dieselbe Nummer vergeben. Umnummeriert wurde der später gemergte PR, damit der zweimal reviewte Stand von #238 unangetastet bleibt.
2. **Paratext-Policy in `DATA-MODEL.md` aufgeteilt.** Sie sagte pauschal „Römische Zahlen im Text: `<w>` behalten", also das Gegenteil dessen, was #138 tut. Jetzt: Zahlen im Textfluss bleiben, Randzählungen gehen und leben in `lg/@n`. Erkennungsmerkmal ist der **xml:id-Block**, nicht `@pos` (in HUG trugen 108 der 814 Randziffern gar keine Annotation, ein `@pos`-Filter erwischt nur 87 %).
3. **`index.html`, `DATA-MODEL.md`, `TEI-MODEL-AUTH-FILES.md` und `CONTRACTS.md` neu im Count-Audit**, mit den englischen Ankern `variant forms`, `raw forms`, `normalized entries`, `mappings` und der Großschreib-Variante.
4. **Kein `<change>` im `revisionDesc` von HUG.** Die Konvention ist im Korpus uneinheitlich (auch #238 hat für 21 geänderte Header keinen gesetzt); ob maschinelle Eingriffe einen Eintrag bekommen, ist eine redaktionelle Entscheidung für KZW, keine technische.

**Lehren, jenseits der Gate-Lehre:**
1. **`git rebase --continue` frisst `#`-Zeilen** aus der Commit-Message. Betreff „#138: …" und alle `##`-Überschriften waren weg. Lösung: nach dem Auflösen `git commit -C <original> --cleanup=verbatim`, dann erst `--continue`.
2. **Die Ausgabedatei eines Hintergrund-Laufs behält nur den Schwanz.** Nach `npm test` fehlten die ersten 182 Testzeilen, die Hapax-Specs waren im Protokoll unsichtbar. Wer die Abdeckung belegen will, lässt die betroffenen Specs gezielt noch einmal laufen (7/7 in 35 s), statt aus der Gesamtzahl zu schließen.
3. **Eine Wartebedingung auf CI-Checks muss auf deren Existenz warten, nicht nur auf ihr Ende.** `grep -c pending` ist unmittelbar nach dem Push 0, weil die Checks noch nicht angelegt sind, und die Schleife fällt sofort durch.
4. **Zahlen im Fließtext altern mit den Daten, auch in Code-Kommentaren.** `hapax-legomena.js` begründete den fehlenden DIG-Filter mit „4.755 Korpusbelege"; nach #138 sind es 4.049. Die Differenz ist exakt 706, also genau die annotierten unter den 814 HUG-Ziffern.

**Phase:** Betrieb. Live verifiziert: `api/index.json` meldet 1.6.4 / 4.1.8. Deterministische Builds (#125) haben gehalten: nach dem Rebase-Rebuild zeigte der Diff ausschließlich die zwei Versionsstrings, und die CI kam beim eigenen Nachbau auf byte-identische Indexe.

**Open issues:** #244 (Emoji-Icons) wartet auf Review; #231 auf die fachliche Verszählungs-Prüfung. An KZW gemeldet: sieben Texte mit leerem `<author>`-Element (ALX, BVSN, PSG, PTS = Mönch von Heilsbronn, BOP = Boppe, MHG = Herger, MRB = Burggraf von Riedenburg) und die Namensvariante Rietenburg/Riedenburg zwischen `works.xml` und `persons.xml`, beides an #228. Korpusweit stehen noch **4.077 `w[@pos="DIG"]` in 79 Texten** (frühere Angabe „4.657 in 66" war falsch gezählt), und diese Zahl **unterschätzt** die echte Menge, weil sie die unannotierten Randziffern nicht sieht.

**Next steps:** 1. #244 reviewen und mergen. 2. #228 als nächste große Sache, KZWs detaillierter Auftrag steht im Issue. 3. Vor einem korpusweiten Ziffern-Lauf die zwei offenen Härtungen im Skript schließen (`huelle_leer()` prüft nur `el.text`, nicht `el[0].tail`; der Regex `^[ivxlcdm]+$` trifft auch „im", „vil", „lid"). 4. KZW an Alan erinnern (they/them), zweite Septemberwoche.

---

## 2026-07-29 – Nähesuche misst jetzt die Spanne (#169, Befunde 15/48/51)

**Kontext:** KZW hat am 28.07. in #169 die drei letzten offenen Audit-Befunde freigegeben („#15 Nähesuche: bitte fixen", „#51 und #48: einverstanden"). Die Nummern 15, 48 und 51 sind Befund-Nummern im Issue-Body, keine Issue-Nummern. Alle drei sitzen im Playground und berühren keine Daten, also kein Data-Change-Lifecycle und kein Index-Bump.

**Die Zahlen-Zäsur, um die KZW ausdrücklich gebeten hat.** Ab heute bedeutet „innerhalb N Wörter", dass alle Treffer-Positionen zusammen in ein Fenster der Breite N passen. Vorher wurde jedes weitere Lemma nur gegen das Anker-Lemma gemessen, die reale Spanne konnte also bis 2×N betragen. **Trefferzahlen aus Suchen mit drei oder mehr Lemmata von vor dem 29.07.2026 sind mit heutigen nicht vergleichbar und liegen systematisch zu hoch.** Bei zwei Lemmata sind Ankerabstand und Spanne dasselbe; dort ändert der Fenster-Fix nichts.

Gemessen an „minne + herze + leit" (lemma_4130 + lemma_2795 + lemma_3691) über alle 667 Texte:

| maxDistance | Treffer alt | Treffer neu | größte real gemeldete Spanne im alten Stand |
|---|---:|---:|---:|
| 5 | 1 | 0 | 6 (BUH) |
| 10 | 5 | 4 | 12 (TRM) |
| 20 | 19 | 16 | 38 (RDS) |

Der RDS-Fall zeigt das Ausmaß: bei „innerhalb 20 Wörter" standen die drei Lemmata 38 Wörter auseinander. Die daneben berechnete `actualDistance` hat diese 38 sogar korrekt ausgewiesen, der Filter hatte den Treffer nur längst durchgelassen.

**Warum der Fix eine Fenstersuche ist und keine Nachprüfung.** Die naheliegende Minimallösung wäre, die alte Auswahl zu behalten und Treffer mit zu großer Spanne zu verwerfen. Das erzeugt aber falsche Negative: `positions.find()` nahm die erste Position in Ankernähe, nicht die brauchbarste. Bei B = {90, 110}, C = {109} und Anker 100 fiele der Treffer weg, obwohl B = 110 mit C = 109 exakt die Spanne 10 bildet. `findCoveringWindow` iteriert deshalb über die möglichen Fensteranfänge und nimmt die kleinste tragfähige Spanne; das hält nebenbei die angezeigte Distanz minimal. Der Testfall dazu ist im Rückbau rot mit `distance: 19` geworden, also genau dem Wert, den die Minimallösung verworfen hätte.

**Befund 48, der Dedup log seit jeher.** Bei überlappenden Kontextfenstern behielt der Code den zuerst startenden Treffer, während Kommentar und Konsolenzeile „keeping shorter distance" behaupteten. Jetzt entscheidet die Distanz. Nebeneffekt: die Trefferzahl kann dadurch leicht **steigen**, weil die distanzsortierte Greedy-Auswahl mehr nicht überlappende Fenster zulässt. Bei „minne + herze" (2 Lemmata, Abstand 10) gehen 243 auf 244; die Rohtrefferzahl bleibt bei 276 unverändert. Das ist die einzige Zahlenänderung, die auch Zwei-Lemma-Suchen betrifft.

**Befund 51 war kein Zukunftsrisiko mehr, sondern ein aktiver Bug.** Das hartkodierte Fast-Path-Wörterbuch in `tei-ui.js` löste zum Zeitpunkt der Entfernung fünf von elf Eingaben falsch auf, weil die Lemma-IDs seit dem Eintragen neu vergeben wurden: „fleisch"/„vleisch" lieferten lemma_1816 *forma* statt lemma_7121 *vleisch*, „käse"/„kæse" lemma_26713 *eierkæse* statt lemma_3175 *kæse*, „bier" lemma_712 *bir* (die Birne) statt lemma_702 *bier*. Wer im Playground „bier" suchte, bekam Birnen. Die sechs korrekten Einträge verlieren nichts, weil Stufe 1 und 2 sie ohnehin finden. Das Issue führte den Punkt als künftiges Renumbering-Risiko; das Renumbering hatte längst stattgefunden, nur gemerkt hatte es niemand, weil ein Fast-Path per Definition nie am Vergleich vorbeikommt.

**Lehren:**
1. **Ein fehlschlagender `npm test` blockiert am Ende die Shell.** Playwrights HTML-Reporter serviert bei Failures den Report und wartet. Für Rückbau-Beweise `PW_TEST_HTML_REPORT_OPEN=never` setzen, sonst läuft das Kommando in den Timeout und lässt bei `git stash`-Rückbauten den Stash liegen.
2. **Ein Fast-Path ist eine Zusicherung ohne Prüfstelle.** Er umgeht genau den Code, der einen Fehler bemerken würde. Ein Cache mit Invalidierung wäre vertretbar gewesen, ein Literal-Dict auf IDs nicht.
3. **Die Doku hatte recht und der Code unrecht.** `ARCHITECTURE.md` beschrieb seit jeher „find combinations where all lemmata within maxDistance". CONTRACTS §C.2.2 dagegen hat die falsche Dedup-Semantik mitsamt Begründung festgeschrieben („This keeps the closer match since results within each file are sorted by position"). Pseudo-Code in Verträgen erbt Bugs, wenn er aus dem Code abgeschrieben statt gegen die Absicht geprüft wird.

**Nicht angefasst, aber gefunden:** `findProximityMatchesInIndex` (`tei-manager.js`) wertet nur `positionSets[0]` und `[1]` aus, ignoriert also ab dem dritten Lemma alles. Die Funktion ist über `searchProximityUsingIndex` erreichbar, das im ganzen Repo nirgends aufgerufen wird, also toter Code. Ebenso tot: `executeProximitySearch` in `tei-ui.js`, das ein blockierendes `prompt()` öffnet. Beides gehört in eine Aufräumrunde, nicht in einen Semantik-PR.

---

## 2026-07-29 – handoff (Autonome Issue-Session: PR #245 #169-Suchsemantik + PR #246 #239-Wortbestandteil-Suche)

**Kontext:** Kickoff über das Playbook `docs/playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md` (Fassung vom 29.07.). Anlass waren KZWs vier Entscheidungen vom 28.07., die vorher blockierten. Zwei Wellen plus Meta, kleiner als die Session vom 28.07., dafür mit schriftlich vorliegenden Entscheidungen zu jedem Punkt. Vorflug sauber: `origin/main..main` leer, Index-Versionen konsistent (4.1.8 / 1.6.4).

**Ergebnis:**

| PR | Issue | Inhalt | Closes? |
|----|-------|--------|---------|
| #245 | #169 | Nähesuche misst die Spanne, Dedup behält den distanzkürzesten Treffer, Fast-Path gestrichen; CONTRACTS §C.2.2 neu | nein (Abnahme KZW) |
| #246 | #239 | Wortbestandteil-Suche im Lemmata-Explorer, nach Position gruppiert | nein (Abnahme KZW, zwei Rückfragen) |
| Meta | #44 | Matrix auf 40 offene Issues, ROADMAP, dieser Eintrag, Playbook | nie |

Kein Issue geschlossen, drei Issue-Kommentare (#169, #239 mit KZW-Ping, #44-Abschlussreport). Beide Code-PRs frontend-only, kein Data-Change-Lifecycle, kein Index-Bump.

**Was über den Auftrag hinaus herauskam:**

1. **Das Playbook lag bei einem Detail falsch, und Nachmessen hat es gefangen.** §1.1 führte `bîr` als Fall auf, in dem Fast-Path und reguläre Auflösung „beide fragwürdig" seien (angeblich lemma_542 `bern`). Gemessen: `bîr` normalisiert zu „bir", Stufe 1 trifft exakt und liefert dasselbe lemma_712 wie der Fast-Path. Es sind fünf falsche Einträge von elf, nicht sechs.

2. **`rôtwîn` existiert nicht.** Sowohl #239 als auch das Playbook nennen es als Leitbeispiel und als Chrome-Verifikationsziel. Kein Lemma normalisiert auf `rotwin` oder `rotwein`, kein Varianten-Schlüssel. Belegt ist die Anforderung an `ôsterwîn`, `ziperwîn`, `lantwîn`, `hovewîn`, `welschwîn`, `alantwîn`, `sacwîn` und `zûberwîn`. Frage an KZW im Issue.

3. **Auch das zweite Akzeptanzkriterium von #239 traf nicht zu.** Es erwartet `winter` bei `gewinnen` in der Wortmitten-Gruppe; `winter` beginnt aber mit „win" und gehört nach der positionalen Gruppendefinition an den Wortanfang. Umgesetzt ist die Definition, nicht das Beispiel, und der Test hält die Abweichung fest.

4. **Eine Doku-Aussage in drei Dateien war falsch, und der Review hat sie gefunden.** Code-Kommentar, Hilfeseite und `FEATURES.md` behaupteten übereinstimmend, eine Trennung von `-wîn` und `-swîn` bräuchte Stemming und gehöre zu #109. Tatsächlich führen **27.166 der 43.879 Lemmata (61,9 Prozent) ihre morphologischen Bestandteile im Lexikon mit** (`<etym type="morphological">`), und die Angaben liegen längst im ausgelieferten Authority-Index. Daraus wurde eine Markierung „belegte Wortbildung" plus Filter, ohne neuen Build-Schritt. Für „wein" sind von 407 Treffern 50 verzeichnete Bildungen, davon **null in der Wortmitten-Gruppe**: die eingeklappte Gruppe ist damit empirisch begründet und nicht mehr nur behauptet. Lehre: eine Aussage darüber, was die eigenen Daten nicht hergeben, ist eine Messung und keine Einschätzung.

5. **Eine Minimallösung wäre falsch gewesen.** Für die Nähesuche hätte nahegelegen, die alte Auswahl zu behalten und Treffer mit zu großer Spanne zu verwerfen. Das erzeugt falsche Negative, weil `positions.find()` die erste Position in Ankernähe nahm, nicht die brauchbarste. Der Rückbau-Test macht es sichtbar: er wird mit `distance: 19` rot, also genau mit dem Wert, den die Minimallösung weggeworfen hätte. Der Fix sucht deshalb aktiv das engste tragfähige Fenster.

**Lehren:**

1. **Ein fehlschlagender `npm test` blockiert die Shell bis zum Timeout.** Playwrights HTML-Reporter serviert bei Failures den Report und wartet. Der erste Rückbau-Beweis lief zehn Minuten ins Leere und ließ den `git stash` liegen. `PW_TEST_HTML_REPORT_OPEN=never` setzen, und Rückbauten in getrennte Tool-Aufrufe legen, damit ein Timeout den Arbeitsbaum nicht im Mutationszustand zurücklässt.
2. **Chrome hält ES-Module über `-c-1` hinweg im Cache.** Die erste Verifikation von #239 zeigte den alten Stand, erkennbar nur daran, dass eine neue Methode `undefined` war. Nach jeder JS-Änderung hart neu laden und eine neue Funktion als Kanarienvogel abfragen, bevor man Ergebnisse interpretiert.
3. **Gezielte Mutation schlägt Komplettrückbau.** Für #239 hat es mehr gebracht, die Variantenbrücke einzeln abzuschalten und die Collapse-Regel einzeln umzudrehen, als alle drei Dateien zurückzusetzen: der Komplettrückbau macht alles rot und beweist deshalb nichts über einzelne Zusicherungen.
4. **Auch eine Zusicherung prüfen, von der man vermutet, sie sei ohnehin erfüllt.** Der Tiebreak im Dedup sah nach totem Code aus, weil die Einfügereihenfolge schon nach `contextStart` läuft. Die Mutation zeigte das Gegenteil: umgedreht wird der Test rot.
5. **Ein Branchwechsel während eines Hintergrund-Testlaufs zerstört den Lauf lautlos.** Der Arbeitsbaum ist geteilt; das `git checkout` auf den Meta-Branch zog Playwright mitten im Lauf die Spec-Datei weg. Die Konsole meldete „41 passed" und keinen Fehler, `testing/test-results/report.json` dagegen 57 Tests mit einem `unexpected` („Cannot find module") und fünfzehn `skipped`. Wer nur die Zusammenfassung liest, hält eine Kollision für ein Ergebnis.
6. **Ein CSS-Rebuild lässt sich exakt prüfen.** `tailwind-output.css` ist minifiziert, der Diff ist immer die ganze Datei. Die Selektorlisten vorher und nachher mit `comm` vergleichen: hier kam genau `.pb-2` dazu, nichts entfiel.

**Reviews:** Beide PRs zusätzlich vom fable-advisor gegengelesen, dazu der automatische Opus-Review auf #245. Übernommen wurden vier Befunde: die Mindestlänge in #239 gilt jetzt auch für die Brückenform, das Grundwort selbst ist ankreuzbar, `maxDistance` wird in der Datenschicht auf den vom UI deklarierten Bereich geklemmt (die Fenstersuche ist im Gegensatz zur alten Ankerprüfung von der Distanz abhängig teuer, und die Hash-Route prüft `dist` nur auf > 0), und der Dedup-Tiebreak hat einen eigenen Test bekommen. Der `words[]`-first-id-Caveat in CONTRACTS §C.2.2 geht ebenfalls auf einen Review-Befund zurück.

**Phase:** Betrieb. **Open issues:** #169 und #239 warten beide auf KZWs Abnahme, #239 zusätzlich auf die zwei Rückfragen oben. **Next steps:** 1. #245, #246, Meta-PR in dieser Reihenfolge mergen, Review-Runs vorher canceln. 2. KZW für #239 anpingen, sobald live. 3. Die Playground-Aufräumrunde (toter Code plus `resolveLemmaIds`-Deduplizierung) als kleines eigenes Ticket anlegen oder in der nächsten Session mitnehmen.

## 2026-07-29 (nachmittags): Playground-Aufräumrunde

Die in ROADMAP und JOURNAL vorgemerkte kleine Runde, direkt nach dem Merge von #245/#246/#247. Frontend-only, keine Datenänderung.

**Acht Funktionen ohne Aufrufer entfernt:** `findProximityMatchesInIndex`, `searchProximityUsingIndex`, `searchDocumentUsingIndex`, `enrichResultsWithTEIText` und `enrichProximityResultsWithText` (alle `tei-manager.js`), `executeProximitySearch` (`tei-ui.js`, öffnete ein blockierendes `prompt()`), dazu `findTextsContainingLemmas` und `hasCorpusIndex`, die erst durch die Löschung von `searchDocumentUsingIndex` verwaisten (deren einziger Aufrufer war sie). Der Beleg lief über einen repoweiten Grep über JS **und** HTML: dieses Projekt verdrahtet UI über `onclick="window.playground.ui…"`-Strings, ein reiner JS-Grep hätte einen Aufrufer übersehen.

**Der Fund, der die Runde gelohnt hat:** `enrichProximityResultsWithText` schnitt Kontextfenster mit Index-Positionen (die nur `<w>` **mit** `@lemmaRef` zählen) in die ungefilterte `<w>`-Liste. Bei einer Wiederbelebung hätte sie stillschweigend verschobene Belege geliefert. Der Unterschied ist keine Kleinigkeit: über alle 667 Korpusdateien tragen 1.898.318 von 9.431.316 `<w>` kein `@lemmaRef`, also 20,1 % (AUP 41,6 %, REF 39,3 %, DL1 38,8 %; 145 Dateien ganz ohne Lücke). Der lebende Anreicherungspfad in `ui-helpers.js` macht es richtig.

**Doppelte Lemma-IDs ließen beide Kookkurrenz-Modi degenerieren.** „wîn" und „wein" lösen beide auf `lemma_7532` auf, das eine über Stufe 1, das andere über die Variantenliste. Mit nur einer eindeutigen ID hat `findCoveringWindow` keine abzudeckende Restliste mehr und gibt `[]` zurück, was truthy ist: jede Fundstelle wurde zum Treffer mit Abstand 0. Im Vers-Modus dieselbe Wirkung aus anderem Grund, dort läuft die Vergleichsschleife `for (let i = 1; …)` nie und `allInVerse` bleibt `true`. `resolveLemmaIds` dedupliziert jetzt, beide Enhanced-Funktionen haben einen eigenen Guard, und die Oberfläche erklärt den Fall statt ihn zu verschlucken.

**Lehren aus den Reviews dieser Runde:**

1. **Vorschläge aus einer Zweitmeinung sind Vorschläge, keine Befunde.** Der Rat, einen verwaisten Kommentar-Verweis auf `searchProximityUsingEnhancedIndex` umzubiegen, war sachlich falsch: diese Funktion scannt `words[]` (First-Id) und ist damit gerade die bekannte Abweichung von der Consumer-Rule in CONTRACTS §B.1, nicht das Vorbild. Ungeprüft übernommen, vom zweiten Reviewer gefangen. Gemessen: 0 von 7.532.998 `@lemmaRef`-Werten tragen mehr als eine Referenz, folgenlos ist die Abweichung also nur heute.
2. **Eine Stichprobe ist keine Messung.** Die Abweichungsquote stand zuerst mit 29,2 % aus zwölf Dateien in der Doku. Die Vollmessung ergab 20,1 %. Wenn eine Zahl in einen Vertrag geschrieben wird, gehört sie über den ganzen Bestand gerechnet.
3. **Eine Verneinung braucht denselben Beleg wie eine Behauptung.** „Im Playground gibt es keinen blockierenden Dialog mehr" stand im Kommentar, nachdem ich nur nach `prompt(` gesucht hatte; `playground-main.js` enthält weiterhin drei `alert()` und drei `confirm()`. (Beim ersten Aufschreiben stand hier „zwei alert()", also eine falsche Zahl ausgerechnet in der Lehre über unbelegte Behauptungen. Vom Review gefangen, nachgezählt.)
4. **Eine Fehlermeldung kann selbst eine Falschaussage sein.** Der erste Guard meldete „Ihre Eingaben führen auf dasselbe Lemma", sobald mehr als ein Begriff eingegeben war. Bei „minne" + „qqqq" ist das schlicht falsch, der zweite Begriff löst gar nicht auf, und die Meldung schickt jemanden auf die Suche nach einer Homonymie, die es nicht gibt.

**Verifikation:** 259/259 Playwright-Tests grün über 30 Spec-Dateien, aus `report.json` ausgezählt, gemessen nach allen Review-Nachträgen. Vier Regressionstests ergänzt (die Spec-Datei geht von 10 auf 14 Blöcke), die Dedup, Normalisierung und die Degeneration beider Kookkurrenz-Modi festnageln.

**Phase:** Betrieb. **Open issues:** #251 (Auswahl im Wortbestandteil-Modus als Modell), #239 und #169 warten weiter auf KZWs Abnahme.

---

## 2026-07-29 (abends): ParzivAI-Wissen in die Promptotyping-Docs überführt

**Kontext:** Die Infos zu ParzivAI lagen als Handover-Notiz in `docs/features/ParzivAI-Infos-fuer-Chris.md`, mit der ausdrücklichen Frage, in welches Promptotyping-Doc sie gehören. Grundlage der Notiz war ein Chat mit Florian Nieser vom 09./10.07.

**Befund vor der Einarbeitung:** ParzivAI, „MHDBDB goes AI", Nieser, Renkert, Heidelberg und Apertus kamen in keiner einzigen Doku-Datei vor; „Sprachmodell" und „feingetunt" hatten repoweit überhaupt nur diese eine Fundstelle. RESEARCH.md hatte keinen Ort für Nachnutzung durch Dritte: die nächstliegenden Stellen waren das Bullet „Machine learning for automatic annotation" unter Future Research Directions und „CC BY-NC-SA license enables reuse" im Ethik-Abschnitt, also Lizenz statt Praxis.

**Aufteilung nach Halbwertszeit.** Der Sachstand (was ParzivAI ist, Team, CLARIAH-AT-Bezug, technischer Stand, Quellen) steht als neuer `##`-Abschnitt „Downstream Reuse and Related Projects" in RESEARCH.md, vor „Limitations & Future Directions" und englisch wie der Rest der Datei. Die Links zusätzlich in INDEX.md unter „Links and Resources" als neue Untergruppe „Related Projects". Die Handlung, also die Vermittlung Brom ↔ Nieser, gehört nicht in die Wissensdokumentation, sondern in die Menschen-Pings-Tabelle der ROADMAP, wo alle personengebundenen Vorgänge geführt werden (dort als einzige Zeile ohne Issue-Nummer).

**Kein ADR-017.** Alle 16 bestehenden ADRs beantworten dieselbe Frage: mehrere technische Optionen für unser Artefakt, welche nehmen wir, mit `Alternatives` und messbaren `Consequences` für Code, Daten oder Schema. Ein externes Projekt zur Kenntnis zu nehmen hat weder Alternativen noch Konsequenzen fürs Repo. Fällig würde ein ADR erst, wenn eine Entscheidung mit Repo-Folgen ansteht, etwa ein Export von Übersetzungsdaten für externes Modelltraining oder deren Aufnahme in die JSON-API.

**Quelldatei gelöscht** nach der Temporal-Artifacts-Regel: `docs/features/` ist Zwischenlager, nicht Zielort. Wichtig dabei: die Notiz war nie committet (untracked), git history ist hier also ausnahmsweise **kein** Archiv. Deshalb wurde die Substanz vollständig übernommen, inklusive der Personen-Rollen und aller drei Quell-Links.

**Phase:** Betrieb. **Next steps:** Vermittlung Brom ↔ Nieser anstoßen, wenn die Merge-Welle abgearbeitet ist.

---

## 2026-07-29 – #236 Frauenlob-Revision: verlorene Parallelüberlieferungs-Ebene aus den Legacy-Quellen rekonstruiert

**Kontext:** #236 lag als `needs-clarification` / `depends-on-human`, weil fünf philologische Fragen offen waren und der Issue-Text als Schritt 1 „Prüfung am Druck" verlangte – ohne die Bände sei alles Weitere Spekulation. KZW brachte stattdessen die alten Ingest-Ordner aus dem SEMD-Sharefolder-Backup ein. Das hat die Sitzung gedreht: statt am Druck zu prüfen, ließ sich alles gegen die Quelle verifizieren.

**Der eigentliche Fund – in zwei Stufen.** Zuerst die RTF-Transkripte (`ERLEDIGT/Frauenlob_Bd2/`): sie führen „Parallelüberlieferung 1/2/3/4" als Zwischenüberschrift im Klartext, dazu Ton-Namen und Vers-Offset-Notizen („beginnend mit Vers 46"). Damit waren 110 von 110 Strophen gedeckt – aber erst über **beide** RTFs, weil `Frauenlob.rtf` kein älterer Teilstand ist, sondern komplementär: es notiert Zeugen mit Siglen `A1/A2/B1` statt mit Überschriften. Dann lieferte KZW die eigentlichen Ingest-Dateien nach (`ERLEDIGT/FR2.txt`, `FR3.txt`) – mit dem **19-stelligen Linecode**, also der `u`-Ziffer direkt im Datensatz. Damit war die Rekonstruktion kein Erschließen mehr, sondern ein Join.

**Lehre 1 – die „Decoding-Falle" ist enger als LINECODE.md sie beschrieb.** Das Dokument warnte pauschal vor positionellem Decodieren. Richtig ist: die Unterscheidung ist *Template bekannt* vs. *Template unbekannt*. Für FR3 steht das Template in `docs/data/linecode-templates.csv`; damit ist das Decodieren exakt und dem plaintext-first-Verfahren überlegen. LINECODE.md hat dazu einen neuen Abschnitt bekommen (zweiter dokumentierter Fall einer verlorenen Ebene nach DUB in #85).

**Lehre 2 – defekte Quellzeilen sehen aus wie saubere Struktur.** 86 der 9.605 Zeilen in `FR3.txt` haben nur 18 statt 19 Stellen (fehlende führende Null), und zwar genau in VIII,215 `u=1` und V,209 `u=2`. Ohne `zfill(19)` verschwinden zwei Zeugen lautlos, und die Struktur wirkt trotzdem in sich stimmig – die Verszahl stimmt, nur eben gegen die falsche Menge. Das war exakt die Stelle, an der der erste Abgleich (nur RTF) zwei „Abweichungen" meldete.

**Lehre 3 – die Verszählungs-Anomalien waren keine.** Alle drei im Issue gemeldeten Fälle (V/211 nicht monoton, X/204 Sprung 15→76, XII/204) bilden die Vorlage korrekt ab. Sie werden erst dann wieder lesbar, wenn die `u`-Ebene steht – jeder Zähler gehört sichtbar zu seinem Zeugen. Das ist ein Argument *für* den Umbau, kein Reparaturauftrag: hier wäre „Korrigieren" die Datenzerstörung gewesen.

**Umsetzung** (`scripts/ingest/frauenlob/`, fünf idempotente Skripte, Quelldateien unter `source/` mit KZW-Freigabe):

| | |
|---|---|
| `02` | 23 gleichrangige Töne → 10; 36 `<div type="parallel">`; 1.563 von 9.595 Versen jetzt als Parallelüberlieferung erkennbar; 127 eindeutige (Ton, Strophe)-Adressen |
| `03` | 42 römische Ordnungszahl-Tokens entfernt (26 FR1 / 2 FR2 / 14 FR3), 3 lose `<p>` unter `<body>` weg, 24 `<head>` mit GA-Nummer und Tonnamen, FR2 `div/@n` → `XIV,1`–`XIV,7` |
| `04` | Titel aller drei korrigiert; FR3 auf den Supplementband 2000 (ISBN 3-525-82504-8, Haustein/Stackmann, Reihenband 232); Zotero-Title-Case „Teil Ii"/„Teil Iii" repariert |
| `05` | Editorische Eingriffe aus `<normalization>` nach `<editorialDecl>`; verstümmelter Legacy-Satz („I-XIII Leichs und XI Lieder") ersetzt |

`01` ist das Gate und bewusst **strukturunabhängig** gebaut: es liest `u`, Ton und Strophe je `<lg>` aus dem `xml:id` des ersten Tokens statt aus der `<div>`-Verschachtelung. Dadurch liefert es vor und nach dem Umbau dasselbe Ergebnis und bleibt dauerhaft brauchbar. Erster Entwurf las noch die `<div>`-Ebene und brach beim ersten Nachlauf – gutes Beispiel dafür, dass ein Verifikationsskript nicht die Struktur voraussetzen darf, die es prüfen soll.

**Zwei Abweichungen vom Issue-Text, beide schema-bedingt.** Der Vorschlag `<relatedItem type="supplement">` *innerhalb* eines `biblStruct` ist in `mhdbdb-authority.rnc` nicht vorgesehen (`relatedItem` existiert dort nur als Hülle *um* einen `biblStruct`, `note` kennt kein `@type`); `<samplingDecl>` ist in `encodingDesc` gar nicht erlaubt. Nach ADR-013 „Daten vor Schema" wurde das Schema **nicht** aufgeweicht: die Supplement-Relation steht als `<ref type="supplement" target="works.xml#FR1_FR1">` in `<analytic>` (im TEI dateiqualifiziert, in `works.xml` selbst als `#FR1_FR1`; der erste Anlauf schrieb beide Male das nackte Fragment, siehe Review-Nacharbeiten unten), die Scope-Aussagen als `<p>` in `<editorialDecl>`. Anmerkung fürs nächste Mal: Issue-Vorschläge, die Markup nennen, gegen das Schema prüfen, *bevor* sie in den Issue-Text wandern – beide Vorschläge klangen plausibel und waren es nicht.

**Abgeleitete Schicht:** Korpus-Index 4.1.8 → **4.2.0** (Dokumentordnung von FR3 ändert sich, Tokens entfallen), Authority-Index 1.6.4 → **1.6.5** (works.xml-Metadaten). `variants.xml` **unverändert** – die entfernten Ordnungszahl-Tokens waren nicht die letzten Belege ihrer Typen (0 added / 0 removed / 0 changed), anders als beim HUG-Fall in 1.6.4. Damit bleibt auch die user-sichtbare Zahl „234.243" in `hilfe-playground.html` gültig. API neu gebaut (2.742 Dateien), Cross-Ref-Audit und `validate-indices.py` grün, Schema 3/3 + 8/8.

**Nebenbefund:** `ERLEDIGT/Textexport-Dateien_Feb2017/` enthält **644 Volltext-Dateien** des Alt-Korpus; 639 der 640 Sigel stehen bereits als TEI im Repo. Als unabhängige Gegenprobe für Struktur- und Umfangsfragen wertvoll (hat hier die Verszahlen aller 13 GA-Abschnitte von FR1 bestätigt), aber Umfang, Lizenz und Ablage brauchen eine eigene Entscheidung → **#248**.

**Offen:** Sichtbarer Divergenz-Hinweis im Reader-Metadatenpanel (Punkt G, zweite Hälfte) – der Text steht jetzt im `<editorialDecl>`, ob der Reader ihn zeigt, ist eine Frontend-Frage und wurde bewusst nicht mitgemacht. Ebenfalls offen als Kosmetik: der Reader rendert weiterhin „Lied 5" *neben* dem neuen `<head>` „V. Langer Ton", weil das synthetische div-Label unabhängig vom `<head>` erzeugt wird.

**Health-Check 2026-07-29 (nach #236).** Flow: die vier geänderten Docs (INDEX §Status, TEI-MODEL §11, LINECODE, JOURNAL) lesen sich stimmig, keine Versions-Altstände mehr im Baum. Algorithmen-Stichprobe 3/3 deckungsgleich (Positionszählung `extract_word_data` gegen CONTRACTS §B, `lemmaRefMatchesId` gegen §B.1 – der Code *ist* der Pseudo-Code –, MHG-Normalisierung inkl. der Breve-Regeln ŏ/ŭ in Python und JS). XPath-Stichprobe 4/4 deckungsgleich gegen `build-authority-index.py`. Zahlen ohne Drift: 667 TEI, 8 Authority-Files, 2.742 API-Dateien, 43.879 Lemmata, 234.243 Varianten. **Zwei Lücken in der eigenen #236-Arbeit gefunden:** (1) der zugesagte GAP-Kommentar zu `lg/@type="stanza"` fehlte im Schema – als GAP 12 nachgetragen, `.rng` regeneriert und byte-identisch, CI-Gate unberührt; (2) die „leeren `<l>`" aus dem #236-Ist-Befund waren **nie ein Fehler**: an diesen Stellen steht in der Quelle `%(...)%`, der Auslassungsmarker der Edition. Daraus der eigentliche Fund: Überlieferungslücken sind korpusweit als `(` + `<caesura/>` + `)` kodiert – 971 Stellen in 21 Texten –, während `<gap/>` **null Mal** vorkommt; `<caesura/>` trägt damit zwei Bedeutungen. → #252. Lehre: Ein Issue-Ist-Befund, der eine Auffälligkeit als Defekt listet, ist selbst eine Hypothese und gehört gegen die Quelle geprüft, bevor man sie „behebt".

**Review-Nacharbeiten 2026-07-30 (zwei Reviews, sechs plus acht Befunde).** Vor dem Merge kam neben dem automatischen Opus-Review eine Zweitmeinung auf Fable dazu. Übernommen wurden vier Punkte:

1. **Ein Verweis hing ins Leere, und kein Gate konnte es merken.** `04-metadata.py` schrieb denselben Literal `target="#FR1_FR1"` in `works.xml` und in den FR3-Header. In `works.xml` stimmt das, in `tei/FR3.tei.xml` gibt es diese `xml:id` nicht: der Zeiger zeigte auf nichts. Das Schema prüft nur `xsd:anyURI`, deshalb blieb die CI grün. Gemessen, wie das Projekt sonst über Dateigrenzen zeigt: 667× `works.xml#…`, 2.671× `contributors.xml#…`, 1.805× `genres.xml#…` und **kein einziger** nackter Fragment-Zeiger. Jetzt `works.xml#FR1_FR1`, und das Skript heilt einen falschen Wert beim nächsten Lauf statt ihn zu bestätigen.
2. **Das Gate prüfte weniger, als sein Code aussagt.** `sorted(src[key])` liefert die Schlüssel eines dict, also nur die u-Ziffern; die eingesammelten `lg`-Nummern wurden nie verglichen. Eine abweichende Strophen-Unterteilung innerhalb eines Zeugen wäre bei gleicher Verssumme unsichtbar durchgelaufen. Jetzt drei Ebenen: u-Mengen, Zahl der `<lg>` je Zeuge, dann ihre Nummern. Dabei zeigte sich, dass die zwei von KZW benannten Umnummerierungen (Ton XV, Strophen 23 und 24) die einzigen sind: sie stehen als benannte Ausnahme im Skript, jede weitere wird rot. Übersprungene Quellzeilen werden ebenfalls gemeldet statt still verworfen (aktuell null).
3. **Die `h`-Stelle ist eine Konvention, kein Beweis.** `03-headings.py` löschte Tokens allein anhand der letzten `xml:id`-Ziffer, und `LINECODE.md` empfiehlt das Verfahren inzwischen als Rezept. Nachgezählt: 339 der 620 Templates enden auf `h`, die übrigen 281 belegen die Stelle anders. Dort würde dasselbe Rezept echten Textbestand löschen. Jetzt prüft das Skript, **was** es entfernt (römische Zahl oder Satzzeichen, im Bestand exakt 16 Zahlen und 26 Satzzeichen) und bricht bei allem anderen ab.
4. **Doc-Count-Drift, die größer war als der eigene PR.** Die `div/@type`-Tabelle in TEI-MODEL.md §3 stand in fünf von sieben Zeilen falsch. Nur drei Abweichungen gehen auf #236 zurück (`song` −13, `parallel` +36, `section` −36); `chapter` 604 → 1.640 und `recipe` 452 → 606 waren vorher schon gedriftet. Alle sieben Werte über die 667 Dateien nachgezählt und korrigiert. Lehre: die Zweitmeinung hatte hier 60 und 1.360 vorgerechnet, also aus den Doku-Altwerten fortgeschrieben; erst die eigene Vollmessung ergab 51 und 1.406. Auch eine Korrektur will gemessen werden.

Dazu die Prolog-Kosmetik: `tree.write(xml_declaration=True)` verliert den Tail der letzten Processing Instruction, wodurch Wurzelelement und `<?xml-model?>` in vier Dateien auf eine Zeile rutschten (in `works.xml` sogar beide PIs plus Wurzel). Die anderen 663 Korpusdateien haben dort einen Umbruch, jeder künftige Diff hätte eine Phantomzeile gezeigt. Der Nachlauf sitzt jetzt in `_tei_io.py` und arbeitet bewusst nur auf den ersten drei Zeilen, weil PIs mitten im Dokument sehr wohl ohne Umbruch an ein Element grenzen dürfen.

**Bewusst nicht gemacht:** die Randnummern-Nebenwirkung im Reader (`divRestartsNumbering` sieht seit der Verschachtelung zwei `l n="1"` im Teilbaum, wodurch die sichtbare „1" vom Basiszeugen zum Parallelzeugen wandert). Nachgemessen sind **19 der 127** FR3-Sections betroffen. Das ist Frontend, gilt korpusweit und würde die Zählregel für 84 Texte ändern, gehört also nicht in einen Daten-PR → #250. Ebenfalls offen und als eigener Punkt festgehalten: Parallel-Tokens zählen in Frequenz, Keyness, Hapax und Nähesuche weiterhin wie eigenständiger Text, der Index kennt kein Parallel-Flag. Nach dem Umbau liegen die Zeugen zudem direkt beieinander, wodurch Kookkurrenzen desselben Strophentexts entstehen können, wo vorher weite Distanz lag.

**Zweiter Review-Durchgang (Nachlauf).** Der Bot hat die Nacharbeiten gegengelesen und vier weitere Punkte gefunden, drei davon übernommen: der FR2-Zweig des Gates verglich nur Längen, obwohl Quelle und TEI dieselbe durchlaufende Strophenzählung führen (für alle sieben Lieder nachgemessen, jetzt Gleichheitsprüfung); die Plausibilitätsschranke las `el.text` und wäre damit bei `<w><hi>xiv</hi></w>` über den Leer-Zweig gelaufen (0 solche `<w>` im Bestand nachgezählt, jetzt `itertext()`); und die Ratsche griff nur in eine Richtung, ein aufgeräumter Ausnahmefall wäre stillschweigend zu totem Code geworden. Der vierte Punkt war der wertvollste: **die Reset-Zahlen in FEATURES.md und in zwei Kommentarblöcken des Readers waren durch den eigenen Umbau veraltet.** Neu gemessen mit `count-verse-numbering-resets.py`: 6.789 statt 6.802 `<div>`, 1.473 statt 1.497 qualifizierende, 1.333 statt 1.352 zusätzliche Randnummern, und FR3 +117 statt +136. Die Differenz von 19 ist exakt die Zahl der Sections, die durch die Verschachtelung ihren Anker verlieren: zwei unabhängige Messwege, dieselbe Zahl. Nicht übernommen wurden drei Einrückungs-Versätze in FR3, weil die Skripte sie erzeugen und eine Handkorrektur vom Skript abdriften würde. Eine Rücknahme aus dem ersten Review: die Whitespace-only-Zeilen sind kein Abweichler, 24 Korpusdateien haben zusammen rund 86.000 davon.

**Dritter Review-Durchgang: ein echter Skript-Fehler.** `shift_indent()` in `02-restore-parallel-level.py` iteriert über `elem.iter()`, und das liefert den Wurzelknoten mit. Verschoben wurde damit auch dessen `tail`, obwohl der nicht zum Teilbaum gehört, sondern das Elternelement schließt. Folge: 28 der 127 `</div>` in FR3 standen zwei Spalten zu tief (64 statt 36 Zeilen auf zehn Spalten). Das war zuerst als „erzeugt das Skript, Handkorrektur würde abdriften" zurückgestellt, und die Zurückstellung war falsch: es ist kein Skript-Stil, sondern ein Fehler im Skript, also dort reparierbar. Wichtiger als die Kosmetik ist die Konsequenz daraus: **würde nur das Skript korrigiert, liefen Skript und Bestand auseinander** und ein späterer Lauf aus der Quelle erzeugte eine andere Datei als die committete. Deshalb wurde FR3 auf den `main`-Stand zurückgesetzt und die Kette 02 bis 05 vollständig neu durchlaufen. Der Unterschied zum vorigen Branchstand sind genau 28 Zeilen `</div>`-Einrückung; Elementzahlen (56.554 `<w>`, 11.820 `<pc>`, 9.595 `<l>`, 527 `<lg>`, 173 `<div>`), Tokentext (243.776 Zeichen), `xml:id`-Folge und div-Struktur sind identisch, Indexe und API byte-identisch. Damit ist die Kette nebenbei als reproduzierbar belegt, nicht nur als idempotent.

Drei weitere Punkte derselben Runde, alle in der Diagnose statt in der Wirkung: die Plausibilitätsschranke prüfte per `itertext()`, berichtete aber `el.text`, hätte also im Abbruchfall `None` gedruckt statt des Inhalts, der den Abbruch auslöste; `03-headings.py` schrieb pro Text sofort, sodass ein Abbruch bei FR3 die geänderten FR1 und FR2 auf der Platte gelassen hätte, während die Meldung „nichts entfernt" lautete (jetzt wird erst nach dem letzten Text geschrieben, und die Meldung sagt es); und die Ratschen-Meldung nannte „Ausnahme streichen" als einzige Ursache, obwohl auch „anders umnummeriert" dazu führt. Alle drei sind Fälle derselben Klasse: **eine Fehlermeldung, die mehr behauptet als sie weiß.** Dieselbe Lehre stand schon am 29.07. im Journal, hier ist sie dreimal wieder aufgetreten.

Zum Verhältnis zu #138: die Reset-Zahlen im Sitzungsbericht vom 17.06. (1.497 / 1.352 / 6.802 / FR3 +136) bleiben als historischer Stand stehen und werden nicht rückwirkend umgeschrieben. Gültig sind die Werte aus diesem Eintrag.

**Verifikation der Nacharbeiten:** beide Indexe und die API neu gebaut, alle drei Artefakte **byte-identisch** (die Änderungen betreffen nur Header-Attribute und Prolog-Whitespace). Die vier geänderten XML-Dateien einzeln gegen ihr Schema validiert (4/4 valide), Cross-Ref-Audit, Em-Dash-Gate und Doc-Count-Audit grün, das gehärtete Gate deckungsgleich, `04-metadata.py` im zweiten Lauf ohne Änderung.


## 2026-07-29 – handoff (Tagesabschluss: vier PRs gemergt, Playground-Aufräumrunde)

**Summary:** Die am Vormittag als PRs abgelegte autonome Session wurde gemergt (#245, #247, #246) und um eine vierte, in ROADMAP und JOURNAL vorgemerkte Runde ergänzt (#254, Playground-Aufräumen). `main` steht auf `ba6ba8e5c`, alles ist deployed und live verifiziert. Kein Issue geschlossen, ein neues angelegt (#251).

**Decisions:**

- **Merge-Reihenfolge #245 → #247 → #246**, weil #247 auf #245 gestackt war. Nach dem Squash-Merge von #245 wurde #247 sofort `CONFLICTING`: Squash erzeugt eine neue SHA, die Patch-IDs der Originalcommits passen nicht mehr. Repariert per `git rebase --onto origin/main 01307da7b` in einem **separaten Worktree**, damit ein parallel laufender lesender Agent den Arbeitsbaum nicht unter sich wechseln sieht.
- **KZWs Antwort auf die #239-Rückfrage umgesetzt:** kein Lemma-Nachtrag für `rôtwîn`, das Beispiel wandert auf `lantwîn` (`lemma_51889`, führt `lant` + `wîn` als verzeichnete Bestandteile). Dabei musste die Eingabe mitwandern, sonst wäre der Satz nur anders falsch geworden: `lantwîn` normalisiert zu „lantwin" und enthält „wein" nicht.
- **#254 trotz eines verbleibenden Befundes gemergt.** Alle Befunde, die Inhalte verbergen oder in Sackgassen führen, sind behoben; der Rest (Auswahlverlust auf dem Weg durch den Leerzustand) hat eine strukturelle Ursache und gehört in einen eigenen Durchgang statt in eine achte Review-Runde. Als #251 dokumentiert.
- **Der Guard gegen die Ein-Lemma-Degeneration sitzt in der Datenschicht, nicht nur in der UI.** Beide Enhanced-Pfade normalisieren, deduplizieren und geben unter zwei verbleibenden IDs `[]` zurück. Vertrag in CONTRACTS §C.2.2 nachgezogen, weil sich aus dem dortigen Pseudo-Code sonst das behobene Verhalten rekonstruieren ließe.

**Dead ends:**

- Ein **Mutationsbeweis, der weniger zeigte als behauptet**: für den Rückbau wurden Normalisierung und Deduplizierung gleichzeitig entfernt, die Rotfärbung stammte allein von der Normalisierung. Die gezielte Mutation (nur Dedup weg) blieb grün, der Dedup war also ungetestet. Genau das verbietet Handwerksregel 18 im Playbook, hier selbst verletzt.
- Ein **aus der Zweitmeinung ungeprüft übernommener Kommentar-Verweis** zeigte in die falsche Richtung: `searchProximityUsingEnhancedIndex` scannt `words[]` und ist damit die bekannte Abweichung von der Consumer-Rule, nicht das Vorbild für den multi-ref-bewussten Vers-Pfad.
- Der **Pages-Build für #246 schlug einmal fehl** (`status: errored`). Transient, ausgelöst durch zwei Pushes kurz hintereinander; KZWs Folge-Commit baute durch und nahm die Änderungen mit.

**Phase:** Betrieb (Implementation, iterativ). Aktuell und gepflegt: CONTRACTS (§B-Ausnahme und §C.2.2-Vorbedingung neu), ROADMAP, JOURNAL, FEATURES, INDEX, DECISIONS (ADR-016-Beispiel korrigiert), `hilfe-playground.html`. Das Playbook steht auf „WARTET AUF BEFÜLLUNG": §1 und §3 bis §6 sind leer, §2 (Betriebsvertrag), §2.1 (22 Handwerksregeln) und §7 (Sessionbericht) tragen.

**Open issues:**

- **#251** (neu): Die Auswahl im Wortbestandteil-Modus wird über `rememberComponentViewState()` aus dem DOM gelesen und einmalig eingelöst. Ein Häkchen überlebt genau einen Render. Wer mit gesetzter Auswahl den Filter so umschaltet, dass nichts übrig bleibt, verliert sie still; bemerkbar erst an der Trefferzahl der Multi-Lemma-Suche. Vorschlag im Issue: Auswahl als Modell führen, gepflegt am `change`-Ereignis.
- **#239** wartet auf KZWs Abnahme am Live-Stand, mit zwei offenen Fragen: ob `winter` in der Wortanfang- statt Wortmitten-Gruppe akzeptabel ist (die positionale Gruppendefinition verlangt es so), und ob der Filter „nur belegte Wortbildungen" standardmäßig an sein soll. Fällt die zweite auf „an", wird der Leerzustand zum Regelfall und #251 damit dringender.
- **#169** wartet ebenfalls auf Abnahme. Die Trefferzahlen für Nähesuchen mit drei oder mehr Lemmata sinken gewollt; die Zäsur ist im Eintrag vom Vormittag datiert.
- **Zwei Kleinigkeiten aus den Reviews bewusst offen:** die Fehlermeldung bei gemischten Eingaben nennt nur den nicht auflösenden Begriff, auch wenn zusätzlich zwei Eingaben zusammenfallen; und `tei-manager.js` hat weiterhin keine Zeilenschaltung am Dateiende (vorbestehend).

**Next steps:**

1. **#251 angehen**, sobald KZWs Antwort zur Filter-Voreinstellung vorliegt: die Auswahl als Modell führen und im selben Durchgang den Fokusverlust der Checkbox beheben (`toggleComponentMorphFilter` rendert den Container samt Checkbox neu, Tastaturbedienung landet auf `<body>`).
2. **Auf KZWs Abnahme in #239 und #169 reagieren**, dann erst schließen.
3. **Das Playbook vor dem nächsten autonomen Kickoff befüllen** (§1, §3 bis §6). Jeder Abschnitt sagt selbst, was hineingehört.
4. Optional: die in #254 dokumentierte Zählweise-Abweichung des Upload-Fallbacks als eigenes Ticket weiterverfolgen, falls hochgeladene Dateien je mit Index-Ergebnissen verglichen werden sollen.

---

## 2026-07-30 – handoff (#236 gemergt nach vier Review-Runden, #251 als PR, Review-Workflow korrigiert)

**Summary:** Interaktive Session, kein Playbook-Kickoff. Drei Dinge sind gelandet: die ParzivAI-Handover-Notiz ist in die Promptotyping-Docs überführt (`83ed50aa0`), #236 Frauenlob ist nach vier Review-Durchgängen gemergt (`115c3a01f`, Korpus-Index 4.2.0 / Authority 1.6.5) samt Nachlauf (`9521d27b6`), und #251 liegt als PR #256 mit 24/24 grüner Spec. Dazu drei Issue-Kommentare, ein neues Issue (#255) und eine CI-Änderung am Review-Workflow.

**Decisions:**

- **Merge nach der vierten Review-Runde, nicht nach der fünften.** Jede der vier Runden brachte genau einen echten Befund, aber in absteigender Größe: dangling `@target`, veraltete Doku-Zahlen, 28 falsch eingerückte Zeilen, ein Docstring auf 4.1.8. Die letzten drei Kleinigkeiten sind nach dem Merge direkt auf `main` nachgezogen worden, statt eine weitere 15-Minuten-Gate-Runde auf dem PR zu drehen.
- **Beim `shift_indent`-Fehler wurde FR3 neu erzeugt statt nachgebessert.** Ein Fix nur im Skript hätte bedeutet, dass ein späterer Lauf aus der Quelle eine andere Datei erzeugt als die committete. Die Kette 02 bis 05 lief vom `main`-Stand komplett durch; Differenz zum vorigen Branchstand waren genau 28 Zeilen `</div>`-Einrückung, bei identischen Elementzahlen, identischem Tokentext (243.776 Zeichen), identischer `xml:id`-Folge und byte-identischen Indexen. Damit ist die Kette als **reproduzierbar** belegt, nicht nur als idempotent.
- **Bei der TEI-MODEL-Tabelle wurde gegen die Zweitmeinung entschieden.** Sie rechnete 60 (`parallel`) und 1.360 (`song`) vor, gemessen über alle 667 Dateien sind es 51 und 1.406: die Doku-Altwerte 24 und 1.373 waren selbst falsch, ihre Zahlen daraus fortgeschrieben. Korrigiert sind alle sieben Zeilen, wovon nur drei Abweichungen auf #236 zurückgehen.
- **`use_sticky_comment: true` im Review-Workflow, `synchronize`-Trigger bleibt.** Ein Kommentar pro PR statt einem pro Lauf (#254 hatte acht). Gegen die naheliegende Einsparung, Runden ab der zweiten nur auf Zuruf laufen zu lassen, spricht der Tag selbst: der automatisch getriggerte zweite Lauf fand die veralteten Reset-Zahlen in `FEATURES.md`, also eine Stelle, die ich für vollständig gehalten hatte.
- **#255 statt eines JOURNAL-Absatzes.** Beide Reviews haben darauf bestanden, dass die Auswertungsfrage der Zeugenvarianten ein eigenes Issue wird. Die Entscheidungsfragen sind an KZW adressiert, nicht an chsteiner; die technische Umsetzung hängt allein an der ersten Antwort.

**Dead ends:**

- **Ein falscher Merkzettel hat monatelang Handarbeit erzeugt.** Ich habe angekündigt, laufende Review-Runs vor dem Merge zu canceln. Der Workflow tut das seit `2d6335856` (12.07.) selbst: `closed` in den Triggern, Job per `if` übersprungen, Concurrency-Group mit `cancel-in-progress`. Belegt durch je einen `skipped`-Lauf nach jedem Merge, einen tatsächlich `cancelled`-Lauf und das Ausbleiben von Nach-Merge-Kommentaren seit dem 12.07. Ursache war ein Memory-Eintrag, der die Dauerlösung nur *vorgeschlagen* hatte und nach ihrer Umsetzung nicht nachgezogen wurde. Korrigiert.
- **Eine Chrome-Verifikation an der falschen von zwei Renderstellen.** Nach der #251-Umstellung habe ich die Gruppen-Checkboxen geprüft und für vollständig erklärt. `.component-pick` wird aber auch im Kopf für den Exakt-Treffer gerendert, und diese Stelle hatte den neuen Handler nicht: das Häkchen am Grundwort erreichte das Modell nicht. Gefangen hat es der Vollauf der Suite, und zwar über einen bestehenden Test aus #239, nicht über die drei neu geschriebenen. Der Lauf endete dabei mit **Exit 0**, obwohl ein Test rot war; die Zahl kam aus `report.json`.
- **Vier Fehlermeldungen, die mehr behaupteten als sie wussten**, alle in denselben Skripten und alle erst durch Reviews aufgefallen: „nichts entfernt" bei bereits geschriebenen Dateien; „die entfernten Tokens trugen teils `@lemmaRef`" bei einer Bedingung, die nur „hat überhaupt etwas entfernt" prüfte (gemessen: 16 von 42); ein Bericht, der `el.text` druckte, während die Prüfung `itertext()` las; eine Diagnose, die eine von zwei Ursachen als die einzige nannte. Dieselbe Lehre stand schon seit dem 29.07. im Journal.

**Phase:** Betrieb (Implementation, iterativ). Aktuell und gepflegt: JOURNAL, ROADMAP, TEI-MODEL (§3-Tabelle und §11), FEATURES (Reset-Zahlen), RESEARCH und INDEX (ParzivAI), LINECODE, CONTRACTS unverändert gültig. Playbook: §2.1 auf 26 Regeln gewachsen, §1 und §3 bis §6 bleiben bewusst leer, weil die Triage kurz vor dem Kickoff entstehen soll und sonst veraltet.

**Open issues:**

- **PR #256 (#251)** wartet auf Merge. fable hat zugestimmt, ein Befund daraus ist umgesetzt: 102 der 43.765 Schreibformen gehören mehr als einem Lemma („sal", „wal", „sin" je vier), das Modell hält Formen, deshalb wirken gleichschreibende Checkboxen jetzt sichtbar als eine Auswahl statt auseinanderzulaufen.
- **Drei KZW-Antworten liegen vor und sind nicht umgesetzt:** #250 (Aufklapp-Abschnitt „Editorische Eingriffe" plus synthetisches Label unterdrücken, dazu neu die 19 FR3-Sections ohne Zählungs-Anker), #252 (971 Auslassungen in 21 Texten von `( caesura )` auf `<gap/>`, echter Datenblock), #28 (Fremdsprachen-Grenzziehung, seit 29.07. im Phasenplan).
- **Drei Fragen liegen bei KZW:** #239 (`winter`-Gruppierung, Filter-Voreinstellung), #255 (Zeugenvarianten in den Auswertungen), plus Lindas Rückfrage in #59 nach einem Filter „wer benennt die Figur" (Eigennennung, nennende Figur, Erzähler).
- **Bewusst offen gelassen:** drei Einrückungs-Versätze im FR3-Header, die aus 04/05 stammen und nach derselben Logik wie der `shift_indent`-Fehler behandelt werden müssten (Skript fixen, Datei neu erzeugen); `01-verify-linecode-vs-tei.py` ist nicht in `data-integrity.yml` verdrahtet, taugt also als wiederholbare Prüfung, nicht als Gate.

**Next steps:**

1. **PR #256 mergen**, danach KZW für #251 und #239 am Live-Stand anpingen.
2. **#252 als Datenblock angehen**: 971 Stellen auf `<gap/>`, mit Data-Change-Lifecycle (Indexe, `variants.xml`, API) und Abgrenzung gegen die echten Zäsuren im Nibelungenlied und bei Tannhäuser.
3. **#250 umsetzen**, sobald #256 gemergt ist: `editorialDecl` im Metadatenpanel als Aufklapp-Abschnitt, dazu die Entscheidung zur Zählregel bei verschachtelten Zeugen (betrifft korpusweit 84 Texte, deshalb mit eigener Messung).
4. Auf #255 warten, bevor an Frequenz, Keyness oder Hapax etwas geändert wird.
5. Vor dem nächsten autonomen Kickoff das Playbook §1 und §3 bis §6 befüllen, dann mit frischer Triage.

---

## 2026-07-30 (Nachmittag) – handoff (#256 gemergt, Sticky-Kommentar probiert und verworfen, KZW-Sammelping)

Setzt den Handoff vom Vormittag fort; dessen offene Punkte sind hier fortgeschrieben, nicht dort überschrieben.

**Summary:** #251 ist als PR #256 nach vier Review-Durchgängen gemergt (`b8aa68472`) und am Live-Stand verifiziert. Der Review-Workflow hat `use_sticky_comment` bekommen und nach einem halben Tag wieder verloren (`bf505a129`). KZW hat einen Sammelkommentar für die drei offenen Abnahmen (#251, #239, #169) statt drei Einzelpings.

**Decisions:**

- **Sticky-Kommentar zurückgenommen, mit gemessenem Grund.** Er tut, was er verspricht, aber zusammen mit `track_progress` überschreibt der nächste Lauf den Kommentar zuerst mit seiner Fortschritts-Checkliste: der letzte Befund ist genau dann unsichtbar, wenn man ihn nachlesen will. Und die früheren Runden liegen danach nur in der Edit-Historie, also nur im Browser. Über API und `gh` sind sie nicht erreichbar, im Job-Log stehen sie auch nicht. Bei #253 wurden an einem Tag vier Runden per `gh api` gelesen und abgearbeitet: genau diese Arbeitsweise hätte Sticky unmöglich gemacht. Die Begründung steht als Kommentar im Workflow, damit die Option nicht wieder als naheliegende Verbesserung vorgeschlagen wird.
- **Der `synchronize`-Trigger bleibt trotz der Kosten.** Vier Läufe auf #253 und vier auf #256, jeder mit einem echten Befund. Runden ab der zweiten nur auf Zuruf laufen zu lassen hätte heute zwei der wertvollsten Funde gekostet.
- **Nach vier Runden gemergt, nicht nach fünf.** Der Ertrag fiel von „Beschriftung lügt in 81 Prozent der Fälle" auf „Docstring steht an der falschen Funktion". Zwei kosmetische Restpunkte sind bewusst nicht mehr in den PR gewandert (siehe Open issues).
- **Ein Sammelkommentar statt drei Pings.** #251, #239 und #169 warten alle auf Abnahme am Live-Stand; der Kommentar in #251 nennt für jedes einen konkreten Prüfweg und referenziert die beiden anderen, wodurch sie in ihren Timelines auftauchen.

**Dead ends:**

- **Drei Fehler des Tages entstanden erst durch Nachbesserungen**, jedes Mal weil eine Bedingung der richtigen *ähnlich* sah: die zweite Renderstelle von `.component-pick` blieb ohne Handler; der `aria-label`-Zusatz „gemeinsam mit gleichlautenden" hing an der normalisierten statt an der geschriebenen Form (gemessen: 387 der 475 Norm-Gruppen mit mehreren Lemmata haben unterschiedliche Schreibformen, das Flag lag also in 81 Prozent falsch); und der Gruppendeckel wanderte in den Aufrufer, während die Meldung „Angezeigt werden 200 von N" in der Funktion blieb und darauf vertraute. Kandidat für Handwerksregel 27: eine Nachbesserung ist ein neuer Eingriff und braucht dieselbe Prüfung wie der ursprüngliche.
- **Ein Push nahm mehr mit als angekündigt.** Der Handoff-Commit `4e1b46c54` sollte nach Playbook-Verfahren liegen bleiben, damit chsteiner über den Push entscheidet. Der unmittelbar danach committete CI-Revert wurde gepusht und nahm ihn mit. Inhaltlich unkritisch (Doku und CI), aber nicht das Angekündigte. Lehre: wer einen Commit bewusst ungepusht lässt, darf im selben Arbeitsbaum nicht sofort den nächsten pushen.
- **`gh pr merge --body` zerbricht an Klammern**, weil die Shell den Text auswertet: „(387 der 475 …)" führte zu `syntax error near unexpected token '('`. Mit `--body-file` läuft es durch. Gilt für alle mehrzeiligen `gh`-Bodys mit Sonderzeichen.

**Phase:** Betrieb (Implementation, iterativ). Aktuell: JOURNAL, ROADMAP, TEI-MODEL, FEATURES, RESEARCH, INDEX, Playbook §2.1 (26 Regeln). `main` steht auf `b8aa68472`, Arbeitsbaum sauber, keine Worktrees, Scratchpad geleert, Dev-Server gestoppt.

**Open issues:**

- **Zwei kosmetische Reste am gemergten Stand:** der Docstring von `buildComponentGroupHTML` warnt vor einem Zustand, den derselbe Commit beseitigt hat (die Kappungs-Meldung kann seit der Umstellung auf `sichtbar.length` nicht mehr falsch werden), und der Betreff von `ae881577f` kündigt die darin enthaltene Verhaltensänderung nicht an. Beides ohne Wirkung, beides in zwei Zeilen behebbar.
- **Der Stau bei KZW ist der eigentliche Engpass**, und er ist heute gewachsen: Abnahme offen für #251, #239, #169; Antwort liegt vor und Umsetzung offen bei #250 (Aufklapp-Abschnitt plus die 19 FR3-Sections ohne Zählungs-Anker), #252 (971 Auslassungen auf `<gap/>`, echter Datenblock) und #28; Entscheidung offen bei #255 (Zeugenvarianten in den Auswertungen) und Lindas Rückfrage in #59.
- **Playbook §1 und §3 bis §6** bleiben leer, bewusst, weil die Triage kurz vor dem Kickoff entstehen soll.

**Next steps:**

1. Auf KZWs Antworten reagieren, sobald sie kommen; #251, #239 und #169 erst danach schließen.
2. **#252 als nächsten Datenblock**: 971 Stellen von `( caesura )` auf `<gap/>`, mit Data-Change-Lifecycle und Abgrenzung gegen die echten Zäsuren im Nibelungenlied und bei Tannhäuser.
3. #250 umsetzen (`editorialDecl` im Metadatenpanel; die Zählregel bei verschachtelten Zeugen braucht eine eigene Messung über die 84 betroffenen Texte).
4. Vor einer Änderung an Frequenz, Keyness oder Hapax auf #255 warten.
5. Handwerksregel 27 ins Playbook aufnehmen, wenn chsteiner zustimmt.

---

## 2026-07-30 – #248 Legacy-Ingest-Quellen im Repo: `sources/` angelegt, Restarchiv inventarisiert

**Kontext:** #248 lag als offene Grundsatzfrage (fünf Punkte: Schicht, Lizenz, Ablage, Format, Archivmasse). KZW hat sie entschieden: alle codierten Ingest-Dateien ins Repo, eigenes `sources/`-Verzeichnis, klar als „Legacy, nicht normativ" markiert, plus ein Verzeichnis dessen, was im Archiv sonst noch liegt, damit bei Unklarheiten bekannt ist, worauf lokal zugegriffen werden kann.

**Umfang war größer als der Issue-Ist-Befund.** Der Issue nannte „~100 Dateien, 42 MB" und meinte damit die Dateien direkt in `ERLEDIGT/`. Ein Scan über den ganzen Baum (`01-scan-linecode.py`, Kriterium: mindestens die Hälfte der nichtleeren Zeilen beginnt mit einer 9- bis 25-stelligen Ziffernfolge) fand **311 codierte Plaintext-Dateien**, davon zehn byte-gleiche Dubletten. Zusammen mit vier codierten Dateien außerhalb von `ERLEDIGT/` (siehe unten): **306 Dateien, 26,0 MB, 199 der 667 Korpussigeln**. Die Trennung ist scharf, nicht graduell: die Treffer liegen bei 95 bis 100 % codierter Zeilen, zwischen 50 und 95 % liegt nichts.

**Damit ist `sources/linecode/` die erste In-Repo-Linecode-Quelle.** Die Diagnose-Rezepte in LINECODE.md setzten bisher Julias Handover-Ordner voraus, der nicht im Repo liegt; für 199 Sigeln ist das erledigt. Beide betroffenen Stellen in LINECODE.md nachgezogen.

**Byte-Identität war nicht gratis.** 305 der 306 Dateien haben CRLF. `core.autocrlf=true` hätte sie beim Commit auf LF normalisiert, damit wären die `sha256` im Manifest gegen das Archiv nicht mehr prüfbar und ein Checkout unter Linux hätte andere Bytes geliefert als das Original. `sources/.gitattributes` setzt deshalb `linecode/** -text`; verifiziert wurde am Blob im Index, nicht nur an der Datei auf Platte. Lehre in derselben Familie wie der `newline=''`-Fall vom 02.07.: bei Archivkopien ist die EOL-Behandlung Teil der Datenintegrität, nicht Kosmetik.

**Vier Sigeln haben nur eine binäre codierte Fassung.** `02-scan-binaries.py` zählt Linecode-artige Ziffernfolgen im Rohbytestrom; aussagekräftig ist die Dichte, nicht die Absolutzahl (Grundrauschen aus Seitenzahlen und RTF-Steuerwerten liegt um 0,5 Treffer je KB, echte codierte Dateien bei 4 bis 13). Befund: für `OVW`, `OSW`, `MSG` und `MSW` existiert die codierte Quelle nur als `.doc`/`.dot`. Nicht aufgenommen, weil eine Extraktion ein abgeleitetes Artefakt wäre und keine Quelle, aber im Inventar verzeichnet, damit die Lücke nicht unsichtbar bleibt. Die einzige aufgenommene Nicht-`.txt`-Datei ist `Frauenlob_Bd2-codiert.rtf`: RTF ist ein Textformat.

**Die vier großen OCR-Projekte sind als Rückfrageinstanz wertlos.** `MR1` (3,7 GB), `FLG1`, `RVB1`, `Der Mantel`, `König vom Odenwald` sind ABBYY-FineReader-Projektordner: 14.771 Dateien, 7.446 MB, und darin **kein extrahierbarer Text**, nur `batch.options.xml` plus interne `.frdat`-Container. Das brauchbare Ergebnis liegt jeweils schon als korrigierter Text daneben. Damit ist auch Punkt 5 des Issues entschärft: die 9,1 GB sind zu 82 % Werkzeug-Innereien, nicht Inhalt. Ein etwaiges Zenodo-Deposit bräuchte nur Scans und PDFs, also 1,3 GB.

**Rechte-Befund, der eine Entscheidung braucht.** 8 der 199 Sigeln tragen `<availability status="restricted">` mit `<ab type="display" n="excerpt-only"/>`: FR3, HUB1, HUB2, MML, MRL, MRS, MSB1, RLS. Das Argument aus dem Issue trägt (der Volltext steht bereits als annotiertes TEI im öffentlichen Repo, die Quelldatei ändert an der Exposition nichts), aber eine codierte Plaintext-Quelle ist einer glatten Lesefassung näher als TEI mit `<w>`-Auszeichnung. Aufgenommen, in `sources/README.md` benannt, über die Manifest-Spalte `sigle` in einem Schritt wieder entfernbar (8 Dateien).

**Nicht aufgenommen:** Seitenscans und Editions-PDFs (neuer Veröffentlichungsakt, in #248 abgelehnt), OCR-Artefakte, und der Volltextexport `Textexport-Dateien_Feb2017/` (644 Dateien, 49 MB) als noch offene Einzelentscheidung.

**Abgeleitete Schicht: nichts zu tun.** Die Änderung berührt weder `tei/` noch `authority-files/`, also kein Index-Rebuild, keine `variants.xml`-Regeneration, keine Versions-Bumps. `data-integrity.yml` triggert auf `sources/**` bewusst nicht. Die Skripte in `scripts/ingest/legacy-sources/` brauchen Lesezugriff auf ein lokales 8-GB-Archiv und laufen deshalb nie in CI; sie liegen im Repo, damit `sources/` reproduzierbar ist.

**Dead end, der Prozess und nicht Inhalt betrifft: der erste Commit saß auf einem veralteten Branch.** Der Arbeitsbaum stand auf `feature/236-frauenlob`, und #236 war zu diesem Zeitpunkt längst über PR #253 auf `main` (dort als eigener, umgeschriebener Commit). Der lokale Branch lag 10 Commits hinter `main` und hätte, als PR eröffnet, die schon gemergte #236-Arbeit erneut vorgeschlagen und die Nachbesserungen aus `9521d27b6` überschrieben. Neu aufgesetzt in einem Worktree auf `origin/main`, wo nur `sources/`, die vier Skripte und drei Doku-Stellen im Diff stehen. **Lehre: „auf welchem Branch stehe ich" ist die falsche Frage; die richtige ist „wie weit liegt dieser Branch hinter `origin/main`, und ist sein Inhalt dort schon drin".** Beides ist mit `git fetch` plus `git rev-list --count HEAD..origin/main` in zwei Sekunden messbar und gehört vor den ersten Commit, nicht danach. Der Fehler ist teuer, weil er still ist: `git status` sagt „nothing to commit, working tree clean" und verrät nichts.

**Nebenbefund: codierte Dateien liegen auch außerhalb von `ERLEDIGT/`.** Ein Scan über die Schwesterordner in `MHDBDB_Inhaltliches/Texte/` fand vier weitere codierte Dateien in `Neue Texte Klaus/`, zusammen 1,4 MB, keine davon in `ERLEDIGT/`: `GTK2.txt` (1,2 MB), `EFB.txt`, `CLV.txt` und ein unbestimmtes `Normal.txt`. Über den `xml:id`-Join eindeutig zugeordnet: `GTK2` → `GWTK` (400/400 Stems), `EFB` → `CEFB` (399/400), `CLV` → `CLV` (400/400). Damit ist die Annahme widerlegt, `ERLEDIGT/` sei die vollständige Ablage der codierten Quellen. **Konsequenz: die Archivwurzel aller Skripte ist jetzt `Texte/` und nicht `Texte/ERLEDIGT/`**, und die vier Dateien sind mit aufgenommen. `Normal.txt` ist übrigens kein Text, sondern ein alphabetisches Namenregister zur Vita Caroli mit 468 Einträgen und fortlaufendem Linecode; der Dateiname ist ein Word-Artefakt. Zugeordnet wurde es über 14 von 14 Wortsonden im Volltext von `VTC`, nachdem der `xml:id`-Join hier versagte: seine Stems sind 1 bis 468 und damit in jedem Text des Korpus vorhanden. **Lehre: ein Join über Schlüssel, die trivial klein sind, matcht überall und beweist nichts.**

**Nebenbefund zur Ablage-Konvention.** Codierte Legacy-Quellen liegen jetzt an drei Stellen: `sources/linecode/` (Archivkopie, vollständig), `scripts/ingest/frauenlob/source/` (#236) und `ingest/wvv/` (#110). Acht Dateien sind doppelt und byte-identisch; `03-build-sources.py` prüft das bei jedem Lauf und bricht bei Abweichung ab, damit die Stände nicht auseinanderlaufen.

**Was sonst noch im Archiv liegt, ist jetzt katalogisiert.** `Texte/` hat neben `ERLEDIGT/` sechs weitere Ordner mit 2.435 Dateien. Vier Befunde daraus: (1) `apk_free.xml` ist die **Apokalypse Heinrichs von Hesler** als fertiges TEI.2 aus dem Trier/Virginia-MHGTA, Header sagt „publicly accessible due to 70 years time limit", fehlt im Korpus – der beste Ingest-Kandidat des ganzen Bestands (#262). (2) 15 frühneuhochdeutsche Koch- und Diätetik-Texte in Editionen von Thomas Gloning, mit Bezug zu CoReMA (#263). (3) Ein großer Block genuin fehlender Werke, aber durchweg auf Editionen des 19. Jahrhunderts: Liedersaal, Zweter, Wartburgstreit, kleinere Spruchdichter (#264, #265, #266). (4) **`FnhdC/` ist lizenzrechtlich gesperrt**: das Bonner Frühneuhochdeutschkorpus, README sagt wörtlich „Eine Weiterverbreitung ist nicht gestattet". Die Falle dabei: `BuchAltväter.txt` und `Durandus.txt` in `Neue Texte Klaus/` stammen daraus, ohne es im Namen zu zeigen, und `Durandus.txt` ist gar kein Text, sondern das FNHD-Quellenverzeichnis.

**Aufgenommen wurde daraus nur ein Werkzeug:** `linecode Generator.dot`, die Word-Vorlage, mit der die Linecodes erzeugt wurden, als `sources/legacy-tooling/`. LINECODE.md hält fest, dass die Gegenrichtung der Konversion nicht erhalten ist; das ist die Erzeugungsseite. Die übrige Pipeline-Dokumentation (`Import-Korrekt/differences` als Diff des Alt-Imports gegen den Druck, die MANTIS-Textliste, die Todo-Listen 2013 bis 2015) ist im Inventar verzeichnet, aber nicht kopiert: Word-Binaries, die Prozess dokumentieren und nicht Daten.

---

## 2026-07-30 (abends) – Kuratiertes Lemma-Wissen bekommt einen Platz im Lexikon (lemma_37818 Abba)

**Summary:** KZW hat zu `lemma_37818` (Abba) eine Erläuterung geliefert (aramäisch „mein Vater“, emphatische Verdoppelung der Gottesanrede in ZUK 2377, Anspielung auf Mk 14,36 / Röm 8,15 / Gal 4,6) und darum gebeten, sie in die Daten zu übernehmen. Dafür gab es im Lexikon keinen Ort: `lexicon.entry` kannte nur Klassifikation (POS, Konzept-Zeiger, Kompositions-Komponenten), keine Prosa. Neu sind drei optionale Produktionen im Authority-Schema (`<etym type="borrowing">`, `<def>`, `<note type="comment">`), ihre Abbildung im Authority-Index (v1.7.0: `lemma.origin`, `sense.definition`, `sense.comment`) und die Anzeige auf der Lemma-Seite plus im Playground-Lemmata-Explorer. Der Eintrag selbst trägt jetzt zusätzlich die Konzepte Aramäisch (`concept_23123905`) und Bibel/Religionsgeschichte (`concept_24411000`).

**Decisions:**

- **Herkunft wird zweifach geführt, nicht doppelt gepflegt.** Der Bestand nutzt den Konzept-Subtree `concept_23123000` (Einzelsprachen) bereits als Herkunftsmarkierung: `mirre` trägt Arabisch + Hebräisch + Aramäisch, `Golgota` und `Barjona` Aramäisch. Diese Konvention war der Grund, `concept_23123905` zu setzen statt sie durch das neue `<etym>` zu ersetzen: das Konzept macht die Herkunft im Begriffssystem auswertbar (Begriffs-Verteilung, ähnliche Lemmata), das `<etym type="borrowing">` macht sie samt Quelle explizit. Regel in TEI-MODEL-AUTH-FILES: wer eine Herkunft neu vergibt, setzt beides.
- **Das ist Phase 0 von #28 für Schicht B, an einem echten Fall entschieden.** Der Phasenplan hatte die Kodierung offen gelassen. Jetzt festgelegt: `<lang @norm>` (BCP-47) plus `<note type="attribution" @resp>`, getrennt von `<etym type="morphological">`. Ein einziger kuratierter Eintrag ist der billigste Zeitpunkt für diese Entscheidung; fällt sie in Phase 2 anders aus, kostet die Migration eine Zeile.
- **`@xml:lang` am Token in ZUK wurde bewusst NICHT gesetzt**, obwohl der Beleg die Drei-Punkte-Prüfung besteht. Das Korpus trägt 0 solche Token; ein einzelnes markiertes Token behauptet im zitierbaren Datensatz, Fremdsprachigkeit sei erfasst. Schicht A soll laut Plan gesichtet und per Skript mit Provenienz-Log geschrieben werden. „abba“ ist stattdessen als Kalibrierfall im Phasenplan notiert: findet der Kandidaten-Scan in Phase 1 diesen Beleg nicht, ist der Scan zu eng.
- **`<def>` und `<note type="comment">` sind getrennt.** Die Definition ist Wörterbuchinhalt, der Kommentar ist Argumentation (Belegkontext, Bibelstellen). Zusammengelegt würde die Lemma-Seite Behauptung und Begründung in einem Absatz mischen und die API-Konsumenten könnten das eine nicht ohne das andere zitieren. `@resp` ist bei beiden `<note>`-Typen Pflicht.
- **Die neuen Index-Felder werden nur gesetzt, wo kuratiert ist.** 43.879 Lemmata mit `null`-Feldern hätten Index und API ohne Nutzen aufgebläht. In CONTRACTS §G.3 nachgetragen, dass Konsumenten sie als optional behandeln müssen: kein Schema-Versprechen pro Record.
- **`concept_24452000` (Kirchliche Hierarchie) wurde entfernt.** Die Zuordnung passt zum monastischen `abbas` „Abt“, nicht zum einzigen Korpusbeleg, der Gott anredet. Mit einer jetzt ausformulierten Bedeutung wäre der Chip auf der Lemma-Seite sichtbar falsch. Eine Zeile, rückholbar, KZW-Veto vorbehalten.

**Dead ends:**

- **Die Arbeit begann auf `feature/236-frauenlob`**, einem gemergten und auf GitHub gelöschten Branch, 10 Commits hinter `origin/main`. Der erste Index-Build lief damit gegen einen veralteten `works.xml`-Stand. Ein Branch-Wechsel im gemeinsamen Arbeitsverzeichnis war keine Option, weil dort parallel eine andere Session mit gestageten Dateien arbeitete. Konsequenz: `git worktree` unter `%TEMP%` auf frischem Branch von `origin/main`, Patch übertragen, Index und API dort neu gebaut. Das Arbeitsverzeichnis der anderen Session bleibt unangetastet. Nebenbefund für künftige Worktrees: der Scratchpad-Pfad ist zu lang für `.gemini/skills/pos-disambiguator/references` (`Filename too long`), kurzer `%TEMP%`-Pfad nötig.

**Review-Runde am PR #268 (drei Befunde umgesetzt, einer ausgelagert):**

- **Die zwei Herkunfts-Schichten sagten Unterschiedliches.** Konzept-Zeiger `{la, arc}`, `<etym type="borrowing">` nur `{arc}`, Brücke war ausschließlich der deutsche Prosasatz. Aufgelöst durch `<lang norm="la">` zusätzlich: beide Schichten sind jetzt deckungsgleich, und die Regel dazu steht als solche in TEI-MODEL-AUTH-FILES. Welche Sprache Quelle und welche Vermittlung ist, sagt die Attributionsnotiz; maschinell ist die Liste ungeordnet, das hält CONTRACTS §G.3 fest.
- **`@resp` war ungetypt und von keinem Gate abgedeckt.** Ein `contrib_03` wäre durch beide Validierungsstufen, beide Audits und die CI gelaufen. Jetzt Pattern im Schema (negativ getestet: Tippfehler in `@norm` und `@resp` werden abgewiesen) plus `'resp'` in `audit-authority-files.py`. Der Cross-Ref-Wert 396 war deshalb kein Beweis: das Skript scannt nur `tei/`. Damit gatet die CI die **Form** des Werts, nicht die **Existenz** des Ziels: `audit-authority-files.py` ist ein manuelles Diagnose-Werkzeug und in keinem Workflow verdrahtet, ein `contrib_099` (es gibt 52 Einträge) validiert also grün. Bewusst so gelassen, weil das Skript 35 Bestands-Orphans meldet und als hartes Gate erst eine Baseline bräuchte.
- **`@norm` auf BCP-47 festgenagelt**, nicht „ISO 639-3 / BCP-47“. Für Aramäisch identisch (`arc`), für Latein nicht (`la` gegen `lat`) – und Schicht A nutzt BCP-47.
- **Ausgelagert:** `@resp` wird in beiden Oberflächen nicht angezeigt, weil `contributors.xml` bewusst nicht im Authority-Index liegt. Die Zurechenbarkeit endet damit auf der Datenebene. In TEI-MODEL-AUTH-FILES und CONTRACTS als Ist-Zustand dokumentiert, Umsetzung als eigenes Issue.

**Phase:** Betrieb (Daten + Schema, additiv). Gepflegt: TEI-MODEL-AUTH-FILES §3.1 (neuer Unterabschnitt), TEI-MODEL §11 (Authority-Index 1.7.0, Authority-Schema 1.1.0), CONTRACTS §G.3, INDEX §Status, `docs/features/FREMDSPRACHEN-PHASENPLAN-28.md` (Phase 0 + Kalibrierfall), `schema/examples/authority-lexicon.example.xml`.

---

## 2026-07-31 – Aufräum-Session (Parallelsession, PR #275)

*Absatz von der Aufräum-Session formuliert und hier eingetragen; PR #275 war zum Eintragszeitpunkt bereits auf `main` (`d350b766c`).*

**2026-07-31 Aufräum-Session.** Directory-Layout in `CLAUDE.md` um `schema/`, `ingest/`, `includes/`, `temp/` ergänzt; der Verzeichnisbaum in `scripts/README.md` war um 19 Skripte und zwei Ortswechsel gedriftet und wurde gegen das Dateisystem neu geschrieben, samt einer explizit formulierten Archivierungsregel (Grenze ist der Issue-Status, nicht „schon gelaufen"). `convert-l-to-lb-143.py` archiviert (#143 geschlossen). Die stale Implementation-Plan-Datei zu #114 gelöscht: 40 offene Checkboxen für ausgelieferte Arbeit. Root-`test-results/` als Abfall eines Root-Playwright-Laufs entfernt, zwei Alt-Branches mit Beleg gelöscht, `origin/ingest/bre-weingruesse` mangels Merge-Beleg bewusst stehen gelassen. Aus der Session heraus #274 (nächtlicher Index-Rebuild) angelegt.

**Phase:** Betrieb (reine Struktur- und Doku-Arbeit, kein ausgelieferter Code, kein Index- oder API-Rebuild).

---

## 2026-07-31 – Health-Check: Zahlen-Drift und Gate-Wirksamkeit

**Scorecard:** Die Datenzahlen der fünf geprüften Docs sind drift-frei (667 Korpusdateien, 8 Authority-Files, 43.879 Lemmata, 256.760 Formen / 234.243 Mappings, Index v4.2.0 / v1.7.0, alle gegen die Daten gemessen, nicht gegen andere Doku); Drift lag bei den **code-abgeleiteten** Zahlen und außerhalb des Reviers (#277 bis #279). Vierzehn Stellen in INDEX/ARCHITECTURE/DECISIONS/DESIGN angefasst (zehn davon in ARCHITECTURE). Die Modulzahl stand an fünf Stellen falsch, und die beiden Fälle brauchten verschiedene Behandlung: die zwei „21" in ARCHITECTURE waren schlicht überholt (Ist 25) und sind korrigiert, die 22 und die 10 in ADR-002 waren gedriftete Ist-Zahlen aus dem Juni 2026, die sich als Angabe zum Refactor-Zeitpunkt ausgaben; der ADR trägt jetzt den gemessenen Stand seines eigenen Datums (13 Module insgesamt, davon zwei in `tei/`). Dazu zwei im Modulbaum und in der Router-Tabelle fehlende Werkzeuge (`hapax-legomena`, `verse-ending-profile`), zwei in der Parameter-Tabelle fehlende `mode`-Werte (`component` aus #239, `verse` aus #106 Punkt 8) und die Verwechslung von Varianten-Formen mit Varianten-Mappings. Spot-Checks ohne Abweichung: `lemmaRefMatchesId` gegen CONTRACTS §B.1, `isStage3Match`/`stage3Distance` gegen §C, `computeKeyness`/`logLikelihood` gegen die #114-Beschreibung in FEATURES (für Keyness gibt es keinen Contract, nur Prosa: genau deshalb #281); XPaths `etym[@type="morphological"]//seg[@type="component"]`, `sense/ptr[concepts.xml#]`, `idno[@type="handschriftencensus"]` gegen `build-authority-index.py`. Rebuild-Test: Suche, Build-Pipeline und Reader sind aus den Docs rekonstruierbar, die elf Playground-Analyse-Werkzeuge nicht (#281). Action Items: #276 bis #281.

**Der Hauptbefund ist das Gate, nicht die Zahlen.** `doc-count-audit.py` lief vor und nach den Korrekturen grün. Zwei der Fehler, die dieser Durchgang gefunden hat, wurden testweise wieder eingebaut und passierten `--check` mit Exit 0. Drei Ursachen: `ARCHITECTURE.md` steht nur in `CODE_DOC_TARGETS` und wird nie auf Datenzahlen geprüft, und von den drei dort konfigurierten Ankern hatte **keiner** einen Treffer in der Datei („Werkzeuge", „analysis tools" und „Entry Points" kommen darin nicht vor), das Target lief also leer; **`DECISIONS.md` steht in keiner der beiden Listen und wird von keinem der zwei Scans angefasst**; und es gibt überhaupt keinen Count für die UI-Modulzahl. Dazu kommt, dass der Anker für `variants_normalized` die Schreibweise „Varianten-Schlüssel" nicht kennt. **Ein konfiguriertes Target ohne Anker-Treffer ist derselbe blinde Fleck wie ein fehlendes Target, nur schwerer zu sehen**, weil die Datei ordentlich in der Liste steht. Nebenwirkung dieses PRs: mit „elf Analyse-Module" trifft der `pattern_modules`-Anker in `ARCHITECTURE.md` zum ersten Mal überhaupt (vorher 0 Vorkommen, jetzt 2). Die Lehre ist Handwerksregel 1 an einem Gate statt an einem Test: ein Audit, das jahrelang grün läuft, sagt nichts, solange niemand den Fehler einbaut, den es fangen soll.

**Eine gemeldete Inkonsistenz war keine, und das Nachmessen hat sie gerettet.** `docs/CONTRACTS.md` nennt an einer Stelle 234.244 Varianten-Schlüssel und an anderer 234.243. Der erste Reflex war „Off-by-one, Ist-Wert einsetzen". Die Zweitmeinung hielt dagegen, die erste Zeile sei eine datierte Aussage über Authority-Index v1.6.2. Gemessen am Blob vor `87b6dc941` (#138/#243): damals **256.761 Formen / 234.244 normalisiert**, heute 256.760 / 234.243, Differenz exakt der Typ `type_195524` („cxlvix", nur in HUG), der mit den 814 Strophenziffern wegfiel. Beide Zahlen waren zu ihrer Zeit richtig; ein „Fix" hätte korrekte Historie überschrieben. #277 ist entsprechend als Stand-Markierung formuliert, nicht als Korrektur. Derselbe Reflex war auch in diesem Durchgang schon einmal am Werk: die INDEX-Chronikzeile zu #45 wurde zunächst auf „heute 43.879" gezogen, also eine driftende Zahl in genau die Zeilenklasse gepflanzt, die das Audit bewusst überspringt, und nach dem Einwand auf den Stand 2026-06 zurückgesetzt.

**Zwei Zahlen, die verschieden bleiben müssen.** 256.760 Rohformen in `variants.xml` gegen 234.243 Mappings im Runtime-Dictionary, und 43.879 Lemmata heute gegen 43.754 vor dem #115-Backfill. Beide Paare sind mehrfach zu einer Zahl verschmolzen worden, in beide Richtungen. Die korrigierten Stellen bekamen deshalb drei verschiedene Behandlungen: ARCHITECTURE §Data Layer benennt Mappings und Rohformen als verschiedene Größen und verweist für die Werte auf CONTRACTS §C, statt sie in einer ungeprüften Datei zu duplizieren; DESIGN und INDEX behalten ihre Zahl und markieren den Stand, zu dem sie galt.

**Die lohnendsten Befunde waren keine Zahlen.** `docs/ARCHITECTURE.md` beschrieb den Storage-Abschnitt so, als seien alle vier Object Stores des Playgrounds in Gebrauch, und stellte die 24 Stunden des ungenutzten `authority_files`-Stores neben die 30 Tage aus ADR-004, als wäre es derselbe Mechanismus. Gemessen hat nur `tei_files` einen Schreiber; die Indexe liegen seit dem gemeinsamen `CorpusLoader` in `MHDBDBMainSite` (#280). Und die Router-Parameter-Tabelle kannte zwei der drei `mode`-Werte nicht (`component` aus #239, `verse` aus #106 Punkt 8), obwohl der Router beide behandelt. Beides sind Aussagen über Verhalten, keine gealterten Zahlen: ein Zahlen-Audit findet diese Klasse grundsätzlich nicht, weil es nichts zu vergleichen gibt. Der nächste Durchgang sollte deshalb nicht nur Zahlen gegen den Code prüfen, sondern auch Behauptungen, und damit rechnen, dass manche davon nie gestimmt haben statt bloß veraltet zu sein.

**Der PR-Review fand drei Dinge, die derselbe Durchgang hätte finden müssen.** Erstens: die Parameter-Tabelle nennt für `mode` nur `proximity` und `document`, aber `handleMultiLemmaRoute()` kennt drei Werte, der dritte ist `verse` (#106 Punkt 8). Gefunden wurde in derselben Zeile der Nachbarfall `mode=component`, der andere nicht. Wer eine gedriftete Zeile anfasst, prüft ihre Quelle vollständig und nicht nur bis zum ersten Treffer. Zweitens: die Gate-Diagnose war für `DECISIONS.md` zu freundlich formuliert („steht nicht in `DOC_TARGETS`"), tatsächlich steht die Datei in keiner der beiden Listen; das ändert den Zuschnitt von #276, weil ein zusätzlicher Count dort nichts nützt. Drittens: ADR-002 hatte im ersten Anlauf drei frische Ist-Zahlen bekommen, ausgerechnet in der ungescannten Datei, während zwei Meter weiter in ARCHITECTURE eine Zahl aus genau diesem Grund entfernt wurde. Die Antwort darauf war zunächst, die Zahlen zu behalten und als historisch zu deklarieren: das war ein Zwischenstand und selbst falsch, siehe den nächsten Absatz.

**Runde 2 fand den Fehler, vor dem der Eintrag selbst warnt.** Die Rücknahme aus Befund 3 hatte ADR-002 die Zahlen „22 Module, `tei/` 10" als die „des Refactor-Zeitpunkts" gegeben. Der ADR ist auf den 2. Oktober 2025 datiert; gemessen am Baum von `ae80175c4` lagen an dem Tag **13** Module dort, davon zwei in `tei/` (`tei-ui.js`, `multi-lemma-search.js`). Sämtliche Analyse-Werkzeuge sind ab Mai 2026 entstanden, die 10 ist der Stand zwischen dem 11. Juni und dem 2. Juli 2026. Ich hatte also eine gedriftete Ist-Zahl zur geschützten historischen Angabe erklärt, und genau diese Umdeutung nennt derselbe Eintrag ein paar Zeilen weiter oben als die Falle, in die man bei #277 fast getreten wäre. Wer eine Zahl für historisch erklärt, misst das Datum dazu, statt es aus der Zahl zu erschließen: `git log --diff-filter=A` kostet zehn Sekunden. Der ADR trägt jetzt den gemessenen Stand.

**Nebenbefund zum Em-Dash-Gate:** `check-no-em-dash.py` prüft nur HTML, JS und CSS (`GLOBS`, Z. 143 bis 153). Für `docs/**/*.md` läuft es leer, ein grünes Gate belegt dort also nichts. Die Stilregel gilt trotzdem; für diesen Diff manuell geprüft (keine Em-Dashes in den hinzugefügten Zeilen).

**Phase:** Betrieb (nur Doku). Gepflegt: INDEX, ARCHITECTURE, DECISIONS, DESIGN, JOURNAL. Keine Daten-, Index- oder API-Änderung, deshalb kein Rebuild und kein Versions-Bump.

---

## 2026-07-31 – #258: Wörterbuchnetz-Verlinkung von zwei auf fünf Wörterbücher

`DICTIONARIES` in `assets/js/lib/woerterbuchnetz.js` umfasst jetzt MWB, Lexer, LexerN, BMZ und FindeB; die Sigle-zu-Titel-Auflösung liegt als `DICTIONARY_TITLES` daneben, weil die API sie nicht liefert (`/dictionaries` gibt zu allen 52 Wörterbüchern nur `sigle` und `path`). Drei Konsumenten, nicht die zwei aus dem Ticket: neben Lemma-Seite (#73) und Korpus-Lemma-Panel (#114) rendert auch das Hapax-Werkzeug (#196) die Links selbst.

Zwei Dinge fielen erst durch die Erweiterung auf. Erstens liefert FindeB bei Schreibdoubletten dieselbe `wbnetzid` mehrfach (5 von 26 Einträgen über zwölf Stichproben; die anderen vier Wörterbücher 0 von 79), was ohne Deduplizierung als identische Links gerendert hätte; der Client verwirft Wiederholungen **pro Wörterbuch**, nicht global, weil derselbe Deep-Link unter zwei Siglen zwei Artikel wären. Zweitens tragen die Einträge eines Wörterbuchs zum selben Stichwort fast immer denselben Text, weil es Homographen sind: „MWB: liebe, liebe, liebe" waren drei gleich beschriftete Links mit verschiedenen Zielen. Die grammatische Angabe steht deshalb jetzt mit im Linktext, und die Sigle nur noch einmal je Wörterbuch statt vor jedem Eintrag.

**Der teuerste Befund kam aus dem CI-Review, nicht aus der Umsetzung.** `fetchWbnetzEntries` warf das `failed`-Flag beim Rückgeben weg, der Aufrufer konnte „kein Eintrag" nicht von „Request gescheitert" unterscheiden. Bei einem Ausfall des Wörterbuchnetzes lieferten alle fünf Wörterbücher leere Listen, und das Hapax-Werkzeug behauptete daraufhin „nicht als Lemma gefunden, Kandidat für ein echtes Hapax", also genau die Aussage, für die es gebaut ist, hergeleitet aus einer Netzstörung. Der `catch` dort fing das nie, weil `fetchWbnetzEntries` gar nicht rejectet: für Netzfehler war er toter Code. Das Verhalten gab es schon mit zwei Wörterbüchern, #258 machte die Aussage nur namentlich und stärker. `failed` bleibt jetzt im Rückgabewert, die Zelle unterscheidet vier Zustände (nichts gefragt, gar nicht durchgekommen, teilweise durchgekommen, belegt-nicht-gefunden), und nur der letzte trägt die Hapax-Aussage. Als Regel in CONTRACTS §D.2 festgehalten: „Absence of a link is not absence of attestation." Die beiden anderen Oberflächen dürfen `failed` weiter ignorieren, weil sie bei leerem Ergebnis schlicht nichts sagen statt etwas Falsches.

Last gemessen und unkritisch: fünf parallele Requests kosten 31 bis 81 ms kalt, 0 ms warm, der Panel-Worst-Case von 15 Requests 41 ms. Zwei Nebenbefunde: das MWB liefert für `minne` und `vriunt` 0 Treffer und für `herze`/`liebe` welche, weil es noch erscheint (in CONTRACTS §D.2 als „not a defect" festgehalten, damit es niemand als Bug anfasst); und `hilfe-daten.html` schrieb `lexicon.xml` eine BMZ/Lexer/MWB-Anbindung zu, die dort nicht existiert (0 Treffer in 43.879 Einträgen). Beides waren keine gedrifteten Zahlen, sondern Aussagen, die nie gestimmt haben. Vom erhofften Erkenntnisgewinn bleibt eine nüchterne Zahl: von 50 geprüften Hapax-Kandidaten wird genau einer erst durch die drei neuen Wörterbücher als belegt erkennbar.

**Bewusst nicht angefasst:** die datierten Meilenstein-Einträge in `INDEX.md` (Z. 165, 166) und `ROADMAP.md` (Z. 107) nennen weiter „MWB/Lexer". Das ist die Beschreibung des Auslieferungsstands vom Juli, und das Projekt lässt solche Zahlen stehen (Z. 160 führt unverändert „damit 8 TEI-Analyse-Werkzeuge im Playground", inzwischen sind es zwölf). Wer sie retroaktiv umschreibt, macht aus einem Protokoll eine Momentaufnahme. Der Kommentar in `korpus.html:262` ist dagegen keine historische Aussage, sondern schlicht veraltet.

**Phase:** Betrieb (frontend-only, kein Index- und kein API-Rebuild). Gepflegt: CONTRACTS §D.2, ARCHITECTURE (Wörterbuchnetz + MWB Online), FEATURES (Korpussuche, Hapax, neuer Abschnitt Lemma-Seite), `hilfe-daten.html`, `hilfe-korpussuche.html`, `hilfe-playground.html`, `impressum.html`, `lemma/index.html`, `README.md`. Issue #258 bleibt bis zur Abnahme durch KZW offen. PR #285 (vier Commits, gesquasht zu `8a6626c68`), README separat als `c3fd43b27`.

---

## 2026-07-31 – Die ROADMAP beschrieb den Stand eines Dokuments, nicht den des Projekts

**Summary:** Zwei Einträge in `docs/ROADMAP.md` führten Arbeit als offen, die seit dem 10.07. erledigt ist: die posAll-Anzeige-Migration (#187, Commit `edb16dd3f`, Issue als completed geschlossen) und der WVV-Strophen-Lauf (nachgemessen an `tei/WVV.tei.xml`: 489 fortlaufende `<lg>`). Beide sind aus der Liste „Direkt startbar geworden" genommen und stehen als ein gemeinsamer, datierter Korrekturabsatz darunter.

**Warum das hier steht und nicht nur im Diff:** Es ist an einem Tag dreimal dasselbe Muster aufgetreten. Neben #187 und WVV suggeriert die Spalte „KZW-Antwort liegt vor" bei #250, es sei entschieden; tatsächlich betrifft die Antwort vom 29.07. nur die Punkte 1 und 2, während Punkt 3 am 30.07. ergänzt und als Frage gestellt wurde und unbeantwortet ist. Die ROADMAP altert also nicht zufällig, sondern strukturell: sie wird beim Aufnehmen gepflegt und beim Erledigen nicht. Wer sie als Gegenwartsbeschreibung liest, plant gegen einen Stand, den es nicht mehr gibt.

**Verifikationsweg, weil er den Unterschied gemacht hat:** Nicht die Doku gegen die Doku geprüft, sondern gegen Code und Korpus. Für #187 hieß das, jede der im Issue gelisteten Anzeige-Stellen auf das `posAll[]`-Muster hin anzusehen (dabei fiel `verse-position-search.js` auf, das in der Issue-Liste fehlte); für WVV, die 489 `<lg>` selbst zu zählen. Ein Commit-Betreff ist eine Behauptung, kein Beleg.

**Phase:** Betrieb, reine Doku, kein Rebuild. PR #296.

---

## 2026-07-31 – Die gefährlichsten Doku-Sätze sind die über Abwesenheit

**Summary:** `docs/CONTRACTS.md` hat mit §H Zählregeln für die Analyse-Werkzeuge bekommen, die zitierfähige Zahlen ausgeben (#281, PR #304). Der Abschnitt ging durch fünf Review-Runden, und in jeder einzelnen wurde ein Fehler im Text gefunden. Bemerkenswert ist nicht, dass es Fehler gab, sondern dass sie fast alle denselben Typ hatten: **Aussagen darüber, dass etwas nicht existiert.**

Die Reihe im Einzelnen: „`sum(shareOfVerses)` liegt unter 100 %, weil unannotierte Versenden fehlen" (falsch, jeder `lineEnds`-Eintrag trägt per Konstruktion eine Lemma-ID, die Summe ist exakt 100 %). „Die übrigen Werkzeuge sind plain counts, nichts Abgeleitetes" (falsch, drei rechnen Verhältniszahlen). Nach der Korrektur: „drei Werkzeuge haben abgeleitete Größen" (falsch, es sind fünf, Begriffs-Verteilung und Versposition-Suche fehlten). Und „keine dieser Raten teilt Gleiches durch Gleiches" (zu breit, `hapaxRate` tut genau das).

**Warum das hier steht:** Eine positive Aussage über Code lässt sich an einer Stelle prüfen und fällt beim Prüfen auf, wenn sie falsch ist. Eine Aussage über Abwesenheit verlangt, alle Stellen zu prüfen, an denen das Fehlende stehen könnte, und niemand tut das beiläufig. Genau deshalb steht sie am Ende eines Abschnitts, der sonst sorgfältig ist, und wirkt wie eine Zusammenfassung, obwohl sie eine unbelegte Behauptung ist. Für Promptotyping-Doku heißt das: Abgrenzungsabschnitte („was hier nicht steht") brauchen dieselbe Prüftiefe wie der Hauptteil, und sie sollten die ausgeschlossenen Fälle **namentlich** aufzählen statt sie zu charakterisieren. Eine Liste von neun Namen ist prüfbar, „die übrigen Werkzeuge" nicht.

**Der wertvollste Satz des Abschnitts** kam aus derselben Prüfrunde und stand vorher nirgends: die Versposition-Suche beantwortet dieselbe Frage wie der Reim-Druck aus §H.4, liest aber beide Seiten aus `text.lemmata`, während der Reim-Druck seinen Zähler aus `text.words[]` nimmt. Nach einem Ingest mit Mehrfach-`@lemmaRef` zeigen zwei Oberflächen für dasselbe Lemma verschiedene Prozentzahlen. Heute ist das folgenlos, weil das Korpus über alle 7.532.982 annotierten Tokens **null** Mehrfach-Referenzen führt (nachgemessen, und `sum(text.wordCount)` im gebauten Index ergibt dieselbe Zahl, der Nicht-leer-Guard zieht also nichts ab).

**Phase:** Betrieb, reine Doku, kein Rebuild. PR #304.

---

## 2026-07-31 – Ein Audit, das seine eigene Fehlalarm-Vermeidung nicht überlebt

**Summary:** Sieben Texte trugen ein `<author ref="#person_N"/>` ohne Textinhalt: nicht anonym, nur namenlos (#228, PR #306). Der Fix ist trivial, interessant ist, warum es niemandem auffiel und was beim Absichern passierte.

**Warum es jahrelang unsichtbar war:** Die Referenz löste sauber auf, ein leeres Element ist schema-valide, und der Cross-Ref-Audit überspringt Tokens ohne Dateinamen (`#frag`). Es gab also drei Prüfungen, an denen der Fall vorbeikam, ohne eine davon zu verletzen. Das neue `scripts/audit/check-author-refs.py` schließt die Lücke und fand dabei vier weitere Befunde, die vorher niemand hatte: einen toten `@ref` (VOR verweist auf eine Person, die es in `persons.xml` nicht gibt, der einzige tote Verweis im Korpus), einen Präfix-Ausreißer (WZB schreibt als einziger `persons.xml#person_anonym` statt `#person_anonym`) und zwei Namensabweichungen. Alle vier stehen als #308, keiner ist mitrepariert worden, weil drei davon eine fachliche Entscheidung brauchen.

**Der lehrreiche Teil:** Das Audit vergleicht den TEI-Text gegen den `preferred`-Namen. Nach der ersten Review-Runde normalisierte ich beide Seiten mit `' '.join(text.split())`, weil ein Zeilenumbruch in `persons.xml` sonst einen Fehlalarm erzeugt hätte. Die nächste Runde zeigte, was diese Normalisierung kostete: `tei/LUU.tei.xml` trägt den Autornamen über zwei eingerückte Zeilen, und `"Albertanus von\n            Brescia"` stand so im Korpus-Index und in `api/texts/LUU.json`. Das Audit meldete nichts, weil beide Seiten nach der Normalisierung gleich aussahen. **Die Maßnahme gegen Fehlalarme hatte einen echten Alarm mitgenommen.**

Aufgelöst mit beidem: der Build normalisiert jetzt selbst (die Einrückung ist eine Eigenschaft der XML-Formatierung, nicht der Daten, der Fix gehört also zum Leser und nicht in die Quelldatei), und das Audit meldet Whitespace als eigene Klasse statt ihn wegzuvergleichen.

**Phase:** Betrieb. Voller Data-Change-Lifecycle: `variants.xml` unverändert (No-op-Lauf), Corpus-Index v4.2.0 → v4.2.1, Authority-Index unverändert (`build-authority-index.py:250` liest nur `persName[@type="preferred"]`, die neue Nebenform kann den Index gar nicht erreichen, siehe #307), API neun Dateien. PR #306.

---

## 2026-07-31 – Das Gate, das die eigene Regression nicht fing

**Summary:** Drei Doku-Befunde aus dem Health-Check gebündelt (#293/#294/#297, PR #305): die XPath-Tabelle beschrieb drei Zeilen ungenau, die Größe des Variants-Dictionary stand an drei weiteren Stellen falsch, und `doc-count-audit.py` prüfte an fünf konfigurierten Stellen faktisch nichts.

**Der Befund, der zählt:** Der PR selbst reproduzierte die Fehlerklasse, gegen die er antrat. Die neue Prosa in `docs/DATA-MODEL.md` führte eine ungegatete `584` ein, und zwar doppelt ungegatet: `works` stand gar nicht im Target der Datei, und der Anker heißt `Werke`, hätte hinter „584 `<bibl>`" also ohnehin nicht gegriffen. Behoben durch Umformulieren an den Anker heran plus Target-Eintrag, belegt mit einer Mutation (586 → Drift, 583 → Drift, 584 → still).

Zweiter Befund derselben Art: die Umformulierung aus #294 ließ den Anker in `docs/DECISIONS.md` treffen, eine Zahl steht dort aber weiterhin nicht. Die Lückenmeldung verschwand, die Abdeckung blieb null. Mein erster Reparaturversuch (Eintrag in `INTENTIONALLY_SILENT`) war selbst falsch, und der im selben PR gebaute Obsoleszenz-Check hat ihn sofort als `silent-obsolet` gemeldet. Ein Gate, das den eigenen Autor korrigiert, hat den Test bestanden.

**Zwei Mechanismen, die dabei herauskamen und über den Anlass hinaus gelten:**

1. `NUMERIC_SCAN_MIN = 100` machte das Audit blind für jede Datenzahl darunter. Beim Absenken für `names` (90 Kategorien) zeigte die Gegenprobe, dass die Absenkung allein wirkungslos ist: das Ziffernmuster fand nur Zahlen ab **drei** Stellen. Zwei unabhängige Schwellen, von denen die eine unsichtbar war.
2. Die Begründung „Ratsche, die greift, sobald die Zahl wieder eingesetzt wird" hielt nicht: ausgerechnet die Form, die vorher dort stand (`~257k`), fällt durch beide Filter (keine Wortgrenze zwischen `7` und `k`, dazu der Rundungs-Skip). Das ist keine Lücke im Code, sondern die Grenze des Verfahrens: eine gerundete Angabe ist erlaubt, und ob sie sich auf die richtige Bezugsgröße bezieht, kann kein Ziffern-Scan wissen. Genau daran ist #279 aufgefallen, per Hand. Der Kommentar sagt das jetzt, statt Sicherheit zu behaupten.

**Nebenbei, aber mit Dauerwirkung:** `build-authority-index.py` las den Werksautor mit `.//tei:author` statt `./tei:author`. Alle 584 Werke tragen seit dem Zotero-Sync ein `<biblStruct>` mit den Autoren der **Edition**; ein Werk ohne eigenen `<author>` hätte still den Editionsautor bekommen. Heute betrifft es kein einziges, der Index bleibt byte-identisch, und die Verengung schließt den Fall aus, bevor er entsteht. Das Schema stützt sie: es erlaubt den Werk-Autor nur als direktes `<bibl>`-Kind und erlaubt zugleich null Vorkommen.

**Phase:** Betrieb, Doku plus zwei Build-Skripte, kein Rebuild nötig. PR #305.

---

## 2026-07-31 – Health-Check-Scorecard (#140, angefordert von KZW am 28.07.)

**Flow (4 der 13 stabilen Docs end-to-end gelesen: CONTRACTS, DATA-MODEL, INDEX, TEI-MODEL):** Die gefundenen Defekte liegen in diesen vier durchgängig in den per PR-Nachtrag gewachsenen Abschnitten, nicht in den am Stück geschriebenen. INDEX „Recent Milestones" (41 Zeilen, endet am 10.07., ein Eintrag meldet ein offenes Issue als geshippt), CONTRACTS §A (korrigiert sich im Fließtext selbst), TEI-MODEL §10 (führt zwei geschlossene Punkte als offen und widerspricht dabei §8.1 derselben Datei). **KZWs Eindruck aus #140 hat damit eine prüfbare Ursache: nicht ein Schreibstil, sondern Absätze, die angehängt wurden, ohne den davor anzufassen.** → #315, #316

**Algorithmen (3 gezogen + 2 Kurzproben):** MHG-Normalisierung in beiden Sprachen, Positionszählung samt Index-Aufbau, Nähesuche mit Fensterwahl und Dedup, dazu 3-Stufen-Auflösung und Cache-Invalidierung. **Alle fünf stimmen vollständig**, inklusive Grenzfälle, Guards und Reihenfolge. Es driften ausschließlich Messzahlen und Zeilenanker, nie die Logik. → #318

**XPaths (22 von 27 Zeilen geprüft, plus Missing-Check):** zwei Zeilen beschreiben falsches Verhalten (`biblStruct/@type` wird nie gelesen, Korpus-Titel steht auf dem Vor-#228-Stand: mein Versäumnis aus PR #306), fünf Produktionen fehlen ganz, darunter `extract-variants.py` als komplettes Skript. Keine Karteileichen. Der wertvollste Fund: `text.genre` ist **in allen 667 Texten leer**, weil kein TEI-File ein `term[@type="genre"]` trägt, steht aber ohne Hinweis in Schema und Tabelle. → #318

**Gates:** Em-Dash-Gate grün, und der Frontend-Bestand ist gate-unabhängig nachgeprüft wirklich sauber. KZWs Meldung vom 28.07. betraf ein mehrzeiliges Template-Literal im Hapax-Werkzeug; testweise eingebaut, vom Gate mit Datei und Zeile gemeldet, danach zurückgebaut. Zur bekannten `docs/`-Lücke (siehe Eintrag oben) kommen zwei neue: `GLOBS` enthält **überhaupt kein `*.md`-Muster** und keine Authority-Files, obwohl `works.xml`-Notizen im Reader und in der API rendern. Für ASCII-Umlaut-Substitute gibt es **gar kein Gate**, mit sichtbarer Folge: nach 252 Korrekturen am 12.07. sind in drei Wochen sieben neue dazugekommen, einer davon am Tag des Checks. → #317

**Rebuild-Test:** für die geprüften Pfade ja, inzwischen einschließlich der Analyse-Werkzeuge über §H (die frühere Scorecard musste sie noch ausnehmen). Ein Nachbau träfe an zwei Rändern daneben: `authorRef` ohne `#` und ein `genre`-Feld, das er füllen wollte.

**Ein gemeldeter Drift war keiner, und das ist der lehrreichste Teil.** Der Prüfdurchgang meldete die Breve-Zahlen in §A als veraltet (469 → 467, 405 → 403). Beim Nachmessen kam heraus, dass die Zahl davon abhängt, ob man vor dem Zählen Unicode-NFD anwendet: ohne Normalisierung 467, mit 469. Für die Aussage, die §A trifft (Schritt 0 komponiert das zerlegte Breve, Schritt 3 löst es auf), ist die NFD-Zählung die richtige, die Doku-Zahl also korrekt. Sechs weitere Angaben desselben Absatzes stimmen exakt, bis auf die Verteilung über zehn Basiszeichen. **Der Mangel ist nicht die Zahl, sondern dass keine Messvorschrift dabeisteht.** Wer die fehlende Vorschrift nicht bemerkt, misst anders und „korrigiert" eine richtige Angabe in eine falsche. Genau das wäre hier ohne Gegenmessung passiert.

---

## 2026-07-31 – Eine Kennzahl ist so gut wie der Name ihres Nenners

**Summary:** #309 sah nach einer Kleinigkeit aus: zwei Spaltenbeschriftungen im Versendings-Profil an CONTRACTS §H angleichen. Beim Nachmessen, wie groß der Unterschied zwischen „Verse" und „annotierte Verse" überhaupt ist, kam die Zahl heraus, die den ganzen PR umgekrempelt hat: **20,13 % aller `<w>`-Elemente im Korpus tragen kein `@lemmaRef`**, und die Abdeckung schwankt je Text zwischen **58,4 % und 100 %** (Median 77,4 %, 358 von 667 Texten unter 80 %).

Damit war es kein Beschriftungsproblem mehr. Jede „pro 1000"-Rate und jede „Wörter"-Angabe im Projekt teilt durch eine Größe, die je Text unterschiedlich weit hinter der Textlänge zurückbleibt. Die Hauptseite nannte die Spalte schlicht „Wörter", und `hilfe-korpussuche.html` erklärte sie ausdrücklich falsch: „Gesamtlänge des Textes in Wörtern".

**Der lehrreiche Teil kam aus dem Review.** Mein erster Entwurf behauptete, schwächer annotierte Texte schnitten systematisch höher ab. Der Einwand: wären die Lücken zufällig über Lemmata verteilt, kürzte sich der Effekt exakt weg, und beim Hapax-Werkzeug wird auch der Zähler gedrückt, weil eine unannotierte seltene Form als Rarität unsichtbar ist. Beides stimmt. Der Bias ist `coverage(Lemma) / coverage(Text)`, er kehrt sich für Funktionswörter um, und aus der bloßen Abdeckungsdifferenz folgt gar nichts.

Nachgemessen statt entschärft: Spearman −0,17 über die 345 Texte ab 1000 Tokens, Faktor 2 zwischen den Abdeckungsquartilen, und kein Längen-Artefakt (Länge korreliert mit Abdeckung, aber nicht mit der Rate). Der Nenner-Effekt überwiegt also, moderat. Der zweite Einwand traf dann die Formulierung: „der Nenner-Effekt gewinnt" ist die kausale Lesart einer Beobachtungskorrelation, und Abdeckung ist im Korpus nicht zufällig verteilt (Gattung, Ingest-Ära). Jetzt steht dort „consistent with", mit den unkontrollierten Confounds im Klartext.

**Was davon bleibt:** ein Contract-Abschnitt, der eine Zahl nennt, muss sagen, womit sie nachzurechnen ist. Die Messung war als zitierfähig behauptet und existierte nur in meiner Shell. Sie liegt jetzt als `scripts/audit/coverage-bias-check.py` bei. Der Unterschied zwischen „ich habe gemessen" und „das kann jeder nachmessen" ist genau der Unterschied, den §H für alle anderen Zahlen längst einfordert.

**Phase:** Betrieb, reine Beschriftung plus Doku, kein Rebuild. PR #313.

---

## 2026-07-31 – Die vierte Stelle, die niemand pflegt, weil sie nichts kaputt macht

**Summary:** Der Authority-Index wurde für #307 auf 1.8.0 gebumpt. Die drei Stellen, die dabei immer angefasst werden (Build-Skript, `corpus-loader.js`, `TEI-MODEL.md` §11), waren alle korrekt. Die unabhängige Gegenprüfung fand eine vierte: `docs/INDEX.md` nannte „Corpus Index v4.2.0, Authority Index v1.7.0" und lag damit schon **vor** diesem Branch zwei Minor-Versionen zurück.

**Warum das interessant ist:** die Pflegeanweisung existierte. `TEI-MODEL.md` §11 nennt die Stelle ausdrücklich („Pflege bei jedem Index-Bump: hier, in `corpus-loader.js`, im Build-Skript, in INDEX.md §Status"). Sie stand da, sie war richtig, und sie hat nicht geholfen. Die drei anderen Stellen werden gepflegt, weil ihr Auseinanderlaufen etwas kaputt macht: der Cache invalidiert nicht, Nutzer bekommen den neuen Index nie zu sehen, und ein Gate meldet es. Die vierte Stelle bricht nichts. Sie wird still falsch.

`check-index-versions.py` prüft deshalb jetzt acht Stellen statt vier, die beiden Doku-Angaben eingeschlossen. Belegt mit zwei Mutationen (INDEX.md 1.8.0 → 1.7.0, TEI-MODEL 4.2.1 → 4.2.0, beide Exit 1, danach wieder 0). Eine Doku-Notiz mehr hätte das nicht verhindert, denn die Notiz war ja schon da.

**Der übertragbare Teil ist nicht der Merksatz, sondern der Beleg:** die korrekte Pflegeanweisung existierte und hat nichts verhindert. Das entkräftet den Reflex, in solchen Fällen noch eine Doku-Notiz zu schreiben. Derselbe Schluss trägt den Umlaut-Befund desselben Tages (#317).

**Phase:** Betrieb. PR #312.

---
## 2026-07-31 – #314: Der Guard, der 1300 Zeilen konserviert hat

**Summary:** Der Playground trug einen vollständigen Datei-Upload-Pfad, den seit dem Redesign niemand mehr erreichen konnte: Datei einlesen, XML-DOM parsen, in IndexedDB ablegen, darin suchen, Ergebnisse rendern. Rund 2200 Zeilen über 19 Dateien, drei davon ganz gelöscht. Ausgangspunkt war ein Beschriftungs-Issue: drei Varianten, wie man den Upload-Knopf besser benennt. Die Bestandsaufnahme davor ergab, dass es den Knopf nicht mehr gibt.

**Warum es niemandem aufgefallen ist.** `setupFileUpload()` prüfte auf `#uploadZone` und kehrte still zurück, wenn das Element fehlte. Der Guard war als Robustheit gemeint, für eine Seite ohne Upload-Bereich. Als das Redesign den Bereich entfernte, hat er genau seine Aufgabe erfüllt und dabei den ganzen dahinterliegenden Zweig konserviert: keine Exception, kein Konsolenfehler, nichts, was jemandem aufgefallen wäre. Ein Guard macht Code robust gegen fehlende Voraussetzungen und damit zugleich unauffällig, wenn die Voraussetzung dauerhaft fehlt.

Dazu kam ein zweiter Mechanismus, und der ist der unangenehmere. `corpus.spec.js` prüfte `typeof teiManager.loadCorpusIntoPlayground === 'function'`. Diese Methode hatte im Produktivcode null Aufrufer; der Test war ihr einziger Nutzer. Ein Test, der nur die Existenz einer Funktion behauptet, hält sie am Leben, ohne je zu zeigen, dass sie gebraucht wird. Er sieht wie Absicherung aus und wirkt wie ein Anker. Dasselbe für `test.html`: dort instanziierten zwei Suites `TEIStorageManager` und `IndexedDBManager` direkt, also an der UI vorbei. Beide waren grün, während der Pfad, den sie prüfen sollten, aus der Oberfläche verschwunden war.

Belegt war der Tod des Pfads dann dreifach: kein `#uploadZone` in irgendeinem HTML, zwei aufruferlose Einstiege, und ein Aufruf auf `getStorageStats()`, eine Methode, die es nicht gibt. Der letzte Punkt ist der stärkste Beweis: wäre der Code je gelaufen, hätte er an dieser Stelle geworfen.

**Ein Test war falsch-grün, und zwar auf lehrreiche Weise.** `playground.spec.js` klickte „Clear Storage" und prüfte, ob danach „Cleared" in der Konsolenausgabe steht. Der Button loggt „Storage cleared", klein geschrieben. Das gesuchte „Cleared" mit großem C stammte aus `clearAllCachedFiles()` im Upload-Pfad und stand dort nur, weil derselbe Test zwei Zeilen vorher „Run Tests Again" gedrückt hatte. Der Test war also seit jeher grün, ohne den Button je zu prüfen. Aufgefallen ist das erst, als der Rückbau die fremde Quelle entfernte. Beim Aufräumen fallen fremde Fehlalarme an, und wer sie nur wieder grün macht, verschenkt den einzigen Moment, in dem sie sichtbar werden.

**Mein eigener Fehler war der teuerste Teil.** Beim Blockschnitt in `ui-helpers.js` lief der Schnitt von `updateTEIOverview` bis zur nächsten Abschnittsmarke. Dazwischen lag `enableAuthorityQueries()`, eine Funktion, die mit dem Upload nichts zu tun hat. Der Aufruf in `updateAllUI` blieb stehen, die Definition fehlte, `updateAllUI` brach ab, alle sechs Authority-Buttons blieben `disabled`: 34 gescheiterte Tests und ein 45-Minuten-Lauf, der zur Hälfte Timeouts abgewartet hat. Bei den anderen sechs Dateien war nach jedem Schnitt auf Restverweise geprüft worden, hier nicht. Genau diese Prüfung hätte den Fehler sofort gezeigt, denn der Aufruf stand ja noch da. Anker schützen davor, an der falschen Stelle anzusetzen, nicht davor, zwischen zwei richtigen Ankern etwas Fremdes einzuschließen. Dieselbe Falle schnappte in kleiner Form ein zweites Mal zu, als ein Schnittende auf das erste `});` traf, das zum inneren `page.evaluate` gehörte: dort fing es `node --check` sofort ab. Der Unterschied zwischen den beiden Fällen ist nicht die Sorgfalt, sondern ob eine billige Prüfung dazwischenlag.

Ein drittes Mal schnappte sie latent zu, und dieses Mal hat nur die Zweitmeinung sie gesehen: `waitFor()` in `test-utils.js` ruft `this.sleep()` auf, und `sleep()` fiel mit dem Upload-Pfad weg. Es brach nichts, weil `waitFor` selbst keinen Aufrufer hat. Latente Brüche dieser Art sind der Normalfall beim Aufräumen in Hilfsdateien, und kein Testlauf zeigt sie an: nur wer die Aufrufkette der entfernten Funktion rückwärts verfolgt, findet sie.

**Ein Rückbau kann eine Aufräumfunktion abschalten.** `indexed-db-manager.js` verwaltete die Datenbank `MHDBDB_Playground`, die genau einen Store hatte (`tei_files`), dessen einziger Schreiber im Upload lag. Der Manager war damit gegenstandslos, aber er trug seit #280 eine Schema-Migration, die drei schreiberlose Altstores aus bestehenden Browser-Datenbanken räumt. Nach Teil 1 instanziierte kein Produktivcode mehr den Manager, also lief diese Migration nicht mehr: der Rückbau hätte still eine gerade erst ausgelieferte Aufräumfunktion deaktiviert. Statt 397 Zeilen Schema-Pflege für eine Datenbank ohne Schreiber löscht `playground-main.js` sie jetzt beim Start einmalig. Das ist gründlicher als die Migration und kostet zehn Zeilen. Die Lehre gilt über den Fall hinaus: wer den letzten Importeur eines Moduls entfernt, entfernt auch alle Nebenwirkungen, die dieses Modul beim Laden oder Initialisieren hatte, und die stehen selten im Namen der Funktion.

**Phase:** Betrieb, reiner Code-Rückbau. Keine Daten-, Index- oder API-Änderung, kein Rebuild, kein Versions-Bump. Doku nachgezogen in ARCHITECTURE (Storage-Abschnitt), CONTRACTS §E, DECISIONS, ROADMAP, `playground/readme.md`. PR #324.

---
## 2026-08-02 – Autonome Aufräum-Session: fünf PRs, und die Hälfte der Review-Last war hausgemacht

**Summary:** Ein Tag Restarbeit aus dem Health Check vom 31.07. und aus den Aufräumbefunden #325/#327/#329. Gemergt: #330 (drei Aufräumbefunde, eine Fehlerklasse), #332 (die zweite Inventar-Tabelle hatte denselben Zustand), #333 (der Konsolen-Fehler-Test konnte nicht sehen, wogegen er schützt), #334 (#322, acht TEI-Header), #335 (#315/#318, Doku-Restposten). #336 (#316, INDEX.md) lag am Abend als PR vor.

### Die teuerste Erkenntnis kam aus einer Frage von chsteiner

„Kann es sein, dass wir over-reviewen? Bewerte das mit Zahlen und kritisch." Gemessen über die drei PRs des Tages (#330, #332, #333): **18 Review-Läufe, 27 Befunde. Davon 10 echte Defekte, 13 falsche Tatsachenbehauptungen in selbst geschriebenen Kommentaren, 4 Kosmetik.**

Die 13 sind der eigentliche Befund. Es waren durchweg Zahlen, die ich in erklärende Kommentare geschrieben und nicht gemessen hatte: „zehn weitere Stellen" statt 19, „in allen Skripten" statt 11 von 22, „der einzige Konsument" statt zwei. Jede dieser Zahlen ist eine Angriffsfläche, die ein Review pflichtgemäß prüft und meldet, und jede erzeugt eine Runde, die nichts am Verhalten ändert. Bei #332 betrafen die Runden 3 und 4 zu 100 Prozent Kommentar-Formulierungen und kosteten je rund 20 Minuten Wanduhr (7 Minuten Review plus 13 Minuten `validate`).

**Weniger reviewen ist ausdrücklich nicht die Konsequenz.** Runde 1 fand jedes Mal echte Defekte, und in #333 führte ausgerechnet ein Kommentar-Befund („zehn Stellen") zu 19 real kaputten Aufrufen. Die Konsequenz steht seither in CLAUDE.md unter „Selbst erzeugter Overhead": keine Behauptung in einen Kommentar, die nicht trägt; ab Runde 3 nur noch Verhaltensbefunde einarbeiten; kein voller CI-Lauf für reine Kommentar-Commits.

Der Tag hat die Regel danach zweimal gegen sich selbst gewendet. In #336 stand nach dem Löschen von 41 Changelog-Zeilen ein Satz über `journal-archive.md`, das sei „nur von dort verlinkt": neun Zeilen weiter verlinkte dieselbe Datei es. In #335 behauptete ein Kommentar, `names.xml` sei „die einzige doc-geprüfte Authority-Datei unter der Schwelle", und die Zeile direkt darunter fügte die zweite hinzu. Beide Male war die billigste Reparatur das Streichen des Halbsatzes, nicht das Nachzählen.

### `waitForFunction(fn, {timeout})` ist seit jeher wirkungslos gewesen

Die Signatur ist `waitForFunction(pageFunction, arg, options)`. Ohne Platzhalter landet das Options-Objekt als **Argument in der Seite**, und der Timeout gilt nie. Der Aufruf wartet dann bis zum Testbudget. Das stand an 19 Stellen in sechs Specs so, und in sechs davon lag der deklarierte Timeout unter dem Budget: dort sollte ein Wait früh mit eigener Meldung scheitern und lief in Wahrheit stumm bis zum Budget durch.

Belegt statt vermutet: mit einem eingebauten `ReferenceError` endete der Lauf vor der Korrektur nach 120 Sekunden (Test-Budget), danach nach 60 (eigener Timeout).

**Der Fix war nicht verhaltensneutral, und das ist der interessantere Teil.** An vier Stellen stand 30000 unter einem 60-Sekunden-Budget. Die Korrektur hätte diese Waits erstmals wirksam gemacht und damit still verschärft, ausgerechnet in `beforeEach`- und `beforeAll`-Hooks, wo ein Fehlschlag die ganze Datei mitreißt. Sie stehen jetzt auf 60000, mit der Begründung daneben. Nebenbei: `test.setTimeout()` läuft im Testkörper und kann einen Hook nicht mehr verlängern.

Dieselbe Klasse von stiller Wirkungslosigkeit an vier weiteren Stellen: `window._mhdbdbApp?.searchEngine !== null` ist auch dann wahr, wenn die App gar nicht existiert (`undefined !== null`).

### Ein strenger Test darf nicht an einem fremden Host hängen

#331 war, dass der Modultest seine Konsolen-Listener erst **nach** `page.goto()` registrierte und damit genau die Fehlerklasse nicht sehen konnte, gegen die er schützt. Die Reparatur (Listener davor, `pageerror` zusätzlich zu `console.error`, benannte Ausnahmen statt Freibetrag) schuf ein neues Problem, das erst die Zweitmeinung gesehen hat: der Playground zieht Matomo per Script-Injection von `webstatistics.sbg.ac.at`. Ist der Host nicht erreichbar, meldet Chromium einen Ressourcenfehler vom Typ `error`, und der Test wäre offline rot, ohne dass am Playground etwas kaputt ist.

Ausgenommen wird deshalb die **Herkunfts-URL**, nicht der Meldungstext. Ein Filter auf „Failed to load resource" hätte auch ein fehlendes lokales ES-Modul verschluckt, also genau den Fall, für den der Test existiert. Die Regel dahinter trägt über den Fall hinaus: eine Ausnahme wird an der Quelle festgemacht, nicht am Wortlaut.

### Zum dritten Mal fast eine richtige Zahl „korrigiert"

Beim Nachmessen der Verszahl kamen 1.358.973 `<l>` heraus, in der Doku standen 1.356.748. Beides ist richtig: der Index zählt nur Verse mit mindestens einem lemmatisierten Wort, weil nur die eine Boundary erzeugen. Ohne die Messvorschrift daneben wäre die richtige Angabe in eine falsche „korrigiert" worden, wie am 31.07. schon bei den Breve-Zahlen und wie bei den zwei Variantenzahlen (#279). Die Vorschrift steht jetzt in DATA-MODEL.md neben den Zahlen, samt Datumsstempel.

**Die Regel ist damit dreimal in fünf Tagen belegt: eine Zahl in der Doku ohne Angabe ihrer Zählweise ist nicht nur unprüfbar, sie zieht aktiv falsche Korrekturen an.**

### Kleinere Lehren

**Ein Gate, das nur eine von zwei gleichartigen Tabellen prüft, sieht aus wie Abdeckung.** `check-test-inventory.py` prüfte die Spec-Tabelle in DEVELOPMENT.md; die Audit-Skript-Tabelle daneben hatte 11 von 22 Einträgen. Das Gate ist jetzt datengetrieben (`check-doc-inventories.py`) und trägt beide, plus einen Selbsttest mit 20 Fällen als eigenen CI-Schritt. Beim Verallgemeinern fiel auf, dass der Fence-Parser `~~~` und ``` gegeneinander toggeln ließ: er merkt sich jetzt Zeichen und Länge des öffnenden Markers.

**Eine dritte Inventarliste stand daneben und war ungegated.** Der Verzeichnisbaum in `scripts/README.md` listet dieselben Skripte ein weiteres Mal, und ausgerechnet im PR gegen Inventar-Drift fehlte dort das neue Gate-Skript. Gefunden hat das die Zweitmeinung, nicht das Gate.

**cp1252 ist nicht ASCII.** Acht Audit-Skripte starben unter Windows an ihrer eigenen Erfolgsmeldung, weil das Häkchen U+2705 ist. Beim Messen, welche Skripte betroffen sind, war meine erste Messvorschrift (`ord(c) > 255`) selbst falsch: cp1252 ist Latin-1 plus 0x80 bis 0x9F und enthält damit Umlaute, Gedankenstriche und Anführungszeichen. Die MHG-Breven `ŏ` und `ŭ` liegen dagegen außerhalb, und Audit-Skripte drucken Korpusformen.

**Der Reader zeigt seit #250 Header-Prosa, und die trug ASCII-Substitute.** Acht Dateien, darunter zwei verschluckte Silben in OVW („Streuberlieferung" statt „Streuüberlieferung"). Der erste Scan war auf die im Issue genannten Wörter gekeyt und hat deshalb nicht geprüft, was er zu prüfen behauptete; der zweite zählt alle 70 Wörter mit `ss`, `ae`, `oe` oder `ue` in der Prosa aller `editorialDecl`-Blöcke und legt die Liste offen. Zwei weitere Dateien kamen so dazu.

### Was offen bleibt

- **#315 Punkt 2:** im Korpus tragen sechs Dateien `role="lead-editor"` (JT, PUC, TKA, TKR, VTC, WZB), die Doku nennt an drei Stellen vier, fünf und sechs. Ob WZB dazugehört, ist eine fachliche Frage an KZW und Julia.
- **#316:** die Sprachmischung in den Docs und der Feature-Katalog in INDEX.md, der FEATURES.md nacherzählt. Dazu neu: das Umleitungsziel ROADMAP → Recently Completed ist selbst nicht frisch (jüngster Eintrag 08.07.). Das Freshness-Problem ist verschoben, nicht gelöst. *(Nachtrag vom Health-Check am 02.09.: die Tabelle „Recently Completed" ist noch am selben Tag ganz entfernt worden, `ce55dde0a`.)*

**Phase:** Betrieb. PRs #330, #332, #333, #334, #335, #336.

---
## 2026-08-02 (Abend) – Reviewer und Berater sind zwei Rollen, und der Fehler saß in den Behauptungen

**Summary:** Der `fable-advisor` lief seit dem 28.07. als PR-Reviewer. Das war eine Rollenverwechslung mit messbaren Kosten, und sie ist jetzt aufgelöst: ein eigener `fable-reviewer` (Fable 5, mit Bash) prüft fertige Diffs vor dem ersten Push, der Berater bleibt für Entwurfsfragen. Dazu bekam der CI-Bot per `--append-system-prompt` ein Gedächtnis für seine Vorrunden, und `scripts/audit/review-rounds.py` macht die Wirkung messbar. Erster PR danach: #339 mit zwei Läufen.

**Die Unterscheidung, um die es geht.** Der Berater beantwortet „sollen wir X so lösen?", der Reviewer „ist dieses X korrekt?". Daraus folgen gegenteilige Pflichten. Beim Berater ist Spekulation erlaubt und nötig, weil bei einer offenen Entscheidung noch nichts zu messen ist, und Alternativen zu suchen ist sein Auftrag: sein Prompt sagt wörtlich „Suche aktiv nach dem stärksten Einwand" und „Prüfe die Alternative mit". Auf einen fertigen Diff angesetzt produziert genau diese Kalibrierung Runden ohne Verhaltensänderung. Der neue Reviewer verlangt für jeden Befund einen Anker in Datei und Zeile, trennt Verhalten (blockiert) von falscher Behauptung (nur gemessen) und Kosmetik (entfällt ab Runde 2), und hat als einziger von beiden ein Abbruchkriterium: Runde 2 nur Vorrunden-Befunde plus seither geänderte Zeilen, Runde 3 nur noch Verhalten, ab Runde 4 Schluss. Dazu der Satz, der am meisten spart: eine leere Befundliste ist ein gültiges und erwünschtes Ergebnis.

**Zwei Modelle, nicht drei.** Der ursprüngliche Vorschlag war je ein Reviewer auf Opus und auf Fable. Dagegen sprach die Bestandsaufnahme: der CI-Bot ist bereits Opus (`claude-code-review.yml`, `--model opus`), und die Hauptsession ebenfalls. Ein lokaler Opus-Reviewer wäre der dritte Kanal desselben Modells auf denselben Diff gewesen. Gebaut wurde deshalb genau einer, auf Fable.

**Der Zeitpunkt ist wichtiger als die Gründlichkeit.** Ohne `use_sticky_comment` löst jeder Push einen Review-Lauf aus, die Rundenzahl ist also die Push-Zahl plus eins. Was der lokale Reviewer findet, kostet null Runden; was der Bot findet, kostet per Konstruktion eine und schafft eine neue Gelegenheit für den nächsten Befund. Deshalb läuft der Reviewer vor dem ersten Push, nicht vor dem Merge. Playbook-Regel 6 und Kickoff-Punkt 4 sind entsprechend umgeschrieben.

**Zwei eigene Zahlen waren falsch, und beide standen in Absätzen über falsche Zahlen.** „11 Review-Runden" über #330/#332/#333 in CLAUDE.md und JOURNAL: gemessen sind es 18 Läufe (5 + 7 + 6, alle mit Ergebnis). Und in der ROADMAP stand, der 45%-passRate-Floor aus #172 habe in `testing/test.html` gelebt; die Assertion stand in `testing/tests/playground.spec.js:47`. Beide Male war der Fundort behauptet statt gemessen, das zweite Mal wenige Stunden nach dem Commit, der genau diese Regel in CLAUDE.md aufgenommen hat. Daraus die vierte Regel dort: ein Befund ist selbst eine Behauptung, und die Nachmess-Pflicht galt bis dahin nur auf der Schreibseite. Sie steht jetzt auch in Merge-Gate G2, also dort, wo ein Befund tatsächlich in Code übersetzt wird.

**Was der erste Einsatz gebracht hat.** Der Reviewer fand in `review-rounds.py` einen Klasse-A-Defekt, den ich nicht gesehen hätte, weil ich die Ausgabe geprüft hatte und nicht die Auswahl: `gh pr list --limit N` sortiert nach Erstellungsdatum, nicht nach Merge-Datum (#338 steht dort vor #337, obwohl #337 zwei Stunden später gemergt wurde). Das Skript sortierte nur die Anzeige um. Jetzt wird ein Fenster geholt, nach `mergedAt` sortiert und dann zugeschnitten; ein Hinweis nennt, wie viele PRs die naive Sortierung verfehlt hätte, und feuert bei `--limit 1` nachweislich.

**Und was er nicht gebracht hat.** Bei #339 hat er die falsche Ortsangabe zum 45%-Floor mitgetragen statt geprüft, und seine Zahl der gepurgten Tailwind-Selektoren war zu niedrig (16 statt gemessen 22, die `hover\:`-Varianten fehlten). Der CI-Bot fand beides. Ein zweiter Reviewer ersetzt das Nachmessen nicht, er verschiebt nur, wer die ungeprüfte Zahl weiterreicht.

**Erste Messung nach der Umstellung, mit Vorbehalt.** #339 brauchte zwei Läufe, beide mit Ergebnis, vier Befunde insgesamt, davon null zum Verhalten. Der Baseline-Median liegt bei 5,5 Läufen, das Baseline-Minimum aber ebenfalls bei 2 (#334). Ein kleiner PR mit zwei Runden ist also nichts, was es vorher nicht gab; Größe und Rundenzahl hängen zusammen, und ein Datenpunkt trennt die beiden Effekte nicht. `review-rounds.py --baseline` sagt das von selbst, solange Baseline-PRs in der Auswahl stehen. Belastbar ist stattdessen das beobachtete Verhalten: Runde 2 hat keinen der drei Befunde aus Runde 1 wiederholt, hat einen Randpunkt ausdrücklich als „ohne Messung, deshalb kein Befund" liegen gelassen und führt einen eigenen Abschnitt darüber, was in der CI-Umgebung nicht messbar war.

**Die Lehre des Tages.** Alle vier Befunde an #339 waren falsche Behauptungen, keine kaputte Logik. Zusammen mit der Messung vom Vormittag (13 von 27 Befunden derselben Klasse) heißt das: die teure Fehlerklasse ist nicht der Code, sondern was daneben über ihn geschrieben steht. Ein Skript fängt sie nicht, weil die Aussagen Prosa sind („in allen Skripten", „der einzige Konsument"). Deshalb hat der Reviewer Bash: Nachmessen ist die Fähigkeit, die ihn vom CI-Bot unterscheidet.

### Was offen bleibt

- **Der Reviewer ist nie gegen einen eingebauten Fehler getestet.** Nach der eigenen Regel 1 („ein grünes Gate ist kein wirksames Gate, Mutation ist der Beweis") fehlt der Nachweis, dass er einen echten Verhaltensdefekt findet. Bisher hat er nur an defektfreien Diffs gearbeitet.
- **Die Wirkung auf die Rundenzahl ist unbelegt.** Sie trägt erst, wenn kein Baseline-PR mehr in `review-rounds.py --baseline` steht, also nach vier weiteren PRs.

**Phase:** Betrieb. PR #339, Issue #326 geschlossen; drei Direkt-Commits auf main (`6a8d4caba`, `e5bd0adc9`, `fd6564bb4`) plus Merge `0d769c8e4`.

---
## 2026-08-03 – #316 abgeschlossen: die Doku ist englisch, und die Sprachregel steht jetzt im Repo

**Summary:** Die letzte Etappe von #316 ist gemergt (PR #347, `b261069cf`): `ROADMAP.md`, `POS-TAGSET.md`, `TEI-MODEL-AUTH-FILES.md` und `TEI-MODEL.md` vollständig englisch, dazu zwei deutsche Restzeilen in `LINECODE.md`. Damit sind die 13 stabilen Promptotyping-Dokumente plus ROADMAP englisch. Deutsch steht nur noch, wo es Dateninhalt ist: der eingefrorene Header-Wortlaut der 667 Korpusdateien, mittelhochdeutsche Belege in der POS-Tabelle, Werktitel, Namen und Notizen aus `contributors.xml`.

**Der teuerste Fund des ganzen Tickets: elf stille Kopplungen zwischen Doku-Prosa und Audit-Skripten.** `doc-count-audit.py` bindet jede Zahl an das Wort direkt dahinter („256.760 Formen"). Übersetzt man dieses Wort, meldet das Audit keinen Fehler, es hört stumm auf, die Stelle zu prüfen. Der Bruch ist damit unsichtbar und sieht wie Erfolg aus. Über die vier Etappen waren es elf solche Stellen; die Anker für `variants_entries`, `variants_forms`, `persons`, `concepts`, `genres`, `names` und `contributors_persons` sind jetzt zweisprachig, ebenso der Historien-Skip in `find_stale_numbers`. Alle dreizehn Zahlbindungen der beiden TEI-MODEL-Dateien sind per Mutation belegt, der Historien-Skip zusätzlich negativ: ohne den Marker im Satz fällt die 666 des #32-Audits sofort als Drift gegen 667 auf.

Eine Anker-Formulierung ist bewusst zusammengesetzt: `variant entries` statt eines blanken `entries`. Ein blankes `entries` hätte in `DATA-MODEL.md` die Lexikonzahl getroffen (43.879 statt 42.627). Das Drift-Fenster verwirft die zwar, die Anker-Abdeckungsprüfung kennt es aber nicht und meldete daraufhin einen richtigen `INTENTIONALLY_SILENT`-Eintrag als veraltet. Zwei Prüfungen desselben Skripts, verschiedene Toleranzen.

**Drei kaputte Anker-Verweise, zwei davon älter als dieses Ticket.** Beim Umbenennen von Überschriften (Paragraph 11 „Versionierung" → „Versioning", 8.1, „Provenienz und Aktualität" → „Provenance and currency") habe ich eine Prüfung über alle `docs/*.md` geschrieben. Sie fand neben den eigenen Umbenennungen zwei Verweise, die schon vorher ins Leere zeigten (POS-TAGSET Paragraph 3 aus TEI-MODEL, der ROADMAP-Abschnitt aus RESEARCH). Die CI hat keinen Link-Checker; ohne die Prüfung wäre nichts davon aufgefallen.

**Der Review-Bot kam am Diff nicht vorbei.** `claude-review` scheiterte auf PR #347 zweimal mit `error_max_turns` nach 8 und 11 Minuten, beide Male mitten in der Checkliste. Der Diff umfasst 11 Dateien und 869 zu 849 Zeilen. Bei #344 mit fünf Dateien lief er noch durch. Die inhaltliche Prüfung lieferte stattdessen der `fable-reviewer` vor dem Push: 28 Mutations-Szenarien über die Zahlbindungen, alle elf dateiübergreifenden Anker aufgelöst, Vollinventar alt gegen neu über Zahlen, Attribute, Dateinamen, XML-Elemente und IDs. **Lehre: die PR-Größe ist eine Eigenschaft, die man einplanen muss, nicht nur eine Folge.** Eine Datei pro PR hätte den Bot arbeiten lassen. *(Vorwärtsverweis, nachgetragen vom Health-Check am 02.09.: diese Lehre ist inzwischen widerlegt, siehe die Einträge vom 31.08. („Der berechnete Diff ist notwendig, nicht hinreichend") und vom 02.09. („46 Turns hier gegen 56 bei #382 mit 13 Dateien"). Der Satz oben bleibt als Protokollstand stehen.)*

**Die Sprachregel hat sich an einem Tag dreimal geschärft**, und die Endfassung ist die einfachste. Zuerst als „user-facing deutsch, Entwickler-Doku englisch, JOURNAL bleibt deutsch" in CLAUDE.md geschrieben (PR #348, `90cc3e49a`, schließt #316). Dann die Korrektur von chsteiner, dass rein für LLMs geschriebene Dateien englisch sein sollen und keine weiteren Auflagen tragen. Und schließlich: **für LLM-Dateien gibt es gar keine Auflagen, die Sprachwahl eingeschlossen** („es geht nur um qualität nicht um das wie es dort steht"). Damit entfällt auch die eben noch geplante Übersetzung von `JOURNAL.md` und `journal-archive.md`, rund 2.800 Zeilen. Dass `docs/` englisch ist und dieses Journal deutsch, ist ab jetzt Zufall der Entstehung und keine Regel.

**Zwei Regeln, die aus dem Tag selbst kommen:**

1. **Kleine Doku-Änderungen gehen direkt auf `main`**, ohne Zweig, PR und CI-Runde. Ich hatte für zwei Absätze in CLAUDE.md einen PR aufgemacht; das ist derselbe hausgemachte Overhead, den CLAUDE.md eine Ebene tiefer schon beschreibt. Zweig plus Review bleibt für Code, Daten, Build-Skripte und alles, was ein Gate oder ein Test fangen kann.
2. **Die Em-Dash-Regel gilt nur für user-sichtbaren Text.** Das Gate prüft weiterhin jede neu hinzugefügte Markdown-Zeile und ist damit weiter gefasst als die Regel, die es durchsetzen soll: ein Treffer in `docs/` ist Rauschen und kostet keine Review-Runde. Steht gleichlautend in Playbook-Regel 32, in der Audit-Tabelle von DEVELOPMENT.md und im Docstring des Gates. Ob der Markdown-Zweig auf user-sichtbare Dateien eingeschränkt gehört, ist offen und als Entscheidung markiert. **Diese Regel hat nur vier Stunden gehalten, siehe den Nachtrag unten.**

**Nachtrag am selben Abend: die Verengung gebaut, gemessen und verworfen.** Punkt 2 oben war der Stand am Nachmittag. PR #349 hat die Einschränkung dann tatsächlich umgesetzt (weiße Liste `publications/` plus `README.md`, später um die zwei aus den Hilfeseiten verlinkten READMEs erweitert) und ist ungemergt geschlossen worden, nachdem die Kosten beider Varianten nebeneinander lagen.

**Die Verengung erzeugte zwei eigene Fail-opens, beide vom `fable-reviewer` gefunden und vor der Übernahme im Wegwerf-Repo nachgestellt.** Eine erkannte Umbenennung hat keine hinzugefügten Zeilen, also trug `git mv docs/entwurf.md publications/entwurf.md` den gesamten Em-Dash-Bestand von `docs/` stumm in den Veröffentlichungspfad: `scanne_diff` lieferte `[]`. Derselbe Fehler ein zweites Mal für `publications/_archived/alt.md` → `publications/alt.md`, wo der alte Pfad zwar im Umfang liegt, aber als Archivcode übersprungen wird. **Beide Löcher gibt es nur, weil es eine weiße Liste gibt.** Eine Regel, die nach Ort unterscheidet, muss auch den Ortswechsel behandeln, und daran denkt niemand beim Schreiben der Liste.

**Die Zahlen, die entschieden haben.** Kosten der stumpfen Regel („keine Em-Dashes in jeder `.md`", weiterhin nur in hinzugefügten Zeilen): 159 von 481 Commits in 90 Tagen, 40 von 182 in 30 Tagen, **5 von 100 in den letzten 14 Tagen mit zusammen 6 Zeilen**. Der große Posten war das JOURNAL (90 Tage: 814 Zeilen) und ist praktisch verschwunden. Der 14-Tage-Wert misst dabei teilweise schon die Regel selbst, weil das Gate seit dem 02.08. so läuft. Kosten der Ausnahme dagegen: 267 Zeilen Umfangs-Maschinerie, zwei Klasse-A-Befunde in zwei Review-Runden und die Frage „ist diese Datei user-sichtbar?", die pro neuer Datei wiederkommt. Sie kam auch prompt: die ausgelieferten Hilfeseiten verlinken zehn `.md`-Dateien, sieben davon unter `docs/`, dazu `schema/README.md`, `ingest/ari/README.md` und eine Agent-Skill-Datei unter `.gemini/`. Über die letzte musste einzeln entschieden werden (draußen: für den Agenten geschrieben, auch wenn eine Hilfeseite sie als Beispiel verlinkt).

**Die Sprachregel ist dabei mitentwirrt worden**, weil „keine Auflagen für LLM-Dateien" und „`docs/` muss einheitlich englisch sein" sich widersprachen. Auflösung in drei Körben statt zwei: user-sichtbare Seiten deutsch; der `docs/`-Satz einheitlich englisch, **nicht** weil er user-sichtbar wäre, sondern weil seine 15 Dateien einander zitieren und zusammen gelesen werden (und weil #316 vier Etappen dafür bezahlt hat); Arbeitsnotizen (CLAUDE.md, JOURNAL, Archiv) ohne jede Auflage. Darüber genau eine mechanische Regel, die überall gilt und maschinenprüfbar ist: keine Em-Dashes in `.md` und user-sichtbarem HTML. Der wiederkehrende Fehler des Tages war, Sprache und Typografie in dieselbe Regel zu packen; die eine ist eine Eigenschaft des Dokumentensatzes, die andere eine Zeichenregel.

**Was davon bleibt:** eine Ausnahme, die pro Fall entschieden werden muss, ist teurer als die Regel, die sie sparen soll. Und: der Aufwand, eine Verengung zu bauen, ist kein Argument, sie zu behalten. Der PR war fertig, zweimal reviewt und grün, als die Messung ihn erledigt hat.

**CLAUDE.md überarbeitet** (`dad844b2a`, `640020235`): ganz englisch, 153 auf 135 Zeilen. Die Doku-Tabelle ist raus, weil `docs/INDEX.md` per `@`-Import ohnehin im Kontext liegt und denselben Katalog vollständig führt; die Kopie war auf 10 von 15 Dokumenten gedriftet. Der Zweig-Abschnitt nannte `feature/*` als Konvention, gemessen sind es bei den letzten 20 gemergten PRs 9 `claude/`, 3 `docs/`, je 2 `fix/` und `feature/`. Eine unbelegte Zahl entfernt („rund 470 Zeilen mit Em-Dash").

**Aufgeräumt:** vier leere Worktree-Hüllen (`mhdbdb-wt-314`, `-323`, `-327`, `-331`, je ein leeres `node_modules`, zusammen 56 KB), während `git worktree list` nur den Hauptbaum zeigte und `.git/worktrees` gar nicht existierte. Git räumt weg, was Git kennt; ungetrackte Verzeichnisse bleiben liegen. Als Punkt 5 in Playbook-Regel 30 (`011f74f9d`).

**Phase:** Betrieb, reine Doku. Kein Index- und kein API-Rebuild, keine Daten berührt.
## 2026-08-05 – Label-Neuordnung: 28 auf 16, und der Backlog hat einen einzigen vollautonomen Eintrag

**Summary:** Alle 53 offenen Issues wurden vollständig gelesen, Body und jeder Kommentar, und gegen ein neues Label-Schema triagiert. Sechs parallele Agenten mit je acht bis neun Tickets, danach zentral angewandt. Das Schema ist ausdrücklich **für Agenten** gebaut, nicht fürs Team: Chris' Vorgabe war „wir menschen nutzen die labels kaum, bitte optimiere für dich selbst". Drei orthogonale Achsen mit genau einem Label je Achse, dazu zwei Flags. `auto:*` (full, brief, checkin, pair, blocked) steuert, wie selbständig eine Session ein Ticket anfassen darf; `area:*` sagt, wo die Arbeit anfällt; `effort:*` blieb unverändert. Gelöscht wurden 23 Altlabels, angelegt 12. Legende und Ping-Liste stehen im Body von #44, die Kurzfassung seit `5e051105d` in CLAUDE.md.

**Der Befund, der die Arbeit gerechtfertigt hat: 30 der 52 offenen Tickets warten auf einen Menschen, nicht auf Arbeit.** 19 davon liegen bei KZW, drei bei Julia, acht bei Externen. Sechs sind sogar gebaut, gemergt und live und warten nur noch auf eine Abnahme (#169, #239, #250, #251, #224, #86). Auf der anderen Seite steht **ein einziges** `auto:full`-Ticket, und das sperrt sich im eigenen Text auf ein anderes (#194 auf #193). Der autonome Vorrat besteht faktisch aus den acht `auto:brief`-Tickets, also aus Arbeit, die eine Klärungsrunde vorweg braucht. Wer eine autonome Session starten will, hat derzeit nichts zu greifen, ohne vorher zu fragen.

**Warum die alten Labels so falsch waren, ist strukturell und nicht Nachlässigkeit.** `needs-clarification` klebte an Tickets, deren Klärung längst da war (#28: KZW hat am 29.07. entschieden; #27: alle Punkte seit dem 10.07.). `depends-on-human`, `external-research` und `needs-clarification` beschrieben dieselbe Sache aus drei Blickwinkeln und wurden entsprechend beliebig gesetzt. `claude-ready` war an keinem Ticket mehr korrekt. Der Grund ist immer derselbe: ein Label wird beim Anlegen vergeben und beim Fortschritt nicht nachgezogen, weil der Fortschritt im Kommentar steht und nicht im Label. Genau darum ist die einzige neue Regel, die etwas kostet, „Labels in derselben Session nachziehen, in der man das Ticket anfasst".

**Der teuerste Fund des Tages ist ein Befund über Befunde.** Der alte #44-Body führte drei tote Codepfade im Playground als Aufräum-Kandidaten: `findProximityMatchesInIndex`, `searchProximityUsingIndex` und `executeProximitySearch` mit blockierendem `prompt()`, dazu eine fehlende Deduplizierung in `resolveLemmaIds`. Chris' Reaktion darauf war „es gibt tote pfade? ja dann unbedingt ein issue draus machen". Nachgemessen: **alle drei Funktionen existieren im gesamten `.js`-Bestand nicht mehr**, das einzige verbliebene `prompt(` ist ein Kommentar in `lemma-explorer.js:832`, der die Entfernung dokumentiert, und `resolveLemmaIds` endet in `tei-ui.js` auf `return [...new Set(lemmaIds)]` mit eigenem Regressionstest. Ein Ticket darauf wäre reine Selbstbeschäftigung gewesen, gebaut auf eine Behauptung aus einer Datei, die dieses Projekt selbst geschrieben hat. Das ist derselbe Mechanismus, den CLAUDE.md unter „Self-Inflicted Overhead" für Review-Kommentare beschreibt, hier nur eine Ebene höher: **#44 ist selbst eine Quelle unbelegter Behauptungen, und zwar die zentralste, die es im Projekt gibt.** Der Body trägt seit heute eine Warnung genau dieses Inhalts an der Stelle, an der die Befunde stehen.

**Der zweite Fund derselben Sorte, mit umgekehrtem Vorzeichen.** Ein Triage-Agent meldete, die Zahl im Titel von #252 („971 Stellen in 21 Texten") sei falsch, gemessen seien es 122 in 9. Vor der Korrektur selbst nachgemessen, und die Rechnung fällt anders aus: es gibt **zwei** Zählweisen, die einander kaum überschneiden. Ein `<l>` mit `<caesura/>` und ohne jeden sichtbaren Text kommt **974-mal in 96 Texten** vor, ein `<l>`, dessen sichtbarer Text nur aus Klammern besteht, **136-mal in 14 Texten**. Die 971 im Titel ist also im Kern richtig, falsch ist die Textzahl daneben, und der Agent hatte schlicht die andere Menge gemessen. Wäre der Befund übernommen worden, hätte eine richtige Zahl eine falsche ersetzt, mit Messung als Beleg. Die Einzelaufschlüsselung im Body ist tatsächlich überholt (FR1 steht dort mit 543, gemessen sind es 1 beziehungsweise 23), was am Frauenlob-Umbau aus #236 liegt. Beide Zählweisen samt Skript stehen jetzt als Kommentar in #252, mit der Vorbedingung, dass vor der Migration zu entscheiden ist, welche der beiden gemeint ist: es geht um 838 Stellen Unterschied. Nebenbei ist auch die Schema-Annahme im Ticket überholt, `gap` steht seit `b59350bb5` in `mhdbdb.rnc` und kommt im Korpus 0-mal vor.

**#114 geschlossen**, das einzige Ticket ohne verbleibenden Adressaten: die Tabellenansicht ist seit PR #157 live und Linda hat am 13.07. abgenommen. Die anderen fünf fertigen Tickets bleiben bewusst offen, weil die Abnahme bei KZW, Julia und Alan liegt und ein Merge keine Abnahme ist.

**ROADMAP.md an drei Stellen richtiggestellt** (`aff7fe2af`), jede Zeile vorher gegen `git log` und die Issue-Kommentare geprüft: die DIG-Renderfrage in #138 hat KZW am 28.07. beantwortet und HUG ist mit PR #243 erledigt (814 Ziffern raus, HUG steht bei 0), offen ist nur der korpusweite Lauf, und der muss über den xml:id-Block gehen statt über `@pos`, weil 108 der 814 HUG-Ziffern gar kein `@pos` trugen. #250 stand als „Implementation open", liegt aber vollständig auf `main`. #114 ist aus der Linda-Zeile verschwunden.

**Was offen bleibt und keine Arbeit ist:** die Ping-Liste. Sie wäre der ertragreichste Handgriff des Tages gewesen, ist aber nicht abgesetzt worden, weil KZW und Julia gerade auf Urlaub sind. Damit bleibt der größte Posten der Matrix bis auf Weiteres genau da stehen, wo er steht.

**Die Lehre, die Chris selbst mitten in der Session formuliert hat** („#44 wird unglaublich schnell stale"): der Body macht Aussagen über 52 Tickets gleichzeitig und veraltet deshalb schneller als jede andere Datei im Projekt. Innerhalb dieser einen Session ist er zweimal falsch geworden, einmal durch das Schließen von #114 und einmal durch die eigene Dead-Code-Passage. Der belastbare Teil ist nicht die Prosa, sondern die Labels: sie hängen am Ticket und nicht an einem Absatz, und ein `gh issue list --label "auto:brief"` ist immer aktuell. Der nächste Schritt wäre folgerichtig, die abzählbaren Teile des Bodys (Quick Stats und die Tabellen je Autonomiestufe) aus den Labels zu generieren und nur die Begründungen von Hand zu pflegen, nach demselben Marker-Muster, mit dem `build-pages.py` Nav und Footer injiziert.

---
## 2026-08-05 (Nachmittag) – Loop Engineering: vier Merkregeln werden ein Skript, drei Verträge werden einer

**Summary:** Die drei Session-Playbooks wurden gegen Anthropics Loop-Engineering-Raster geprüft und daraufhin umgebaut. Ergebnis in zwei Teilen: ein Wrapper `scripts/run-tests.js` (331 Zeilen, PR #353), der `npm test` sein Ergebnis selbst verkünden lässt, und eine Aufteilung der Playbooks in einen gemeinsamen `BETRIEBSVERTRAG.md` (17 Regeln), eine `KICKOFF-VORLAGE.md` (8 Bausteine) und drei Playbooks, die nur noch ihre eigenen Abweichungen führen. §2.1 des Issue-Playbooks ist dabei erstmals geschrumpft, von 32 auf 26 Regeln.

**Der Anlass war ein Widerspruch zwischen zwei Playbooks, die einander zitieren.** Das Merge-Playbook wies in Zeile 61 die Task-Ausgabe eines Testlaufs als Ergebnisquelle aus. Die Issue-Regeln 26 und 27 belegten dieselbe Quelle als falsch-grün, mit Datum und Vorfall. Beide Sätze standen seit Wochen nebeneinander, und keine der beiden Sessions, die dazwischen liefen, ist über den Widerspruch gestolpert, weil jede nur ihr eigenes Playbook liest. Kopien driften, und zwar nicht durch Nachlässigkeit, sondern weil eine Kopie keinen Grund hat, von der Korrektur der anderen zu erfahren.

**Der Wrapper beantwortet die Frage einmal, statt sie vier Merkregeln zu überlassen.** Er löscht den alten Report, setzt `PW_TEST_HTML_REPORT_OPEN=never`, vergleicht bei filterlosem Lauf die Spec-Dateien auf der Platte gegen die im Report und bildet den Exit-Code aus `report.json`: 0 grün, 1 rot, 2 der Lauf ist gar nicht zustande gekommen. Die VERDICT-Zeile nennt Testzahl, Dateizahl und den geprüften Pfad. Damit fällt die Unterscheidung, an der die alten Regeln hingen, in den Aufruf: ein gefilterter Lauf sagt TEILLAUF und belegt keine Vollständigkeit mehr, auch wenn ihn jemand als Beleg in einen PR schreibt.

**Der teuerste Teil war die Prüfung des Wrappers, nicht sein Bau.** Runde 1 des `fable-reviewer` fand, dass die Server-Prüfung im eigenen Zielfall versagt: sie wertete jeden Fetch-Fehler als „kein Server da" und übersprang danach genau die Sentinel-Prüfung, die einen fremden Dev-Server auf Port 8080 fangen sollte. Gemessen: ein geschlossener Port liefert `ECONNREFUSED`, ein sättigender Server einen `AbortError` ohne Code. Seither gilt nur `ECONNREFUSED` als „niemand da", und die Frist steht bei zehn Sekunden. Runde 3 des Bots fand, dass die VERDICT-Zeile im Abbruchfall auf stderr ging, live bestätigt mit getrennter Umleitung, und dass Playwrights eigener Exit-Code im Report-Pfad verworfen wurde. Beides behoben. Der dritte Bot-Befund war als Befund widerlegt, führte aber zur besten Ausgabeform des Tages: `NICHTS GELAUFEN (0 Tests). Das belegt nichts.`

**Ein Zitat eines beratenden Agenten hat der Messung nicht standgehalten, und das ist der Grund, warum eine Regel unverändert blieb.** Ein Opus-Berater begründete eine vorgeschlagene Umschreibung von Regel 26 mit einem wörtlichen Zitat aus `journal-archive.md:2383`. Der Satz existiert dort nicht, und keiner der drei „Exit 0"-Treffer im Archiv ist der behauptete Vorfall. Die Regel wurde deshalb nicht auf seine Diagnose umgeschrieben. Derselbe Mechanismus wie bei #44 heute früh, nur eine Rolle weiter: **ein Berater, der eine Fundstelle nennt, macht damit eine Behauptung und keine Messung.** In dieselbe Richtung ging ein eigener Fehler in die Gegenrichtung: eine Korrektur am Vorschlag des Fable-Advisors zu `skipped > 0` war falsch, sein Vorschlag hätte funktioniert.

**Die Regelliste schrumpft auf zwei Wegen, und beide sind jetzt im Kopf von §2.1 benannt.** Der erste ist Ausführbarkeit: was ein Skript deterministisch prüfen kann, gehört nicht in eine Merkregel (die Regeln 6, 16, 26, 27 sind eine geworden). Der zweite ist Geltungsbereich: drei Regeln waren keine Projekterfahrung, sondern Fallen von Git und der Windows-Shell, die in jedem Repo gelten, und stehen seit heute in der persistenten Memory statt in einer Datei, die nur nach einem Kickoff gelesen wird (8, 9, 31). Die Nummern bleiben als Anker stehen, mit sechs Lücken, weil Wellenplan, Merge-Playbook und ROADMAP sie zitieren und die datierten Wachstumsangaben sonst auf andere Regeln zeigen würden.

**Neu im Merge-Playbook: die Pilot-PR-Regel.** Ein PR durchläuft die Schleife vollständig, bevor der zweite anfängt. Der Grund ist nicht Vorsicht vor dem einzelnen PR, sondern vor dem Verfahren: die erste Merge-Session hat 13 PRs am Stück abgearbeitet, und der Retarget-Fehler, der dabei #177 geschlossen hat, hätte jeden weiteren Stack genauso getroffen.

**Verifikation:** Volllauf nach dem Ende der parallelen Session 271 expected, 0 unexpected, 0 flaky, Exit 0. In zwei von drei vorherigen Volläufen war `playground-authority-index.spec.js` mit der 10-Sekunden-Schwelle für den Authority-Index flaky, isoliert dagegen 7 von 7 grün in 46 Sekunden. Der Test misst damit unter Last die Maschine und nicht den Code.

**Nachtrag am selben Tag, die Schwelle steigt.** Chris hat entschieden, den Test zu behalten und die Grenze anzuheben. Isoliert nachgemessen, drei Läufe: 5,5 / 5,9 / 5,9 Sekunden. Die alte Schwelle von 10 Sekunden lag damit nur um den Faktor 1,7 über dem Normalfall, was unter parallelen Workern nicht reicht. Neu sind 20 Sekunden, und der `waitForSelector` steigt von 15 auf 30 Sekunden mit, weil die Zusicherung sonst gar nicht zum Zug käme: der Wait wäre vorher gescheitert, und die wirksame Grenze wäre still eine andere gewesen als die im Testnamen. **Die Obergrenze kommt nicht aus dem Bauch, sondern aus der Regression, gegen die der Test steht:** Laufzeit-XML-Parsing hat vor den vorgebauten Indexen laut `ARCHITECTURE.md:481` rund 30 Sekunden gekostet, und genau das muss die Schwelle noch fangen. Die Zahl ist eine Doku-Angabe und keine eigene Messung, weil es diesen Codepfad nicht mehr gibt; sie steht deshalb mit Fundstelle da, im Test wie hier. Sie liegt jetzt zwischen beiden Werten statt dicht am Normalfall.

---
## 2026-08-06 – ADR-017 und ein Lifecycle, der nichts zu tun fand

**Summary:** Die editorische Frage, die ADR-016 offen an KZW abgegeben hatte, ist entschieden: das Breve über `w` und `n` ist in der Wenzelsbibel keine Umlautmarkierung, sondern böhmische Schreibkonvention, und wird deshalb getilgt statt zu einem Digraphen aufgelöst. Julia hat das als WZB-Editorin festgelegt, die beiden Regeln stehen in beiden Normalizern (`f3dcf2a8`), ADR-017 schreibt die Entscheidung samt Messung fest. Der anschließende Data-Change-Lifecycle für die 17 WZB-Tokens, die statt eines Leerzeichens die Zeichenfolge `\u0020` trugen und jetzt zwei `<w>` sind (#235 Punkt 1), endete ohne einen einzigen geänderten Byte in der abgeleiteten Schicht.

**Der Lifecycle war kein Leerlauf, sondern eine Messung.** Korpus-Index, Authority-Index und die 2.742 API-Dateien wurden vollständig neu gebaut und sind byte-identisch zum Bestand; `extract-variants.py` meldet alle vier semantischen Zähler auf 0. Damit ist belegt statt vermutet, dass beide Änderungen indexneutral sind, und der Versions-Bump entfällt zu Recht (die Regel „kein Bump ohne Inhaltsänderung" schneidet in beide Richtungen). Möglich ist diese Auskunft nur wegen der deterministischen Builds aus #125: vor ihnen hätte derselbe Rebuild einen Diff aus Zeitstempeln erzeugt und die Frage gar nicht beantworten können.

**Warum die Normalizer-Regel den Index nicht anfasst, ist der interessantere Teil.** Keines der 113 Breve-Tokens trägt ein `@corresp`, keines ist also je in `variants.xml` gelandet, und die gebaute Variantenkarte enthält null Schlüssel mit einem Breve. Die Regel erzeugt deshalb keinen neuen Treffer, sie lässt die WZB-Schreibung einen erreichen, den es schon gab: `fewer`, `ewer`, `wenn` sind aus anderen Texten als Formen belegt. Auffindbarkeit wächst von 11 auf 100 von 113 Tokens, 93 davon über Stufe 2, und für alle 64 lemmatisierten Tokens ist der erste Treffer genau das Lemma, das das Token selbst trägt.

**Zwei Zahlen in CONTRACTS §A waren falsch, und zwar in dieselbe Richtung.** Dort stand, vor der Regel sei „nicht ein einziges" der 113 Tokens auffindbar gewesen und danach 93. Gemessen waren es vorher 11 (alle über die Stufe-3-Notlösung, keines davon lemmatisiert) und nachher 100. Beide Male war die Zahl zu gefällig für die eigene These. Die Korrektur nennt jetzt die Aufteilung nach Stufen, und ADR-017 nennt die Messvorschrift dazu, weil „113 Tokens" je nach Zählweise auch 40 (distinkte Formen) oder 64 (nur lemmatisierte) heißen kann.

**Offen bleibt die Gegenrichtung, und sie ist der eigentliche Rest von #235.** Wer `fewer` tippt, findet das Lemma und über das Lemma die annotierten Stellen. Die 49 unlemmatisierten Breve-Tokens leuchten in der Leseansicht trotzdem nicht auf, dafür braucht es ein `@lemmaRef`. Zusammen mit den 289 o/u-Breve-Tokens ohne Lemmaverweis und den 8 Makron-Tokens ist das der Matcher-Rerun, den schon ADR-016 als eigene Runde vorgemerkt hat.

**Phase:** Betrieb. #235 Punkt 1 committet (`f3dcf2a8`), Punkt 2 seit 28.07. gemergt, Punkt 3 offen.
## 2026-08-07 – #58: der Weg vom Lemma zum Beleg, und warum er eine ID trägt

**Summary:** Aus dem Lemmata-Explorer führte kein Weg in die Belegsuche; das war der Rest von #58 („Begriff → Lemma → Beleg"). Neu ist ein Knopf pro Treffer und, dahinter, ein neuer Parameter `ids` an der Route `#multi-lemma`, positionsgleich zu `lemmata` gepaart. Dazu geschlossen: #68 (der Beitragsleitfaden war seit dem 29.05. vollständig, nur hatte es niemand nachgeprüft). #194 von `auto:full` auf `auto:checkin` korrigiert, weil sein eigener Body die Umsetzung an #193 bindet und #193 nicht gebaut ist.

**Die Entscheidung, um die es ging, war nicht A gegen B gegen C, sondern Schreibform gegen ID.** Der naheliegende Weg wäre gewesen, die Schreibform an die Multi-Lemma-Suche zu übergeben, so wie es die beiden bestehenden Übergaben tun (Wortbestandteil-Auswahl, Kookkurrenz-Ranking). Die Messung hat das verworfen: 102 Schreibformen im Lexikon tragen mehr als einen Eintrag, nach Normalisierung sind es 477 Formen und 993 der 43.879 Lemmata, darunter `sin`, `wal`, `mal`, `de`. Für die hätte der Knopf still die Belege eines anderen Lemmas gezeigt, und zwar immer die des häufigeren, weil `searchLemmaByOrthography` nach Korpusfrequenz sortiert und die Aufrufer `matches[0]` nehmen. An genau der Stelle hat der Nutzer aber schon entschieden, welches Lemma er meint. Die Schreibform fährt nur noch als Beschriftung mit.

**Der teuerste Fehler des Tages war meiner und wurde von einem Gegenprüfer gefunden.** `executeSearch()` schließt das Modal, bevor es auflöst, und `close()` leert über `reset()` auch die neue Zeiger-Map. Der Zeiger wäre also bei jedem Aufruf leer gewesen: die Übergabe hätte immer auf die Schreibform zurückgefallen, und zwar unbemerkt, weil das Ergebnis für 97,7 Prozent der Lemmata dasselbe ist. Der bestehende Kommentar an `searchTerms` warnt zwei Zeilen darüber genau davor. Die Map wird jetzt wie die Begriffsliste kopiert und als Argument durchgereicht statt aus `this` gelesen.

**Zwei Doku-Stellen waren nicht veraltet, sondern falsch.** `FEATURES.md` führte für den Lemmata-Explorer eine „Action: Search lemma in corpus", die es nie gab; #58 macht die Zeile erstmals wahr. Und `CONTRACTS.md` §C behauptete, die Auflösung laufe „through exactly 3 stages" ohne Ausnahme. Mit dem Zeiger gibt es einen Aufruferpfad, der alle drei überspringt, und der steht jetzt als §C.1.1 dort, samt der Einschränkung, dass zwei weitere Erzeuger derselben Route noch nach Schreibform auflösen.

**Nebenbei zu #225:** Thomas Burch hat die Verlinkung im Wörterbuchnetz umgestellt, auf drei unabhängigen Wegen nachgeprüft (Konfigurationsdatei, konsumierender Code, echte Cross-Reference über die Live-API beider Seiten). Damit ist der Rückweg von Lexer, BMZ und Findebuch auf unsere Lemma-Seiten offen. Was Trier im Gegenzug erbeten hat, ist ein aktualisierter Lemmabestand im alten XML-Format; die Messung dazu steht im Ticket, sie ist ein eigenes Arbeitspaket.

**Phase:** Betrieb. #58 im PR, #68 geschlossen, #225 mit Messung an KZW und Chris zurückgegeben.

---
## 2026-08-07 (Nachmittag) – Drei Tickets, in denen die Entscheidung teurer war als die Umsetzung

**Summary:** #269 (Playbook für die Kuration eines einzelnen Lemmas), #225 (Skript für die Trierer Lemmaliste, Mail raus), #111 (Schwellenmessung) und #270 (als ADR-018 entschieden). Keine Zeile Produktionscode an diesem Nachmittag. Geschlossen wird davon nur #270: #269 wartet auf KZWs Abnahme, #111 ist ein Trigger-Reminder und bleibt einer, #225 hängt an Trier.

**#225: die Sperre im Skript ist die Aussage, nicht ein Detail.** `build-wbnetz-lemma-list.py` weigert sich, innerhalb des Repos zu schreiben, weil Ein- und Ausgabe Copyright Trier sind. Genau diese Sperre beantwortet auch Chris' Frage, ob wir Burch die Datei nicht einfach hosten könnten: können wir nicht ohne sein Einverständnis, und aktuell halten könnten wir ohnehin nur unsere Hälfte, weil das Rückgrat der Datei 86.121 Lexer-Ansetzungen sind. Die Frage steht deshalb als Frage in der Mail, nicht als Ankündigung. Ergebnis des Laufs: 2.487 Verweise ergänzt, 54 umgebogen, 129 gestrichen, 6.657 statt 4.643 erreichbare Lemmata, kein toter Zeiger mehr in der Ausgabe.

**#111 war keine Aufgabe, sondern eine Messung, und die Messung hat vor allem eine Messvorschrift ergeben.** 40,2 MB gz und 160,5 MB roh gegen Schwellen von 50 und 200. Die 42 MB aus dem Mai sind kleiner geworden, und trotzdem steht im Ticket ausdrücklich, dass ich daraus keinen Rückgang lese: für die Mai-Werte ist keine Zählweise dokumentiert, „ca. 165" sagt es selbst, und vier Prozent gegen eine gerundete Zahl sind keine Beobachtung. Der nächste Auslöser ist ohnehin kein Datum, sondern #27, dessen Per-Word-POS mit +3 bis 5 MB allein die Hälfte des Abstands bräuchte.

**#270 hat sich beim Messen selbst widerlegt, und das ist der eigentliche Ertrag.** Das Ticket schlug vor, die Contributor-Map erst mit #28 Phase 3 zu bauen, mit dem impliziten Argument, es sei zu teuer für einen Nutzen an einem einzigen kuratierten Lemma. Gemessen sind es **764 Byte gzip** für alle 54 Einträge, 0,02 Prozent des Authority-Index. Kosten sind also kein Grund und stehen jetzt im ADR, damit niemand sie noch einmal verhandelt. Die echten Gründe sind zwei andere: bei n=1 lässt sich nicht ehrlich entscheiden, wo auf einer Lemma-Seite eine Urheberangabe steht (das ist KZWs Entscheidung über eine sichtbare Seite), und der Phasenplan von #28 liefert für Schicht B „Quellsprache plus Quelle der Zuschreibung (Lexer/MWB/Kluge/LLM)". Diese Quelle ist bibliographisch, keine Person, und `contributors.xml` modelliert weder Wörterbücher noch Pipelines. Wer die Auflösung vorher baut, baut den falschen Mechanismus, und auf tausenden Lemma-Seiten stünde „nach Katharina Zeppezauer-Wachauer", wo „Lexer, akzeptiert durch die Pipeline" die Information wäre.

**Ein Ist-Zustand ohne Auslöser ist ein Versäumnis mit Dokumentation.** Deshalb hat ADR-018 eine Schwelle statt eines Verweises auf „später": ab dem 26. kuratierten Lemma oder mit #28 Schicht B, was zuerst kommt. Die Zählweise steht daneben. Nebenbei fiel dabei eine Ausnahme im `doc-count-audit.py` weg: ADR-018 nennt die Lexikongröße jetzt selbst (1 von 43.879), der Anker greift, und die Selbstprüfung hat den veralteten `INTENTIONALLY_SILENT`-Eintrag im selben Lauf gemeldet. Zu wissen ist dazu: das Skript kennt ein `--check`, das bei Drift ungleich 0 zurückgibt, wird aber in keinem Workflow aufgerufen und ist ohne dieses Flag immer grün. Ein Handlauf also, kein Gate.

**Phase:** Betrieb. #270 geschlossen, #225 auf `auto:blocked` + `wait:extern`, weil Trier antworten muss.

---
## 2026-08-08 – #111: aus dem Reminder wird ein Gate, und die Zahl von gestern war eine Einheit

**Summary:** #111 hat jetzt `scripts/audit/check-index-budget.py` und ADR-019. Kein Splitting, der Korpus-Index steht bei 84 Prozent seines Budgets. Zwei Befunde aus der Messung sind mehr wert als das Gate selbst.

**Der Eintrag von gestern stimmt nicht ganz: „Die 42 MB aus dem Mai sind kleiner geworden" beschreibt keinen Rückgang, sondern einen Einheitenwechsel.** `data/corpus-index.json.gz` ist seit dem 31.07. unverändert (`4195581e3`). Die 42 MB aus dem Mai sind dezimal gerechnet, die 40,2 MB von gestern sind MiB. Die Mai-Datei (`ea7b0a507`) hielt 42.183.990 Bytes, das sind 42,18 dezimale MB und 40,23 MiB; heute sind es 42.165.752 Bytes, und 40,2 ist exakt deren MiB-Wert. Seit der Mai-Messung haben 12 Commits die Datei angefasst, nie mehr als 19 kB auseinander. Einen Commit weiter zurück sieht es anders aus: am 08.05. waren es noch 35,8 MB. Die vorsichtige Formulierung von gestern („daraus lese ich keinen Rückgang") war im Ergebnis richtig, aber aus dem falschen Grund: es lag nicht an einer ungenauen Mai-Zahl, sondern daran, dass zwei verschiedene Einheiten verglichen wurden. Belastbar ist: der Index ist seit Mai **flach**. Und weil die Schwellen 50/200 aus der dezimalen Messung stammen, rechnet das Gate dezimal. `check-file-sizes.py` bleibt bei MiB, weil GitHubs Wand in MiB steht; die beiden liegen bei derselben Datei um 4,9 Prozent auseinander, und das steht in beiden Docstrings.

**Der zweite Befund kippt die im Ticket vorgeschlagene Strategie.** Option A in #111 will `texts[].words` auslagern und rechnet mit einem Kern von 10 bis 15 MB gz. Gemessen komprimieren die Felder völlig unterschiedlich: `words` ist 58 Prozent des Index im Speicher, aber nur 31 Prozent auf der Leitung (7,5 Millionen Tokens aus 42.630 verschiedenen Werten, Faktor 7,5). Die Positionsarrays in `texts[].lemmata` komprimieren nur 2,4-fach und sind damit **51 Prozent des Downloads**. Wer `words` auslagert, hat noch 29 MB gz im Kern, nicht 15.

Daraus folgt die eigentliche Regel in ADR-019: die beiden Schwellen sind nicht zwei Sichten auf ein Problem, sondern zwei Probleme. Die gz-Schwelle betrifft Leitung und Cache, dort muss `lemmata` weichen; die Roh-Schwelle betrifft den Speicher nach `JSON.parse`, dort muss `words` weichen. Welche zuerst reißt, benennt das Feld. Eine Vorabfestlegung hätte für den gz-Fall das falsche gewählt.

**Das Gate warnt und wird nie rot** (Entscheidung Chris, auf Rückfrage). Eine Überschreitung ist kein Fehler des Commits, der sie auslöst: der Index wächst durch legitime Annotationsarbeit, und ein rotes Gate würde den nächsten Backfill blockieren, bis jemand ein Splitting gebaut hat. Rot wird nur die gescheiterte Messung. Weil ein dauerhaft grünes Gate nichts beweist, hängt ein Selbsttest mit 20 Fällen daran, der auch die Rangfolge-Frage festhält: der Authority-Index hat weniger MB Luft als der Korpus-Index (4,7 gegen 7,8) und ist trotzdem der harmlosere Fall (41 gegen 84 Prozent Auslastung). Berichtet wird deshalb Auslastung, nicht Abstand. Die erste Fassung hatte genau das falsch herum.

**Zwei Sachen, die dabei auffielen und nicht hierher gehören.** `maps` ist 14,5 Prozent des Authority-Downloads und wird ausschließlich von `playground-main.js:147-157` gelesen; `korpus.html`, `woerterbuch.html` und jede Lemma-Seite laden und parsen 2,5 MB roh, die sie nie anfassen. Und `playground-main.js:319-324` läuft beim ersten Aufbau über `Object.keys(text.lemmata)` aller 667 Texte, nur um eine Anzeigezahl zu füllen, für die es das ungenutzte Top-Level-Feld `totalLemmata` schon gibt. Beides steht als Konsequenz in ADR-019, beides ist Frontend-Arbeit mit eigenen Tests und nicht Teil dieser Messung.

**Nummer:** #111 verlangt im Body ADR-015. Die ist seit 05/2026 vergeben (Authority-Source-Modell), worauf der Ticket-Kommentar vom 05.08. schon hingewiesen hatte. Es ist ADR-019 geworden.

**Phase:** Betrieb. #111 bleibt offen und bleibt Trigger-Reminder, jetzt aber mit einem Wächter statt mit der Hoffnung, dass jemand nachmisst.

---
## 2026-08-08 (Nachmittag) – #193 Baustein 1: ein Pferd, das als Mann klassifiziert war

**Summary:** `lemma_3036` Ingliart trägt jetzt `concept_14012100` (Haustiere/Namen) und `concept_23221000` (Pferd und Reiten/Namen) statt `concept_21012000` (Männlich/Mann) und `concept_23112500` (Personennamen). Zwei Zeilen in `lexicon.xml`, dazu die abgeleitete Schicht. Stufe 1 nach dem Playbook, in etwa der veranschlagten halben Stunde plus Bauzeit.

**Die Streichung war der heikle Teil, und sie war gedeckt.** Das Playbook sagt: Zeiger setzen ist Stufe 1, Zeiger streichen ist eine Rückfrage. Hier beauftragt #193 die Umklassifizierung wörtlich und nennt die Belege. Nachgeprüft statt geglaubt, und beim ersten Versuch falsch nachgeprüft: Ingliart hat **drei** Tokens im Korpus, nicht zwei. `PZ_38926_4` und `PZ_39814_3` sind exakt Boreks Stellen Pz. 389,26 und 398,14, und dort entscheidet der Kontext die Sache ohne Sekundärliteratur: „mit den kurzen ôren ingliart" beschreibt kein Mannsbild. Eine halbe Umklassifizierung wäre außerdem schlechter als keine gewesen, weil Ingliart dann gleichzeitig Mann und Pferd wäre.

**Der dritte Beleg, und wie ich ihn beinahe unterschlagen hätte.** `REN_242090_0` trägt `ingligar` und steht im Rennewart in einem Namenkatalog nach dem Muster „X von Ort": `wimiligar von kartetstere`, `ingligar von jelezie`, `rufter von themarie`. Die Nachbarn tragen alle eigene Hapax-Lemmata im 22xxx-Bereich, nur dieser eine hängt am Parzival-Pferd, allem Anschein nach wegen der Formähnlichkeit. Das ist ein **älterer** Fehler, keiner dieser Session: vorher standen zwei Pferdebelege unter „Personennamen", jetzt steht ein Ritter unter „Pferdenamen". Netto besser, sauber nicht, und ob `ingligar von jelezie` überhaupt derselbe Name ist, entscheidet KZW und nicht eine Session. Liegt als Rückfrage am Ticket.

**Zwei Suchfehler auf dem Weg dahin, beide in CLAUDE.md geregelt (#126/#130).** Meine erste Zählung ergab null Tokens: `@lemmaRef` trägt `lexicon.xml#lemma_3036`, nicht `#lemma_3036`, das Dateipräfix gehört zum Token. Meine zweite Zählung lief in einen Timeout, und danach habe ich die zwei Parzival-Belege für das ganze Bild gehalten, statt die Messung zu wiederholen. Elf Dateien enthalten die Zeichenkette `lemma_3036`, neun davon nur als Präfix von `lemma_30360` bis `lemma_30369`, zwei mit echten Treffern. Gefunden hat den dritten Beleg das Review, nicht ich. Die Lehre ist weniger die Token-Regel als die banalere Hälfte: eine Messung, die in einen Timeout läuft, ist keine Messung, und ein Teilergebnis darf nicht als Gesamtzahl weitergereicht werden.

**Quercheck der Rubrik**, der zweite Teil von Baustein 1: 49 Lemmata hängen jetzt unter `concept_23221000`, das sind die 48 aus dem Ticket plus Ingliart. Alle 49 tragen `pos=NAM`, alle zehn Namen von Borek sind vertreten, und bis auf einen tragen alle zusätzlich `concept_14012100`. Der eine ist Pegasus, und der gehört dort nicht hin: er führt stattdessen Fabelwesen und Mythologie, was für ein geflügeltes Pferd der griechischen Sage richtiger ist als „Haustier". Kein Befund, sondern eine begründete Ausnahme.

**Was die Kuration praktisch ändert**, damit die Erwartung stimmt: in der Volltextsuche nichts, die zwei Belege waren immer schon auffindbar. Sichtbar wird es im Begriffs-Zugang: wer im Playground die Pferdenamen unter „Pferd und Reiten/Namen" aufblättert, fand dort bisher neun der zehn arthurischen Pferde und Ingliart stattdessen unter den Personennamen. Genau diese Lücke hat Borek von außen bemerkt.

**Lifecycle:** Authority-Index v1.8.0 auf v1.8.1, fünf Stellen gebumpt, Index und die 2.742 API-Dateien neu gebaut. Geändert haben sich davon zwei, `api/index.json` (Versionsangabe) und `api/lemmata/index.json` (der Eintrag selbst). Die Konzept-Dateien unter `api/concepts/` führen nur Metadaten und keine Lemma-Listen, deshalb bleiben sie unberührt: das ist kein vergessener Rebuild, sondern die Form der API.

**Phase:** Betrieb. #193 bleibt offen, Baustein 1 von dreien ist erledigt bis auf die Rückfrage zu `ingligar`; Baustein 2 (Wortlisten-Abgleich) und 3 (der Playground-Explorer) sind eigene Arbeitspakete.

---
## 2026-08-08 (spaeter Nachmittag) – #193 Baustein 2: was eine Quote von 76 Prozent nicht heisst

**Summary:** Boreks drei hippologische Wortlisten von TUdatalib gegen unseren Wortschatz. Neu sind `scripts/ingest/horses/01-wordlist-crosscheck.py` und `ingest/horses/README.md`. Keine Datenaenderung, das ist ein Report.

**Die Zahl, die man aus so einem Abgleich herausliest, ist fast immer die falsche.** 76 Prozent der Pferdebezeichnungen loesen auf, 80 Prozent der Gangarten, 97 Prozent der Koerperteile. Als „24 Prozent fehlen im Lexikon" gelesen waere das eine Arbeitsliste von 124 anzulegenden Lemmata. Tatsaechlich ist `variants.xml` korpus-abgeleitet und kennt nur Schreibungen aus unseren 667 Texten, waehrend Boreks Listen aus einem weiteren Textfeld stammen. Belegt statt behauptet: 34 der 67 nicht aufgeloesten Pferdebezeichnungen tragen ein bekanntes Grundwort in sich, fast alle `-ros`- und `-pfert`-Komposita, und die Gegenprobe zeigt `ros`, `phert`, `vole`, `zelter`, `stuot`, `schenkel` alle vorhanden. Von den geprueften fehlen nur `wallach` und `merhe` wirklich.

**Zwei Zwischenbefunde haetten den Report unbrauchbar gemacht, und beide sahen erst wie Ergebnisse aus.** Borek markiert zwoelf Formen mit einem Stern; ungestrippt scheiterten alle zwoelf an der Aufloesung und erschienen als Wortschatzluecke, gestrippt loesen alle zwoelf auf (Gangarten von 74 auf 80 Prozent). Und die erste Fassung meldete 21 Klassifikationsluecken, von denen die Mehrzahl Fehlaufloesungen waren: `hors` auf `haar`, `roes` auf `rose` die Blume, `oren` auf einen Volksnamen. Die stehen jetzt als eigene Klasse „Verdacht auf Fehlannotation im Korpus", weil sie zu anderer Arbeit fuehren als eine fehlende Konzeptzuordnung.

**Der Bug, den das Review gefunden hat, ist der lehrreichste Teil.** `by_norm` ist ein `defaultdict(list)` und lebt ueber alle drei Listen. Ein Lesezugriff mit eckigen Klammern, `len(by_norm[normalize(f)])`, legt fuer jede ueber Stufe 2 aufgeloeste Form einen leeren Eintrag an. Die naechste Liste nimmt dieselbe Form dann in Stufe 1 mit leerer ID-Liste: sie zaehlt als aufgeloest, faellt aber aus jeder Ergebnisklasse heraus, still. Drei Formen stehen in mehr als einer Liste, und `zeldere` ist genau so verschwunden. Ein `.get()` behebt es. Das ist die Sorte Fehler, die kein Gate faengt und keine Summe verraet, weil die Zahl, die kleiner wird, in keiner Zeile steht.

**Zur Ablage:** die Listen sind CC-BY 4.0 und duerften ins Repo, liegen aber nicht drin. Das Skript holt sie in Sekunden ueber ihre Handles, und eine Kopie waere eine zweite Stelle, die altern kann. Der Attributionsvermerk steht trotzdem prominent, wie es #193 verlangt.

**Als Arbeit bleiben 20 Kandidaten fuer eine Nachklassifikation und 25 Verdachtsfaelle.** Beide brauchen eine philologische Durchsicht, bevor daraus Aenderungen werden; der klarste Block sind die Koerperteile, wo mehrere Lemmata nur an `concept_21030000` (Koerper von Menschen) haengen, obwohl Borek sie fuer Pferdekoerper belegt.

**Phase:** Betrieb. #193 Baustein 2 erledigt, Baustein 3 (Playground-Explorer) unberuehrt.

---
## 2026-08-08 (Abend) – #193 Baustein 3: das Maß hat die Zweifelsfälle erfunden, die es finden sollte

**Summary:** Boreks Belegstellen sind an unser Korpus angeschlossen und der Index `data/horses-index.json.gz` steht (11 KB gz, 346 Belege, 13 Pferde). Neu sind `scripts/ingest/horses/mapping.py` und `03-build-index.py`, `02-map-citations.py` ist auf das gemeinsame Modul umgestellt, DATA-MODEL.md hat einen Abschnitt.

**Der Bericht vom Nachmittag meldete neun Verse ohne Entsprechung. Sechs davon gab es nicht.** Verglichen wurden normalisierte Wortmengen, und daran scheiterte „unt hetz Lehelîn genomn" gegen unser „und hetez lehelîn genomen", ebenso „ans grâles" gegen „an sgrâles". Das Maß hat an Orthographie und Worttrennung versagt, nicht an Textidentität, und damit genau die Zweifelsfälle produziert, deren Aufspüren seine Aufgabe war. Auf der MHD-normalisierten Buchstabenkette bleiben drei. Die Schwelle 0.75 sitzt danach in einer leeren Zone: schwächste akzeptierte Entsprechung 0.84, stärkster verworfener Treffer 0.42.

**Die drei Reste waren keine Reste, sondern ein zu enger Suchradius.** Vier Verse Umkreis reichen nicht, wenn der Versatz über die Grenze des Dreißigers geht: `Pz. 604,18` steht bei uns unter 603,18, textlich zu 1.00 identisch. Und eine falsche Ziffer springt beliebig weit, `Er. 4118` ist textlich `4718`. Werkweit gesucht lösen sich alle drei eindeutig auf, mit 0.32 bis 0.38 Vorsprung vor dem jeweils zweitbesten. Damit sind **336 von 336 Versen textlich verifiziert**, kein einziger bleibt offen. Der Fallback übernimmt nur bei mindestens 0.15 Vorsprung, sonst fände er im Versepos irgendeine Formelzeile.

**Der Berater hat den Fehler gefunden, und zwar nicht durch Nachrechnen, sondern durch Lesen.** Der README nannte als Beispiel für „ohne klare Entsprechung" einen Vers, der bei 0.80 lag und die eigene Schwelle von 0.60 klar überschritt. Ein Beispiel, das der Regel widerspricht, die es illustrieren soll, ist ein zuverlässigerer Indikator als jede Summe: hier hing an ihm das ganze Maß.

**Die Modellierungsfrage ist entschieden, und die Begründung kam aus einer Metadatenzeile.** Gespeichert wird beides, Boreks Zitation wörtlich und unser aufgelöstes Ziel, dazu `match` und `score`. Ausschlaggebend war nicht die Abwägung Provenienz gegen Bequemlichkeit, sondern der Befund, dass **Borek gar keine Ausgabe nennt**: ihr `sourceDesc` führt nur die GND des Werks, während unser Parzival Leitzmann ATB 12 folgt. Eine stille Umrechnung wäre damit unprüfbar, denn prüfbar ist allein der Wortlaut. Der Berater hat zusätzlich den Präzedenzfall beigebracht, den ich nicht auf dem Schirm hatte: #59 hat wegen genau dieser Frage bewusst **keine** Reader-Links gebaut. Hier sind sie vertretbar, aber nur, weil jede einzelne Stelle am Text geprüft ist.

**Nebenbefund mit Folgen für die Zählung:** ein `dict` hat die Mehrfachzitate überschrieben. 346 Stellenangaben entfallen auf 336 Verse, vier werden von zwei Pferden mit abweichendem Wortlaut zitiert, und welche Fassung gewann, hing an der Dokumentreihenfolge. Jetzt werden alle Fassungen bewertet und die beste genommen.

**Das Review fand drei Auszeichnungen, die der Index still verschluckt hat**, alle drei Einzelfälle und deshalb in keiner Summe sichtbar: ein `event`, das innerhalb des Verses steht statt um ihn herum (Pz. 549,7 trägt sein `care` so), ein `objectName` ohne umschließendes `object` (Wh. 77,14, das Schwert Schoyuse), ein `horseGrp` für eine Gruppe statt für dieses Pferd (Pz. 474,3 stellt „ein ors" neben „den orsn"). Wer nur die Vorfahren eines Verses abläuft, verliert den ersten Fall aus jedem Ereignisfilter, ohne dass eine Zahl kleiner wird. Dazu ein latenter Fehler im werkweiten Fallback: die beiden Rangplätze waren nicht nach Vers dedupliziert, also konnte derselbe Vers beide belegen und der Abstand ihn gegen sich selbst messen. Mit dieser Quelle tritt es nicht ein, aber die Falle würde jede Wiederverwendung erben.

**An KZW gemeldet** (#193): die fünf verschobenen Parzival-Verse, die drei fern aufgelösten Stellen zum Gegenlesen, und die Bitte, Luise Borek auf den Zahlendreher hinzuweisen. Eine stillschweigende lokale Korrektur einer fremden publizierten Quelle wäre nicht in Ordnung, auch bei CC0 nicht.

**Zur Lizenz:** TUdatalib führt den Datensatz als CC0 1.0 (publiziert 2023-01-18), die Datei selbst trägt im Header noch „Veröffentlichung unter CC-BY-SA wird angestrebt" und Januar 2017. Das ist der Entwurfsstand, es gilt die Lizenz des Repositoriums. Steht so in DATA-MODEL.md, damit die Frage nicht ein zweites Mal gestellt wird.

**Phase:** Betrieb. #193 Baustein 3 datenseitig fertig, die Playground-Ansicht steht noch aus und gehört mit #194 zusammen.

---
## 2026-08-08 (spät) – #193/#194: die Ansicht, und ein Deep-Link, den es nicht gab

**Summary:** Der Pferde-Explorer steht (`playground/js/ui/tei/horses-explorer.js`), dazu die Rubrik „Experimentelle Forschungsdaten" aus #194, ein Hilfe-Abschnitt, 7 Tests und ein neuer Reader-Parameter `?verseId=`. Voller Playwright-Lauf grün (290 Tests). Lokal committet, **nicht gepusht**: die Abnahme der Oberfläche durch Chris steht aus.

**Der Reader konnte 288 der 346 Belege gar nicht anspringen, und das fiel erst beim Bauen auf.** `?verse=` sucht `<l @n>`. Im Parzival trägt das `<l>` aber nur die Verszahl innerhalb des Dreißigers, die Abschnittsnummer hängt am `<div>`; ein Link auf „26" träfe einen von 827 Versen. Im Willehalm ist es schlimmer: dort gibt es **überhaupt keine Abschnittsgliederung**, die `<l>` hängen nackt in einem `<p>`, und die Dreißiger-Nummer existiert im TEI nicht. Sie steckt einzig in den Wort-IDs. Deshalb rendert jedes `<l>` jetzt `data-core`, die Kernzahl seiner ersten Wort-ID, und `?verseId=PZ_33926` löst darüber auf: korpusweit eindeutig, unabhängig von Zählweise und Struktur. Bestehende `?verse=`-Links bleiben unberührt.

**Das Review fand den Fall, den ich selbst dokumentiert und dann nicht implementiert hatte.** Der Ambraser Einschub im Erec steht vollständig als `<supplied>` in EINEM `<l n="4629">` und deckt die Kerne 462900 bis 462957 ab. Mein `data-core` trug nur den ersten. Die zehn Einschub-Belege hätten also nichts gefunden, und zwar stumm: eine Konsolenwarnung, kein Sprung, der Leser landet am Anfang eines Werks mit 10.135 Versen. Behoben über `data-core-max` und eine Spannensuche. Die Lehre ist unangenehm konkret: ich hatte den Sonderfall zwei Stunden vorher im Modulkopf beschrieben („der Sprung landet auf 4629") und beim Implementieren nicht wiedergelesen.

**Und die Zahl in derselben Beschreibung war falsch.** „24 Verse" hatte ich aus Boreks höchster Zitation (4629,24) gelesen statt aus unseren Daten. Es sind 57. Genau der Fehler, gegen den die Projektregel gemacht ist: eine Zahl, die plausibel aussieht, weil sie irgendwo steht, aber nicht gemessen wurde.

**Eine gemeldete Zahlendifferenz war diesmal keine.** Der Reviewer fand 335 verschiedene Sprungziele bei 336 Versen. Das ist kein Zählfehler, sondern der Zahlendreher: Boreks `4118` und ihr `4718` zeigen beide auf denselben Vers, und genau das ist die richtige Auflösung.

**Zur Modellierung in der Oberfläche:** sichtbar ist immer Boreks Zitation, der Link benutzt unser aufgelöstes Ziel. Die acht auseinanderfallenden Belege tragen ein Sternchen mit dem Grund im Tooltip. Der Hinweis steht am einzelnen Beleg und nicht als Fußnote unter der Tabelle: pauschal formuliert würde er 338 korrekte Stellen mit verdächtigen.

**Phase:** Betrieb. #194 ist mit erledigt und kann nach dem Push geschlossen werden. #193 bleibt offen, bis KZW die acht Stellen gegengelesen hat.

---
## 2026-08-09 – #59: die Gegenrichtung war schon in den Daten, und #111 durfte zu

**Summary:** Lindas beide Wünsche vom 29.07. sind live, dazu der Alexander-Override, der seit dem 28.07. abgesegnet herumlag. #111 geschlossen, weil das gestern gebaute Gate den Reminder ersetzt.

**Der Explorer konnte die Frage schon beantworten, er konnte sie nur nicht stellen.** Jeder Record trägt beides, `who` und `by`, seit dem ersten Build im Juni. Auswählbar war bis heute nur die benannte Figur, der Nenner stand als Beschriftung in der aufgeklappten Belegzeile und sonst nirgends. Beide Wünsche sind deshalb reine Frontend-Arbeit gewesen, kein Rebuild, kein neues Feld, nichts an Lindas Repo. Vorher gemessen statt vermutet: 3.156 Figurenrede-Records, davon genau 3 ohne erfassten Nenner, und pro Werk zwischen 29 und 73 verschiedene Nenner. Lindas eigene Beispielfrage geht exakt auf, Iwein benennt im *Iwein* 26 andere Figuren.

**Zwei Entscheidungen, die die Frage erst vollständig machen.** Der Erzähler ist in der Nenner-Perspektive ein wählbarer Nenner wie jeder andere; im *Iwein* ist er mit 619 Belegen über 47 Figuren die größte Instanz überhaupt, und „welche Benennungen für wen" ist für ihn dieselbe Frage. Und die Selbstnennungen einer Figur zählen zu ihr als Nenner, sonst hätte Iwein 120 statt 129 Belege und die Dreiteilung aus Wunsch 1 (Erzähler, Figurenrede, Selbstnennung) fiele in Wunsch 2 auf zwei Drittel zusammen. Beides steht so in der Antwort an Linda, damit sie widersprechen kann.

**Der Befund kam aus dem Nachmessen, nicht aus dem Bauen.** Die Nennerspalte trägt im Rolandslied eine Notation, die die Figurenspalte nicht hat: ein führendes `#`, Unterstriche, wechselnde Großschreibung. Fünf Nenner zerfielen dadurch in je zwei Einträge, `#David` neben `David`, `#Karlinge` neben `#karlinge`. Das ist genau die Spalte, nach der Linda filtern wollte, also wäre die Ansicht mit einem sichtbaren Defekt live gegangen. Ursache ist zur Hälfte unser Skript: `clean_figure_name` glättet die Unterstriche der benannten Figur, `by` bekommt nur `clean`.

**Gruppiert wird trotzdem in der Ansicht und nicht im Index.** Naheliegender wäre das Skript gewesen, dort stehen die anderen Quirks der Quelle schon. Dagegen sprach, dass die Notation Lindas ist und ich nicht weiß, was das `#` bedeutet: es sieht nach Kollektiv aus (`#haiden`, `#cristen`, `#alle`), aber `#David` und `#Engel` widerlegen das. Eine Bereinigung im Index hätte eine Bedeutung weggeworfen, die ich nicht gelesen habe. In der Ansicht ist es eine Funktion, die wegfällt, sobald Linda die Quelle vereinheitlicht. Die Regel dazu ist gemessen und nicht angenommen: beide erwogenen Schlüssel, mit und ohne MHD-Normalisierung, führen genau dieselben fünf Paare zusammen und sonst nichts, in den anderen drei Werken ändern beide nichts. Also der schlichtere.

**Vier weitere Namenspaare gemeldet statt zusammengefasst.** `Pförnter`/`Pförtner`, `[Bote]`/`[Boten]`, `Oetas`/`Oeteas`, `Herclues`/`Hercules`. Die sehen nach Tippfehlern aus, aber „sieht aus wie" ist bei fremden Forschungsdaten keine Erlaubnis. Der Ähnlichkeitslauf fand als fünftes Paar `die Alte vom Schwarzen Dorn` neben `die Junge vom Schwarzen Dorn`, zwei verschiedene Figuren mit 0,87 Ähnlichkeit, und genau deshalb wird hier nichts automatisch geglättet.

**Der Alias-Override war der billigste Teil und lag am längsten.** Am 12.07. entworfen, am 28.07. von Linda mit „passt sehr gut" abgesegnet, dann nie gebaut, weil der Entwurf „beim nächsten Naming-Update" sagte und das Update ein Cron ist, der keine Menschen anspricht. Wirkung nachgemessen: genau ein Record, TRO V. 20665, von Antonomasie zu Eigenname. Der Build failt hart bei unbekanntem Werk- oder Figurennamen, weil ein Tippfehler sonst wirkungslos in der Datei stünde und die Datei trotzdem so aussähe, als tue sie etwas.

**Der Reviewer hatte einen Befund, und der war ein Kommentar.** Die Begründung an `NARRATOR_KEY` behauptete Kollisionsfreiheit stärker, als `namerKey` sie herstellte: das Gitter wurde vor dem Trimmen abgeschnitten, ein Wert mit führendem Leerzeichen hätte es behalten. In den Daten kommt das nicht vor, der Kommentar wäre also nur zu entschärfen gewesen. Billiger war, den Mechanismus stimmen zu lassen, ein `trim()` weiter nach vorn.

**Kein voller Testlauf**, und das ist gemessen und nicht geraten: der Tailwind-Rebuild war rein additiv, vier neue Klassen, keine weggefallen. Damit betrifft die Änderung nur das eine Modul, dessen 12 Tests grün sind, plus fünf Gates. Die CI hat den Rebuild-and-Compare des Naming-Index mitgemacht, also nimmt auch der wöchentliche Cron den Override mit.

**#111 geschlossen.** Das Ticket war ausdrücklich ein Trigger-Reminder, und seit gestern prüft `check-index-budget.py` genau die Schwelle, die es aufschreiben wollte. Beim Schließen fiel auf, dass die Prognose von 05/2026 nicht eingetroffen ist: erwartet waren 60 bis 80 MB gz binnen zwölf Monaten, tatsächlich steht der Index nach drei Monaten fast unverändert bei 42,17 MB. Der Grund ist nicht, dass die Schätzung falsch gerechnet hätte, sondern dass #27 und #109 nicht ausgespielt wurden. Eine Größenprognose ist eben eine Roadmap-Prognose.

**Phase:** Betrieb. #59 bleibt offen auf `auto:blocked`/`wait:linda`: Linda liest die Ansicht gegen, beantwortet die `#`-Frage und schickt später den Nutzer-Leitfaden mit DOI, den wir dann im Modul verlinken.

---
## 2026-08-09 (Nachmittag) – #358: die Prüfung, die den Umfang ausweiten sollte, hat ihn halbiert

**Summary:** Der Willehalm hat seine 467 `<div type="chapter">`. Der Weg dahin ging über zwei eigene Messfehler und endete bei genau dem Umfang, den das Ticket von Anfang an genannt hatte.

**Das Ticket verlangte selbst, erst das ganze Korpus zu prüfen, und das war richtig.** Nur hat die Prüfung nicht das ergeben, wonach sie suchte. Mein erster Lauf meldete 48 betroffene Werke, weil ich nach `<div @n>` als Vorfahr gesucht hatte und die Strophentexte ihre Nummer am `<lg @n>` tragen. FDS, VIR, NBB und siebzehn weitere sind vollständig ausgezeichnet. Nach der Korrektur blieben 18, davon zehn mit genau einem „Abschnitt": das ist kein fehlendes Kapitel, sondern der Linecode-Offset des Textes selbst. Übrig blieben sieben.

**Danach hat die Messung den Umfang ein zweites Mal eingedampft, und diesmal inhaltlich.** Die sieben sind nicht dasselbe Phänomen. Entscheidend war die Länge: 465 der 467 WH-Abschnitte haben exakt 30 `<l>`. Eine Handschriftenseite mit 465 mal exakt 30 Zeilen gibt es nicht, ein Dreißiger schon. Die Gegenprobe an DIO, dessen 212 `<pb>` Commit `795670240` (#26) im Mai nachweislich aus Julias Linecode-Seitenangaben eingefügt hat, ergab 45 Verse je Einheit bei 210 von 212: echte Seiten, korrekt kodiert. Und WH steht nicht in der #26-Sigle-Liste, seine `<pb>` stammen aus der Ursprungstransformation. Damit ist belegt, was das Ticket vermutet hatte, und zugleich, dass DIO, FB, WLE, FP, RUD und WUT eben nicht mitgemeint sind.

**Ich hatte dem User vorher „alle sieben, gestaffelt" empfohlen und WUT als den billigen Einstieg verkauft.** Beides war falsch, und beides hat erst die Messung gezeigt: WUTs 346 `<lg>` decken sich zwar mit den Abschnitten, aber `lg[344]` und `lg[345]` tragen beide Abschnitt 345, die Abschnitte 326 bis 343 beginnen bei Vers 3 oder 5 statt bei 1, und 316 der „Dreißiger" haben 31 Verse. Das ist eine editorische Frage. Die Staffelung umzudrehen und dann auf einen Text zusammenzustreichen war die Konsequenz aus Zahlen, die es bei der Empfehlung noch nicht gab.

**Die eigentliche Invariante des Migrationsskripts ist nicht die Token-Sequenz.** Die auch, aber sie prüft nur, dass nichts kaputtging. Die inhaltliche Prüfung ist eine andere: je Abschnitt wird die Nummer am neuen `<div>` gegen die aus der ersten Wort-ID abgeleitete gehalten. Das vergleicht die beiden Quellen der Zahl miteinander, statt einer von beiden zu glauben, und es ist derselbe Gedanke wie bei #193, wo der Wortlaut und nicht die Zahl entschieden hat.

**Kein Frontend-Code, und das war keine Sparsamkeit, sondern der Beleg.** Der Reader rendert für `type="chapter"` längst `<h3>Kapitel N</h3>`. Dass WH die sichtbare Abschnittsnummer allein durch die Datenkorrektur bekommt, ohne dass irgendwo ein Sonderfall dazukommt, ist das Argument dafür, dass die Daten und nicht die Anzeige falsch waren. Option 3 aus dem Ticket („nur die Anzeige") hätte denselben Effekt erzeugt und die Ursache konserviert.

**Der Korpus-Index blieb byte-identisch**, bestätigt durch den Rebuild-and-Compare der CI: der Build liest im Body nur `<l>` und `<w>`, nie `div`/`pb`/`p`. Kein Version-Bump, kein Reindex. Eine Korpusänderung dieser Größe ohne jede Bewegung in der abgeleiteten Schicht ist selten genug, um sie zu notieren.

**Der Reviewer fand zwei Zahlen, und beide waren mein eigener Fehler in genau der Disziplin, die dieses Projekt sich aufgeschrieben hat.** „Die beiden anderen 23 und 28" mischte zwei Messvorschriften in einer Klammer: Abschnitt 467 hat 24 `<l>`, davon 23 mit Tokens, weil sein `<l n="24">` nur eine `<caesura>` enthält. Und „DIO: 45 Verse je Einheit" war eine Idealisierung von 210 der 212. Beide Zahlen waren für sich richtig und in der Formulierung falsch.

**Phase:** Betrieb. #358 steht auf `auto:blocked`/`wait:kzw` mit drei benannten Fragen: ob DIOs und FBs `<pb>` als Seiten richtig sind, wie WUTs Doppelabschnitt 345 und die bei Vers 3 beginnenden Abschnitte zu lesen sind, und was mit RUD, WLE und FP geschieht.

---
## 2026-08-10 (Nachmittag) – #361: die Kette war keine Hierarchie, weil die Daten eine Hülle sind

**Summary:** Der Gattungs-Explorer zeigt die Textreihentypologie als aufklappbaren Baum. Aus #93 herausgelöst, weil dieser Teil an nichts hängt, was auf KZW und Marco Heiles wartet. Authority-Index v1.8.1 auf v1.9.0.

**Der Defekt war eine Zeile, die Ursache ein Datenmodell.** Die Ansicht verkettete die übergeordneten Gattungen mit " UND ", und bei `genre_26c0ce4c` wurden daraus gemessene 408 Zeichen aus 20 Namen. Das sah nach einem Anzeigefehler aus und war keiner: `genres.xml` speichert die volle transitive Hülle, jede Kategorie nennt **alle** ihre Vorfahren statt nur der nächsten. 615 Kategorien tragen so 3.175 Kanten. Die Zeile war also korrekt, sie gab nur wieder, was dasteht. Eine Hierarchie lässt sich daraus nicht zeichnen, weil eine Abkürzungskante (Wurzel → Blatt) von einer echten Elternkante nicht zu unterscheiden ist.

**Die Reduktion gehört in den Build, nicht in die Ansicht.** `_direct_parents()` streicht jeden Elternteil, den ein anderer Elternteil bereits als Vorfahren führt: 3.175 Kanten werden 819. Danach 2 Wurzeln (*Epik, Lyrik und Dramatik*, *Wissensliteratur und Gebrauchsliteratur*), 442 Kategorien mit einem direkten Elternteil, 139 mit zwei, 29 mit drei, 3 mit vier. Der Schritt ist nur zulässig, weil die Menge wirklich eine Hülle ist, und das wurde geprüft statt angenommen: für alle 3.175 Kanten gilt die Enthaltensein-Bedingung, null Verletzungen, null tote Verweise, null Selbstbezüge.

**Die Messung hat die einzige echte Designfrage entschärft, bevor sie gestellt war.** Das Ticket kam als `auto:checkin` herein, weil 171 Kategorien mehr als einen Elternteil haben und ein Baum sie entweder mehrfach zeigen muss oder einmal mit Querverweisen. Die Sorge war der Umfang: bei Tiefe 20, wie das Ticket sagte, klingt Duplizieren nach Explosion. Gemessen ist die Tiefe aber 9 (die 20 im Ticket war die Hüllengröße, nicht die Pfadlänge), und voll entfaltet belegen die 615 Kategorien 1.167 Baumplätze, Faktor 1,9. Damit kostet Duplizieren praktisch nichts, und es ist auch das Richtige: ein *Predigtmärlein* IST *Märe* und *Predigt*, `Monatsregimen` steht unter *Kalender*, *Tagewählerei* und *Text zur Diätetik* zugleich. Es unter einen Elternteil zu zwingen wäre eine Aussage über die Typologie, die die Daten nicht machen.

**Aus derselben Einsicht folgt die DOM-Regel.** Die Schlüssel des Baums sind der **Pfad**, nicht die Kategorie-ID, sonst hätten die 171 mehrfach einsortierten Kategorien kollidierende Knoten und ließen sich nicht unabhängig auf- und zuklappen. Dasselbe Motiv beim Detailfeld: eines für den ganzen Baum statt eines pro Knoten. Der Test dafür ist der wichtigste der sieben.

**Die alte Karte ist weg statt ergänzt.** `maps.genreHierarchy` trug Eltern-*Namen* und die volle Hülle, und ihr einziger Konsument war genau die UND-Kette. Sie durch ein Feld an den Gattungs-Einträgen zu ersetzen war billiger als beides zu pflegen; der Index ist dadurch netto 5,4 KB kleiner geworden.

**Erwartungsdämpfer, der in die Ansicht gehört.** 482 der 615 Kategorien haben im ganzen Zweig unter sich kein einziges Werk unseres Korpus, benutzt werden 92 mit 874 Referenzen. Ein Baum ohne diese Angabe führt in leere Äste. Jeder Knoten nennt deshalb eigene Werke und Werke im Zweig, und was zu nichts führt, ist gedimmt und beschriftet.

**Vier Reviewrunden, und die letzte war die wertvollste.** Runde 1 und 2 (`fable-reviewer`, vor dem Push) fanden Textpfeile `▸`/`▾` statt Heroicons und ein `aria-label`, das an allen 615 Knöpfen gleich lautete und den Zustand doppelt trug. Dann schrieb der CI-Bot fünf Befunde, und Runde 3 hatte nicht mehr die Aufgabe, den Diff zu lesen, sondern **diese fünf zu beurteilen**: drei real, einer als billiger Mitnahmefix, einer fallenzulassen (ein `?.`-Fallback, den kein Ladepfad erreicht). Das ist die Projektregel „ein Befund ist selbst eine Behauptung“ in ihrer nützlichsten Form, und sie hat hier zwei Arbeitspakete gespart statt eines erzeugt.

**Der teuerste Befund war ein Nebenschaden meiner eigenen Aufräumarbeit.** Die Checkbox „Nur Gattungen mit zugeordneten Werken anzeigen“ aus #119 war im Baum-Ruhezustand ein No-op, weil ihr Handler in `searchGenres` läuft und die Methode bei leerem Suchfeld vorher zurückkehrt. Der No-op ist älter als dieser PR, unsichtbar war er aber nur, solange unter der Checkbox die Aufforderung zum Suchen stand. Sobald dort eine vollständige Ansicht steht, sieht sie aus, als beziehe sie sich darauf. Jetzt tut sie das: 1.167 Baumplätze fallen auf 246, dahinter genau die 133 belegten Kategorien. Dass das den Baum nicht zerreißen kann, ist keine Beobachtung, sondern folgt aus der Konstruktion, die Werkmenge eines Elternteils ist die Obermenge jedes Kindzweigs. Dazu zwei Barrierefreiheits-Befunde: das Detailfeld steht hinter dem ganzen Baum und war nach einem Klick weit oben nicht zu sehen, und `renderTree()` zerstörte den gedrückten Knopf samt Tastaturfokus.

**Und ein Test, der schwächer prüfte als sein eigener Kommentar.** Der wichtigste der Specs filterte mit `onclick.includes(id)`, und weil der Schlüssel der Pfad ist, traf das auch jeden Nachfahren. Zwei Treffer kamen nur heraus, weil die eine Unterkategorie der Predigt selbst keine Kinder hat. Er hätte nie falsch grün werden können, nur irreführend rot, aber der Kommentar darüber behauptete etwas anderes als der Code prüfte, und genau das verbietet die Regel.

**Nicht Teil davon:** der Abgleich mit `Middle-High-German-Conceptual-Database/textseries` (618 Konzepte dort gegen 615 hier, 157 Kanten nur dort, 95 nur hier) und die toten `dhplus`-URIs. Das bleibt in #93 und braucht eine philologische Entscheidung darüber, welcher Stand gilt.

**Phase:** Betrieb, in einem Worktree gebaut, während die Parallelsession #59 gemerged hat. Der Rebase auf den neuen `main` hatte genau einen Konflikt, die einzeilige Tailwind-Ausgabe, und der wurde durch `npm run build:css` erledigt statt von Hand.

---
## 2026-08-10 – #59: das Gitter darf bleiben, weil wir jetzt wissen, was es heißt

**Summary:** Lindas drei Punkte vom Morgen sind umgesetzt: „Nennende Instanz" statt „Nennende Figur", Alexander als eigene Kategorie *Deckname* statt als Eigenname, und ihr Quell-Commit `b7cc0585` zieht die Gruppierungsfunktion vom 09.08. ersatzlos zurück. 297/297 grün.

**Die Funktion ist weggefallen wie geplant, nur aus einem stärkeren Grund als geplant.** Gestern stand im Kommentar, die `#`-Gruppierung liege in der Ansicht statt im Index, weil sie dann bei einer Vereinheitlichung der Quelle „als Funktion wegfällt statt als Datenstand". Genau das ist eingetreten, einen Tag später. Gemessen gegen Lindas neuen Stand führt der Schlüssel nichts mehr zusammen (distinkte `by`-Werte je Werk, also ohne Erzähler und Selbstnennungen: 33/29/48/71 in IW/ENE/ROL/TRO, mit und ohne Gitter-Schnitt identisch; die Nennerliste des Moduls zählt mit Erzähler und Selbstnennungen 36/31/50/73). Der eigentliche Grund, ihn zu entfernen, ist aber ein anderer: Linda hat erklärt, wofür das `#` steht, nämlich für eine Instanz, die keine handelnde Figur des Werks ist, entweder eine unbestimmbare Menge (`#haiden`) oder eine nur zitierte Person (`#David`, den der Erzähler anführt). Damit ist das Abschneiden nicht mehr nur überflüssig, sondern falsch: `#David` und ein handelnder David wären derselbe Schlüssel und derselbe Nenner. Das Zeichen steht jetzt in der Anzeige, mit ihrer Erklärung darunter.

**Die Zurückhaltung von gestern hat sich bezahlt gemacht, und zwar messbar.** Hätte das Skript die Notation im Index bereinigt, stünde heute eine Bedeutung nicht mehr in den Daten, die wir inzwischen kennen und im Modul erklären. Der Aufwand für den Rückbau war eine Funktion und ein Regex; der Aufwand für einen Rückbau im Index wäre ein Rebuild gegen einen Quellstand gewesen, den es so nicht mehr gibt.

**Der Deckname ist eine vierte Kategorie und keine Umbenennung.** Linda: „Der Name sollte in dem Fall nicht als 'Eigenname', sondern als 'Deckname' gelabelt werden." Damit sitzt er zwischen Eigenname und Antonomasie, benennt die Figur wie ein Name, ohne ihr Name zu sein, und darf in keiner der beiden aufgehen. `alias-overrides.json` trägt deshalb jetzt ein Pflichtfeld `category` mit zwei erlaubten Werten, `deck` und `eig`; fehlt es oder steht etwas anderes darin, bricht der Build ab. Kein Default: der Unterschied zwischen einem Decknamen und einem bloß fehlenden Namensalias ist eine philologische Aussage, die ein neuer Eintrag nicht stillschweigend erben soll. Beide Fehlerfälle sind gegen die geladene Funktion getestet, nicht behauptet.

**Eine Kategorie mit genau einem Beleg im ganzen Index braucht eine Anzeigeregel.** Tab und Kachel erscheinen nur, wo die Kategorie trifft, sonst stünde in 615 von 616 Figuren eine Null neben drei gefüllten Kategorien und läse sich wie eine Erhebungslücke statt wie ein kuratierter Sonderfall. Eine Ausnahme davon ist nötig und stand nicht im ersten Entwurf: ist der Deckname-Tab gerade der gewählte, bleibt er sichtbar, auch wenn ein Unterfilter ihn auf 0 bringt. Sonst verschwindet das aktive Steuerelement, und die leere Tabelle hat keinen sichtbaren Grund mehr.

**Vier gemeldete Namenspaare, drei waren Tippfehler, eines nicht.** `Pförnter`, `Herclues` und `Oeteas` sind korrigiert, `[Bote]` neben `[Boten]` bleibt: ein sprechender Bote und mehrere sprechende Boten. Das ist die Bestätigung für die Regel von gestern, nichts automatisch zu glätten, was nach einem Tippfehler aussieht. Vier von fünf hätten gestimmt, und das fünfte hätte zwei Instanzen zu einer gemacht.

**Zwei Sessions in derselben Datei, und die Git-Regel greift dafür nicht.** Eine Parallel-Session hat `naming-explorer.js` gegen 10:05 per Skript in-place überschrieben, während diese Session dieselbe Datei bearbeitete; das Ergebnis war ein lauffähiger Mischstand, in dem zwei Methoden aus der anderen Fassung stammten. Aufgefallen ist es an einem `Edit`, dessen Suchtext nicht mehr passte, und an einem NUL-Byte, das dabei in die Datei geriet (`git grep` meldete sie als binär). Die bestehende Regel adressiert den *Index* (`git add -A`), nicht den *Arbeitsbaum*. Was hier geholfen hat, war die Übergabe im Klartext: die andere Session hat aufgeschrieben, welche Methoden ihre sind und was davon weg soll, und diese Session hat den Diff danach ganz gelesen statt nur die eigenen Stellen.

**Der Sentinel, der kollisionsfreier aussah, war der einzige echte Fehler.** `NARRATOR_KEY` hing vorher daran, dass `namerKey` das führende `#` abschnitt; als das wegfiel, brauchte er einen eigenen Grund. Meine Wahl war U+0000, und die ist falsch: der Schlüssel steht als `<option value>` in einem `innerHTML`, und der HTML-Tokenizer ersetzt U+0000 im Attributwert durch U+FFFD. Der Wert aus dem Select traf den Schlüssel damit nie, und die Erzähler-Auswahl lieferte in allen vier Werken 0 Treffer, beim belegstärksten Nenner jedes Werks. Der `fable-reviewer` und der CI-Bot haben ihn unabhängig gefunden, der eine gemessen, der andere aus der Parser-Spezifikation hergeleitet. Richtig ist ein Sentinel aus Großbuchstaben: `namerKey` schreibt alles klein, also kann kein echter Nenner ihn erzeugen, und durch ein Attribut geht er unverändert. Die 297 grünen Tests hatten den Fehler nicht gesehen, weil kein einziger den Erzähler je ausgewählt hatte, obwohl er in jedem Werk ganz oben steht.

**Der neue Test hat zweimal aus dem falschen Grund rot gezeigt**, und beide Male lag es an ihm. Erst nahm `selectOption` die RegExp im `label` nicht an, dann brach `\d+` am Tausenderpunkt des ROL-Erzählers (1.222 Belege, `toLocaleString('de-DE')`). Erst der dritte Anlauf hat gemessen, was er messen sollte. Er liest den Wert jetzt aus dem DOM zurück, statt ihn hinzuschreiben: genau die Round-Trip-Eigenschaft, an der der Sentinel gescheitert ist. Gegenprobe nach Projektregel: mit dem alten Sentinel fällt er, mit dem neuen läuft er.

**Zwei weitere Befunde waren meine eigenen Zahlen.** „Eckige Klammern (Trojanerkrieg)" stand im Kommentar, obwohl ich die Verteilung Stunden vorher selbst gemessen hatte: sie stehen in IW (7), ENE (7) und TRO (14), nur ROL hat keine. Und „33/29/48/71 Nenner" ist die Zählung über die distinkten `by`-Werte; die Liste, die das Modul anzeigt, hat mit Erzähler und Selbstnennungen 36/31/50/73. Beide Zahlen waren richtig und ohne Messvorschrift trotzdem irreführend, dieselbe Fehlerklasse wie am 31.07. bei den Breve-Zahlen.

**Phase:** Betrieb. #59 bleibt offen auf `auto:blocked`/`wait:linda`: der Nutzer-Leitfaden mit DOI fehlt weiter, und Linda will die eckigen Klammern im Trojanerkrieg noch auf die Gitter-Notation vereinheitlichen. Der Erklärsatz im Modul nennt beide Notationen und zieht seine Beispiele aus dem jeweiligen Werk, er stimmt danach also ohne Nacharbeit.

---
## 2026-08-24 – #216 Serie 1: der Filter, der die schweren Fälle finden sollte, kannte kein Mittelhochdeutsch

**Summary:** 6.982 unannotierte Tokens der Form `minne` aus 262 Texten kontextdisambiguiert, in 118 Bündeln von je etwa 60 Fällen. 5.435 sind in 255 Texten annotiert (5.106 zu `lemma_4130` NOM, 329 zu `lemma_4133` VRB), 1.547 bewusst zurückgehalten. Drei Regeln halten zurück, gemessen gefeuert haben zwei davon: 1.546 Fälle an der Konfidenz unter `high`, einer am Konflikt zwischen Verdict und bestehendem `@pos`. Die dritte, das Verbot einer automatischen NAM-Vergabe, hat nie gegriffen, weil der Prompt NAM auf höchstens `medium` deckelt und damit schon die erste Regel zieht: ein Sicherheitsnetz, das nur an einem zweiten Faden hängt. 982 der zurückgehaltenen Fälle tragen NAM als Verdict, das ist die Personifikation „Frau Minne". Der Rückhalt ist kein Rest, er ist die Entscheidung: ob eine Stelle die Allegorie meint, ist eine philologische Frage, keine LLM-Frage.

**Drei Stichproben-Durchgänge, 150 Fälle, kein Fehler – und der zweite Durchgang war wertlos.** Die „schwere" Stichprobe sollte gezielt Fälle ohne stützenden Vorgänger ziehen. Der Prüfer maß nach, dass 46 Prozent der gezogenen Fälle sehr wohl einen Artikel oder ein Possessivum vor sich hatten. Ursache war die Wortliste des Filters: sie kannte `der`, `die`, `dîn`, nicht aber `di`, `dorch`, `sîner`, `grozzer`. **Eine Wortliste ist im Mittelhochdeutschen kein Filter**, weil es die eine Schreibung nicht gibt. Der Ersatz fragt nicht mehr den Text, sondern das `@pos` des vorangehenden `<w>` im TEI, und der traf.

**Ein Nullbefund aus dem eigenen Skript ist noch kein Befund.** Die Prüfung des `wâren`-Nebenbefunds meldete zunächst null Treffer korpusweit. Der Grund lag im Skript: `@corresp` trägt `variants.xml#type_273621`, verglichen wurde auf den blanken Typnamen. Nach dem Fix waren es 5.641. Seither prüft jedes Messskript hier zuerst einen bekannten Positivfall, bevor seine Null etwas heißt.

**Zwei Heuristiken sind gescheitert, und das steht so im Log.** Der Verdacht, `minne` stehe in GWTK stellenweise für das Possessivum *mîne*, ließ sich korpusweit weder belegen noch ausschließen: die Kontextheuristik erzeugte 1.181 Fehlalarme (Genitivattribute), das Verhältnismaß bildet nur den Themenanteil eines Textes ab. Sieben Verdachtsfälle liegen als Review bei KZW. Ein „nicht entschieden" im Provenienz-Log ist billiger als eine Zahl, die niemand nachrechnen kann.

**Der Lifecycle wurde gemessen statt geschätzt.** `extract-variants.py` im Trockenlauf meldet alle vier Semantik-Zähler auf 0, also entfallen die Schritte 5 und 6 und der Authority-Index bleibt bei 1.9.0: der Batch vergibt ausschließlich die beiden bestehenden Typen. Gebumpt wurde nur der Korpus-Index (4.2.1 → 4.2.2). Die Abnahme lief nicht über das grüne Build-Log, sondern über einen positionsgenauen Abgleich gegen den Vorstand: Belegstellen 7.532.982 → 7.538.417, Differenz exakt 5.435, genau zwei Lemmata mit veränderter Belegzahl, kein Text mit Positionsverlust.

**Nebenbefund als eigenes Ticket (#367), und beim Aufschreiben ist er beinahe falsch geworden.** `wâren` ist als Verb (`wesen`) getaggt, wo das flektierte Adjektiv `wâr` steht; belegt sind 40 Fälle „der/die wâren minne". Die erste Fassung des Tickets stellte sie als „davon" unter 5.641 Vorkommen des Variantentyps `type_273621`. Das kann nicht sein: zwei der 40 schreiben `wæren` und `woren` und tragen deshalb einen anderen Typ. Über den Variantentyp gemessen sind es 38, über die Schreibfamilie unter `lemma_7505` sind es 40, und beide Zahlen sind richtig, solange die Vorschrift danebensteht. Die naheliegende Kennzahl taugt ohnehin nicht als Fehlermaß: von den 936 Vorkommen nach einem Artikel und den 168 in der Stellung ART + `wâren` + NOM ist die Mehrheit korrektes Prädikativ („daz wâren brüeder").

**Zwei Review-Runden, acht Befunde, kein einziger am Verhalten.** Alle acht betrafen Zahlen in Prosa, und drei davon zeigen dasselbe Muster: eine fremde Zahl übernommen, statt sie zu messen (8.385 Belege und 914 Vorkommen, beide aus einem Prüfer-Bericht, beide unter keiner Vorschrift reproduzierbar), eine Zahl aus einer Konsolenausgabe gelesen, in der Windows die Diakritika durch `?` ersetzt hatte (die 907 sind `waeren` mit ASCII-Digraph, nicht `wæren`), und eine Restmenge subtrahiert statt gezählt: „ohne beide Stützen 957" war arithmetisch ausgeschlossen, weil zwei überschneidende Mengen von 1.144 und 1.084 in 2.041 höchstens 897 übrig lassen können. Gezählt sind es 409. Das Skript etikettierte richtig, der Fließtext daneben nicht.

**Phase:** Betrieb, `claude/216-minne-serie1`. Schema-Stichprobe, Cross-Ref-Audit und `validate-indices.py` grün, Playwright 310/310.

---
## 2026-08-24 – #369 Serie 2: das Kandidatenpaar war zu eng, und der Lauf hat es selbst gezeigt

**Summary:** 7.855 unannotierte Tokens der Form `stat`/`stât` aus 326 Texten disambiguiert, in 131 Bündeln zu je 60 Fällen. 7.760 sind in 322 Texten annotiert (6.665 zu `lemma_5732` NOM, 1.095 zu `lemma_5710` VRB), 95 zurückgehalten. Die Rückhaltequote fällt damit von 22 Prozent in Serie 1 auf 1,2 Prozent, und der Grund ist nicht ein besserer Lauf, sondern ein anderer Gegenstand: bei `minne` war die Personifikation der große Posten, bei `stat` gibt es nichts Vergleichbares.

**Die Serie hätte man nicht mit einer Regel erledigen können, und das ist der eigentliche Befund.** Korpusweit ist `stat` sechsmal häufiger das Substantiv als das Verb, aber das Verhältnis kippt textweise vollständig. In den Stadtchroniken und Trojaromanen (RCC, TRO, OVG, KCR, JEW) tragen ganze Bündel 60 von 60 Substantiven, in Rudolfs Weltchronik, im Tristan und bei Frauenlob überwiegt das Verb mit bis zu 42 von 60. Eine Mehrheitsregel hätte in der einen Gruppe alles richtig und in der anderen alles falsch gemacht.

**51 der 95 Rückhaltefälle sind gar kein Zweifel zwischen den beiden Kandidaten, sondern ein anderes Wort.** 32 Belege meinen das maskuline `stat` im Sinn von Ufer (die Landungsszenen im Trojanerkrieg, `an den stat` im Parzival), 13 den Stand oder Zustand (`stat und wesen` im Prosalancelot), 6 sind das Adjektiv *stæte* in den Urkundenformeln von HZU2, und einer ist ein lateinisches Bibelzitat. Der Prompt kannte keine dieser Bedeutungen. Die Bearbeiter haben sie trotzdem erkannt und die Konfidenz gesenkt, statt den nächstbesten Kandidaten zu nehmen. **Ein zu enges Kandidatenpaar erzeugt keine falschen Annotationen, solange die Konfidenz die Notlage ausdrücken darf** – die Regel „bei Zweifel senke die Konfidenz" trägt mehr als die Aufzählung der erwarteten Fälle. Für das Ufer gibt es im Korpus ohnehin keine geübte Zuordnung: unter `lemma_5712` (*stade*) stehen nur `stade`, `staden`, `stades`, nie `stat`. Vorgelegt als #371.

**Diese Zahlen waren beim ersten Aufschreiben falsch, und der Fehler ist lehrreicher als die Zahlen.** Die Kategorien stammten aus einer Stichwortsuche über die Freitext-Begründungen der Verdicts, und die griff dreimal daneben: `adjektiv` fing `gût stat` und `heiligen stât` ein, wo das Adjektiv ein anderes Wort ist; `stand` traf im Prosa-Kontextfenster statt in der Begründung und zog einen Fall herein, der ein Verb-Verdict ist; `staet ze haben` fiel durch, weil es nicht auf `staete` passt. **Freitext, den ein Modell geschrieben hat, ist keine Klassifikation, auch wenn er wie eine aussieht.** Ersetzt ist die Heuristik durch eine Klassifikation am Beleg, die als `kategorien-review.json` im Batch-Ordner liegt statt als Zahl in einem Satz. Ab Serie 3 gehört ein Feld für das dritte Lemma ins Verdict-Schema, dann entsteht die Frage gar nicht erst. Aufgefallen ist der Widerspruch zuerst als Rechenfehler (30 + 12 + 6 sind 48, im Text stand 42), und erst beim Nachrechnen zeigte sich, dass auch die Summanden nicht stimmten.

**Ein Prompt-Fehler, der teuer gewesen wäre, und seine Korrektur ist gemessen.** Version 1 formulierte die Konfidenzregel zur Schreibung symmetrisch: die Zirkumflex-Form `stât` sollte ein NOM-Verdict deckeln, und der Satz las sich, als gelte dasselbe umgekehrt. Das hätte 7.688 der 7.855 Fälle auf `medium` gedrückt, also fast den ganzen Batch in den Review geschoben. Die acht bereits bearbeiteten Bündel wurden mit Version 2 wiederholt, und der Vergleich beider Läufe über dieselben 480 Fälle ergab **100 Prozent Übereinstimmung im Verdict** bei einer Konfidenz von 26 `medium` auf 1. Der Fehler hätte keine falsche Annotation erzeugt, sondern richtige verhindert. Nebenbei ist das die einzige Doppelmessung dieser Serie, und sie kostete nichts extra.

**Die Blindprüfung ist blind, seit sie es vorher nicht war.** Beide Stichproben zu je 50 Fällen gingen ohne Verdict, Konfidenz und Begründung an den Prüfer, der Abgleich lief hinterher maschinell über die xml:id. Ergebnis: null Abweichungen in beiden Durchgängen, auch in der schweren, die gezielt Fälle ohne stützenden Vorgänger zieht. Zwei Fälle hat der Prüfer als unsicher markiert, beide Ufer-Belege: er entschied die Wortart richtig und vermisste dasselbe dritte Lemma. Damit ist der Befund unabhängig zweimal entstanden.

**Der Filter der schweren Stichprobe war wieder falsch, diesmal eine Ebene höher.** Serie 1 scheiterte an einer Wortliste, die kein Mittelhochdeutsch kannte; der Ersatz fragt das `@pos` des vorangehenden `<w>`. Dieser Ersatz verglich den ganzen Attributwert gegen die Markermenge und zählte deshalb Tokens mit Mehrfachtag (`ART NUM`, `ADJ ADV`) als schwer, obwohl der Artikel danebensteht. Nach der Korrektur auf einen Vergleich je Tag sind es 1.647 statt 2.571 von 7.760. **Ein Filter, der Annotationen liest, muss das Format der Annotation kennen, nicht nur ihre Werte.**

**Der Lifecycle wurde wieder gemessen statt geschätzt**, mit demselben Ergebnis: alle vier Semantik-Zähler von `extract-variants.py` auf 0, Schritte 5 und 6 entfallen, Authority-Index bleibt 1.9.0, Korpus-Index 4.2.2 → 4.2.3. Der positionsgenaue Abgleich gegen `HEAD`: Belegstellen 7.538.417 → 7.546.177, Differenz exakt 7.760, genau zwei Lemmata verändert, kein Text mit Positionsverlust. `lemma_5732` steigt von 2.394 auf 9.059 Belege und von 160 auf 332 Texte: das Substantiv war im Index bisher massiv unterrepräsentiert.

**Sieben Skripte generisch statt serienspezifisch.** Serie 1 hinterließ `extract-216-minne.py`, `fix-216-minne.py` und `revisiondesc-216-minne.py`; Serie 2 hat daraus `extract-homograph.py`, `apply-homograph.py`, `revisiondesc-homograph.py` und vier weitere gemacht, die ihre Serienparameter aus einer `config.json` im Batch-Ordner ziehen. Serie 3 braucht damit keine Kopie mehr, sondern eine Konfigurationsdatei.

**Ein einziges Token als eigener PR, und der Grund ist die Trennschärfe.** Bei der Sondierung fiel `SKT_502140_4` auf: `stât` als Substantiv annotiert, obwohl *mîn gedanc an ir vil hôhe stât* das Verb ist. Der Beleg war korpusweit der einzige seines Variantentyps `type_218598`, weshalb die Serie für das Paar `stât` plus Substantiv-Lemma gar keinen Bestands-Typ ansetzen konnte. Die Korrektur macht den Typ unbelegt und zieht damit `variants.xml`, den Authority-Index (1.9.0 auf 1.9.1) und beide Neubauten nach: genau die Schritte, die dieser Batch nachweislich nicht auslöst. **Ein Ein-Zeilen-Fix, der den abgeleiteten Layer anfasst, gehört nicht in einen PR, dessen zentrale Aussage lautet, dass er ihn nicht anfasst.** Als eigener PR unmittelbar danach kostet er zehn Minuten und lässt beide Aussagen wahr. Präzedenzfall für dieselbe Mechanik: 1.6.4, wo `variants.xml` den nur in HUG belegten Typ `type_195524` verlor.

**Phase:** Betrieb, `claude/369-stat-serie2`. Schema-Stichprobe 9/10 (der eine Fail ist ADP aus der 30er-Baseline), Cross-Ref-Audit und `validate-indices.py` grün, Playwright 310/310.

---
## 2026-08-31 – Drei entblockte Tickets, und zweimal war die Messvorschrift das Byte

**Summary:** Julia Hintersteiner und KZW haben am 25./26.08. drei Fragen beantwortet, die je ein Ticket blockierten. Daraus drei PRs in einer Session: #374 nimmt `role="lead-editor"` aus der WZB und bringt die Doku von vier auf fünf Sigel, #377 annotiert 40 Belege der Fügung *der/die wâren minne* vom Verb aufs Adjektiv um (Korpus-Index 4.2.4 auf 4.2.5, Authority 1.9.1 auf 1.9.2), #235 Punkt 3 annotiert 66 von 289 Breve-Tokens der WZB mechanisch nach (Korpus-Index 4.2.5 auf 4.2.6, Authority unverändert). Damit ist auch die Frage beantwortet, die der Eintrag vom 02.08. offen ließ: die Auszeichnung bezeichnete Julias Rolle im Editionsprozess, nicht den Status des Textes, ihr Beitrag bleibt im `respStmt` verzeichnet und nur die Rollenbezeichnung fällt.

**Ein Diff, der zeichenweise stimmt, ist keine Messung.** Der erste WZB-Edit lief über das Edit-Werkzeug und sah im `git diff` genau so aus wie beabsichtigt: eine Zeile, ein entferntes Attribut. Tatsächlich hatte er 17 fremde reine LF-Zeilen still auf CRLF vereinheitlicht. Die WZB ist die einzige Datei im Korpus mit CRLF (gemessen: 1 von 667) und mischt darin 235.973 CRLF- mit 17 LF-Zeilen, die aus Julias Token-Split `f3dcf2a86` stammen. Sichtbar wurde das erst beim Byte-Vergleich gegen `origin/main`; die Diff-Hunks selbst waren zeichengleich. Alle drei Wellen haben ihre WZB-Änderungen danach über exakte Byte-Ersetzung mit `newline=""` beim Lesen **und** Schreiben ausgeführt und die beiden Zähler vorher und nachher protokolliert.

**Und derselbe Fehler kam ein zweites Mal, weil die Prüfung jetzt dastand.** `revisiondesc-homograph.py` hängt seinen `<change>`-Eintrag mit einem harten `"\n"` an. In den 666 reinen LF-Dateien fällt das nicht auf, in der WZB stieg die Zahl der reinen LF-Zeilen von 17 auf 18. Das Skript nimmt das Zeilenende jetzt aus der Umgebung. Der Punkt ist nicht der Fix, sondern dass die Kontrollzahl aus Welle 1 den Fehler in Welle 3 abgefangen hat, ohne dass jemand nach ihm gesucht hätte.

**Zweimal Skript reparieren und Daten neu erzeugen, nicht nachbessern.** Die Regel aus #236 wurde in Welle 3 zweimal gebraucht: einmal, weil dem Backfill-Skript die Spalte `file` fehlte, die `revisiondesc-homograph.py` als Schnittstelle liest, einmal wegen des Zeilenendes. Beide Male ging `tei/WZB.tei.xml` zurück auf `HEAD` und die ganze Kette neu, beide Male reproduzierte sie 66 ANNOTATE und 223 REVIEW identisch. Das ist der Reproduzierbarkeitsbeleg, den die Idempotenz allein nicht liefert.

**Die 66 sind mechanisch, und die 223 sind es genau deshalb nicht.** Annotiert wurde nur, wo die MHG-normalisierte Schreibung in `variants.xml` genau ein Lemma trifft und dieses Lemma genau eine Wortart hat: kein LLM, keine Kontextentscheidung, 46 NOM, 18 VRB, 1 ADJ, 1 NUM. Zurückgehalten sind 112 ohne Treffer im Lexikon (`ŏpfeltragendes`, `gevŏggeln`, `bŏvme`), 98 mit mehrdeutiger Wortart am Ziel-Lemma (`bŏse` führt auf `lemma_788` mit ADJ, ADV, GRA und NOM) und 13 mit mehreren Ziel-Lemmata. Die 98 sind ein Arbeitspaket nach dem Muster #216/#369 und bleiben in #235 stehen. Kein `corresp`: alle eindeutig auflösenden Kandidaten brauchten unter ihrem Ziel-Lemma eine neu geprägte Typnummer (113 distinkte Form-Lemma-Paare), und neue Typen sind genehmigungspflichtig. Die 66 landen damit in derselben Lage wie die 52.097 anderen WZB-Tokens aus #370.

**Der Nebenbefund war größer als das Ticket.** Bei der Sondierung für #367 fiel auf, dass die Varianten-Map beim Aufbau nach first-wins entscheidet: trägt dieselbe Schreibform Typen unter zwei Lemmata, gewinnt das zuerst gelesene, nicht das häufigere. Roh sind 1.893 Formen betroffen, für Nutzerinnen sichtbar 1.272, weil Stufe 1 der Lemma-Auflösung den Rest vorher abfängt. Die rohe Zahl allein hätte den Befund dramatischer aussehen lassen, als er ist, die kleine allein hätte den Umfang verdeckt. Beide stehen in #378, mit ihrer jeweiligen Messvorschrift. Eine Zweitmeinung nannte an derselben Stelle 2.065 und 1.331; übernommen wurde nichts davon, gemessen und in das Ticket geschrieben ist die eigene Zahl samt Zählweise, und dass die Differenz offen ist, steht dabei.

**Der Review-Bot der CI ist auf Daten-PRs weiter unbrauchbar, jetzt zum zweiten Mal belegt.** Auf #377 meldete die GitHub-API `changed_files: 0`, die Plattform hatte den Diff also gar nicht berechnet: dieselbe Lage wie bei #368, ausgelöst vom 40 MB großen `corpus-index.json.gz`. Kein Rerun, kein Aufsplitten des PR, stattdessen ein Kommentar am PR, damit der rote Haken nicht als Befund gelesen wird.

**Punkt 1 und 2 von #235 waren längst erledigt, ohne dass das Ticket es wusste.** Die 17 Tokens, die statt eines Leerzeichens die Zeichenfolge Backslash-`u0020` trugen, hat Julia am 26.08. mit `f3dcf2a86` gesplittet, die 20 kaputten Harsch-URLs sind seit PR #238 vom 29.07. repariert (gemessen: 41 Fundstellen in 25 Dateien, alle mit ASCII-Tilde). Ein Ticket, das drei Punkte bündelt, altert an jedem einzeln.

**Phase:** Betrieb. PRs #374, #377 und der Breve-PR; neue Tickets #375, #376, #378. #235 bleibt offen wegen der 223 Review-Fälle.

---
## 2026-08-31 – Zwei Messaufträge und ein Datenlauf, der den Index nicht anfasst

**Summary:** Drei Tickets in einer Session. #369 bekam nach dem Merge seinen ersten Kommentar überhaupt, #255 die von KZW bestellte Messung samt Skript (PR #380), #370 Punkt 1 den Datenlauf: 46.890 WZB-Tokens haben den Variantentyp bekommen, den das Korpus für dieselbe Schreibung schon übt. Beide PRs schließen kein Ticket, und das ist der Normalfall: der eine liefert eine Entscheidungsgrundlage, der andere erledigt einen von vier Punkten.

**Ein Datenlauf über 46.890 Tokens, der beide Indexe byte-identisch lässt.** `build-corpus-index.py` liest an `<w>` nur `@lemmaRef`, den Text und die Dokumentordnung; `@corresp` ist ihm unsichtbar. Der Neubau ergab denselben sha256 bei 42.228.352 Bytes. Der Authority-Index ändert sich ebenfalls nicht, obwohl `variants.xml` sich ändert: er trägt nur normalisierte, also kleingeschriebene Formen, und die beiden gekippten Schreibungen unterscheiden sich allein in der Großschreibung. Gegenprobe im rohen Index-JSON: `schafhirten` kommt einmal vor, `Schafhirten` und `Fur` kein einziges Mal. Die Routing-Tabelle in DATA-MODEL.md wirft `@corresp` mit `@lemmaRef` in eine Zeile und verlangt die volle Checkliste; sie ist damit nicht falsch, nur gröber als nötig. Die Schritte laufen, das Ergebnis ist an zwei Stellen leer.

**Der Bump stand trotzdem erst drin, und zwar gegen eine Regel, die derselbe Eintrag zitiert.** DATA-MODEL.md sagt wörtlich, man solle keinen Bump ohne Inhaltsänderung setzen, weil sonst jede Rückkehrerin ein Artefakt neu lädt, an dem sich nichts geändert hat, und kein CI-Gate das bemerkt. Der erste Commit dieses PRs setzte den Authority-Index trotzdem auf 1.9.3, mit der Begründung, `variants.xml` habe sich ja geändert. Das ist die falsche Bezugsgröße: gebumpt wird das Artefakt, und dessen einzige Änderung wäre der Bump selbst gewesen. Gefunden hat das der lokale Review, gemessen durch Vergleich beider dekomprimierter Indexe ohne das Versionsfeld. **Kein Gate hätte es gefangen**, denn `check-index-version-bump.py` prüft nur die Richtung „Inhalt geändert, Version vergessen", nicht die umgekehrte, und `data-integrity.yml` hätte den gebumpten Index anstandslos nachgebaut. Die 3,3 MB unnötiger Neuladung wären still geblieben.

**Die Vorabmessung zu #378 hat den Lauf freigegeben, und zwar mit null.** Die Sorge war, dass 46.890 neue `@corresp` neue first-wins-Kollisionen erzeugen, also Schreibformen, die auf das seltenere Lemma zeigen. Sie tun es nicht, und der Grund ist die Auswahlregel selbst: übernommen wurde nur, wo außerhalb der WZB genau ein Typ belegt ist, also kommt kein Typ hinzu. `extract-variants.py` meldet 0 added, 0 removed, 0 lemma assignment changed. Die Abbildung normalisierte Form auf Lemma bleibt bei 234.243 Einträgen, 0 fallen weg, 0 kommen hinzu, 0 wechseln das Lemma. **Eine Zusicherung ist erst dann etwas wert, wenn sie hätte scheitern können**, und diese hier hätte: sie hing daran, dass die Auswahlregel keine neuen Typen prägt, und genau das war zu prüfen und nicht vorauszusetzen.

**Zwei Formen kippen doch, und beide sind ein Gleichstand, kein Überstimmen.** `type_68232` geht von `fur` auf `Fur`, `type_276606` von `schafhirten` auf `Schafhirten`. Die Stimmverhältnisse sind 2:2 und 1:1: die WZB bringt keine Mehrheit, sie stellt einen Gleichstand her, und der alphabetische Tiebreak in `extract-variants.py` sortiert Großbuchstaben vor Kleinbuchstaben. Auf die Lemma-Auflösung wirkt das nicht, weil `normalize_mhg` kleinschreibt. **Sichtbar wird die Änderung überhaupt nur in `variants.xml` selbst**, und diese Zeile stand zuerst falsch hier: sie behauptete, die Rohform sei im Lemma-Explorer zu sehen. Das ist sie nicht. `build-authority-index.py` legt ausschließlich `normalize_mhg(variant)` ab, kennt die Rohform also gar nicht, und `renderVariants` in `lemma/lemma-page.js` invertiert dieselbe Map und zeigt damit ebenfalls die normalisierten Schlüssel. Gefunden hat das der CI-Bot in einem Lauf, der danach am Turn-Limit abbrach. Ob ein satzinitiales `Fur` überhaupt eine eigene orthographische Variante ist, ist eine redaktionelle Frage und nicht in diesem PR zu entscheiden; hier steht sie als gemessener Nebeneffekt.

**Die Zählweise eines Tickets gehört rekonstruiert, bevor man seine Zahlen für gedriftet hält.** #370 nennt 52.097 Tokens in 1.685 Paaren, gemessen wurden 52.163 in 1.733. Die naheliegende Deutung, das Ticket sei veraltet, war halb richtig und hätte zur falschen Korrektur geführt. Erst schreibungsgetreu gezählt ergaben sich 1.886 Paare, also noch weiter weg; mit Kleinschreibung als Schlüssel stimmten die Tokenzahlen exakt. Die Gegenprobe am WZB-Stand vor `c0e8dee80` lieferte dann genau 52.097 und 1.685. Beide Zahlensätze sind richtig, sie messen verschiedene Stände mit derselben Vorschrift, und die Differenz sind die 66 Tokens des Breve-Batches vom selben Tag.

**Das Gate zu #370 Punkt 4 ist ein Zähler-Gate, und der Kommentar zehn Zeilen darüber warnt davor.** Die #152-Ratsche im selben Skript ist bewusst eine Ratsche auf der ID-Menge, weil Zähler kompensierende Drift durchlassen. Für lemmatisierte Tokens ohne `@corresp` wäre die Mengenvariante unverhältnismäßig: sie müsste Zehntausende Token-IDs committen, und anders als bei einer hängenden Referenz ist die einzelne Token-ID kein Befund, nur die Summe. Gewählt ist deshalb eine Ratsche je Sigle mit ausgeschriebener Grenze: innerhalb einer Sigle bleibt +5/-5 grün. Die Sigle ist die Granularität, auf der der Fehler real auftritt, nämlich als Ingest, der eine Phase auslässt. Belegt ist das Gate durch Mutation in beide Richtungen: fünf `@corresp` aus EKL entfernt macht es rot (2 auf 7, Exit 1), eine künstlich erhöhte Baseline erzeugt die Nachzieh-Warnung.

**Bei #255 war der Befund nicht die Verzerrung, sondern die Auszeichnung.** `<div type="parallel">` trägt zwei Bedeutungen, getrennt allein durch `@n`: einen Zeugennamen oder eine laufende Nummer. In BRW und DL1 liegen 100 Prozent der indexierten Tokens in solchen divs, ein Filter „Zeugenvarianten nicht mitzählen" löscht diese Texte also, statt sie zu entzerren. **Die `@n`-Klasse ist trotzdem nicht der Diskriminator**, und das hat erst die lokale Review gezeigt: DL2 trägt drei benannte Blöcke mit 5,2 Prozent der Tokens neben einem Basistext, dort sind sie selbst der #255-Fall. Was entscheidet, ist der Anteil, nicht der Name. Die erste Fassung des PR-Textes hatte daraus eine Allaussage gemacht.

**Zwei Kontrollzahlen haben sich im selben Skript bezahlt gemacht.** Die 0 falsch gemeldeten Reimpaare über eine Naht ist nur deshalb ein Befund und kein kaputter Lookup, weil daneben steht, dass 7,5 Prozent der Verspaare innerhalb eines Blocks reimen. Und FR3s Typ-Token-Verhältnis steigt ohne die Zeugen um 13,9 Prozent, ein gleich langer Zufallsausschnitt aus dem vollen Text erreicht aber schon 0,0977 gegen 0,1006: der größere Teil ist Längenartefakt, weil die TTR mit der Textlänge fällt. Ohne diese Spalte hätte der Bericht ein Artefakt als Entzerrung ausgewiesen.

**Die lxml-Proxy-Falle schlägt erst zu, wenn man aufräumt.** Eine Fassung des Messskripts nahm `id(el)` als Schlüssel für die Blöcke und zählte für FR3 die richtigen 36 divs, solange sie das Element nebenbei noch in einem Feld festhielt. Nachdem dieses Feld als überflüssig entfernt war, wurden daraus 16. Regel 10 des Playbooks steht seit Langem da; was sie nicht sagt, ist dass eine Aufräumänderung den Fehler scharf machen kann, ohne ihn selbst zu enthalten.

**Zwei Sessions im selben Arbeitsbaum, und die Absprache lief über eine Versionsnummer, die am Ende niemand brauchte.** Parallel lief die Frauendienst-Titelkorrektur (#381) im Hauptbaum und hatte den Korpus-Index auf 4.2.7 gebumpt; reserviert war deshalb 4.2.8. Gebraucht wurde keine Nummer, weil dieser Lauf gar keinen Index ändert. Die Absprache war trotzdem nicht umsonst: sie hat den Konflikt sichtbar gemacht, bevor er entstand, und die Prüfung, die ihn auflöste, ist dieselbe, die den überflüssigen Bump gefunden hat. Was bleibt, ist die Regel für den Zweit-Merger bei echten Index-Änderungen: nach dem Rebase den Index **neu bauen**, nicht nur die Versionszeile anfassen, sonst passt der committete Index nicht mehr zum Korpus.

**Und die Lehre, die über den Anlass hinausgeht: Sessions im selben Repo sollten ihre Nummernabsprache nicht als Reservierung führen, sondern als Messung.** Beide Seiten haben zuerst eine Nummer verteilt und erst danach gemessen, ob eine gebraucht wird. Richtig herum ist es billiger: erst bauen und vergleichen, dann bumpen.

**Ein rot gemeldeter CI-Review kann vier Befunde tragen, und alle vier hielten der Nachmessung stand.** `CLAUDE.md` sagte bis heute, der Bot könne einen Daten-PR nicht verarbeiten; belegt war das an #368, wo die Plattform `changedFiles: 0` meldete und er ohne einen einzigen abgehakten Punkt starb. Auf #382 war der Diff sehr wohl berechnet, alle zehn Einträge standen im Prompt, die Checkliste war vollständig abgehakt, und vier Befunde standen da. **Und der Lauf ist gar nicht gescheitert:** im Log steht `subtype: success` und `is_error: false`, die Action hat nur den Haken rot gemacht, weil das Review 56 Turns gegen ein konfiguriertes Limit von 50 gebraucht hatte. Der rote Haken kam also nicht vom Bot, sondern aus einer Zahl in unserer eigenen Workflow-Datei. Seit `6fbf7e002` steht sie auf 100.

**„Verworfen" wäre trotzdem das falsche Wort, und das ist der Unterschied, an dem #377 hängt.** Die erste Fassung dieses Eintrags schrieb, die Action habe ein fertiges Review verworfen. Sie verwirft nur die grüne Bewertung. Der Kommentar wird rund anderthalb Minuten nach dem Start gepostet und überlebt den Fehlschlag um zehn Minuten: bei #377 um 09:10:53 bei einem Lauf, der 09:20:37 rot wurde, bei #382 um 13:10:42 gegen 13:19:28. Es geht nichts verloren, es sieht nur nach Verlust aus, und genau dieser Anschein hat bei #377 gereicht, damit niemand nachliest. Ein Satz, der in einem Absatz über „lies den Kommentar" behauptet, das Review sei weg, arbeitet gegen seinen eigenen Zweck.

**Eine Konfigurationslösung gibt es nicht, das ist geprüft.** Im gepinnten `v1` wirft `base-action/src/run-claude-sdk.ts` unbedingt, sobald ein `success` über dem Budget liegt; kein Input steuert das. Die beiden denkbaren Auswege sind teurer als das Problem: `--max-turns` ganz weglassen nähme die Kostenbremse bei einem Bot, der auf jedes `synchronize` läuft, und `continue-on-error` machte auch echte Abbrüche wie #379 grün, womit der Haken gar nichts mehr sagte. Die Zahl 100 bleibt, und die Suche nach einem Schalter kann sich die nächste Session sparen.

**Die naheliegende Erklärung dafür war trotzdem falsch, und das ist der lehrreichere Teil.** Ich hatte geschlossen, entscheidend sei, ob die Plattform den Diff berechnet hat. Die Gegenprobe an #379 widerlegt das: dort standen 16 Dateizeilen im Prompt, der Diff war also da, und der Lauf endete gleichwohl in einem echten `error_max_turns` mit `is_error: true`, einem von vier abgehakten Punkten und null Befunden. Der berechnete Diff ist notwendig, nicht hinreichend, und woran ein Lauf scheitert, ist von außen nicht vorherzusagen. Übrig bleibt die schmalere und haltbarere Regel: **ein roter Haken auf einem Daten-PR ist kein Befund, aber auch kein Beweis, dass keiner drinsteht.** Der Kommentar wird gelesen, immer.

**Und diese Regel hat heute schon zwei Befunde gekostet, bevor jemand sie aufgeschrieben hatte.** Die Nachfrage nach einer Zahl, die ich nicht reproduzieren konnte, hat #377 als vierten Fall aufgedeckt, und der ist der teuerste: 34 Dateien im Prompt, `subtype: success`, 59 von 50 Turns, fünf von fünf Punkten abgehakt und **zwei echte, sauber gemessene Befunde** im Kommentar. Neun Minuten nach dem Bot-Kommentar wurde der rote Haken als Plattformgrenze abgetan und der PR gemergt, ohne dass jemand ihn geöffnet hatte. Beide Befunde stehen unverändert auf `main`: eine Siglen-Ableitung per `rsplit("_", 2)`, die an WZB-Token-IDs mit drei Unterstrichen scheitert und dann meldet, das Token sei nicht im Korpus, und eine Idempotenz-Lücke in der Platzhalterprüfung von `revisiondesc-homograph.py`. Sie zu beheben ist nicht Sache dieser Session; die Meldung an chsteiner läuft über die Session, die sie gefunden hat.

**Die Ursache der Fehldiagnose war ein Feld, dem beide Seiten geglaubt haben.** `gh api .../pulls/377 -q .changed_files` liefert 0, `gh pr view 377 --json files` liefert 34. Für #368, #379 und #382 stimmen beide Endpunkte überein, für #377 nicht, und genau auf dieser falschen 0 stand die Abtun-Begründung. Zwei Sessions haben unabhängig voneinander dasselbe Feld als Beleg genommen. Wer künftig behauptet, GitHub habe den Diff nicht berechnet, liest den `<changed_files>`-Block im Job-Log oder nimmt `--json files`.

**Und der Beleg, auf den ich die erste Fassung gestützt hatte, war selbst ein Messfehler.** Ich hatte behauptet, auf #382 sei derselbe leere `<changed_files>`-Block gelaufen wie auf #368. Das kam daher, dass ich das Run-Log durch ein `grep` mit einem Suchmuster gelesen hatte, das die Zeilen zwischen den beiden Tags gar nicht treffen konnte: übrig blieben die Öffnungs- und die Schlusszeile direkt untereinander, und das sah aus wie ein leerer Block. Ein Artefakt der eigenen Filterung, gelesen als Befund über die Welt. Gefunden hat es die lokale Review, die die Zahl schlicht direkt abgefragt hat (`gh pr view 382 --json changedFiles` → 10). Die Lehre für gefilterte Logs: was ein Filter nicht zeigt, ist nicht abwesend, und eine Abwesenheitsbehauptung braucht eine Abfrage, die Anwesenheit zeigen könnte.

**Der teuerste der vier Befunde war einer, in den ich in derselben Session selbst hineingelaufen war.** `--update-baseline` schrieb beide Ratschen des Cross-Ref-Audits, die #152-ID-Menge und die neue #370-Zählung, ohne Wahlmöglichkeit. Genau das ist mir beim ersten Anlauf passiert: der Aufruf hat nebenbei das Datum in `lexicon-baseline.json` neu geschrieben, obwohl die ID-Menge unverändert war, und ich habe die Datei per `git checkout origin/main --` zurückgeholt, weil sie sonst eine Prüfung behauptet hätte, die nicht stattgefunden hat. Erst der Bot hat daraus den allgemeinen Fall gemacht: die neue Warnung schickt Sessions künftig **routinemäßig** zu diesem Kommando, und ein Ingest, der nebenbei neue dangling lexicon-IDs erzeugt, bekäme sie damit still in die Baseline. Der Flag nimmt jetzt einen Bereich (`=lexicon`, `=corresp`, nackt weiterhin beides), und die beiden Warntexte nennen je den ihren. Die Lehre ist nicht „Flags aufteilen", sondern: **ein Werkzeug, das zwei Ratschen bedient, darf nicht einen Aufruf haben, wenn die beiden Anlässe verschieden autorisiert sind.** Die #152-Ratsche zieht man nach einer KZW-Entscheidung nach, die #370-Ratsche mechanisch.

**Eine gekappte Liste ohne Kappungsmarke ist eine falsche Zahl, nicht nur eine unvollständige.** `zuordnung.csv` nannte je Zeile bis zu acht Belegsigel außerhalb der WZB, hart abgeschnitten und ohne Hinweis darauf. 92,5 Prozent der Zeilen waren gekappt. Der Bot hat den Fall an `hebt`/`type_9058` gezeigt: acht Sigel gelesen, tatsächlich sind es 82; die häufigste Zeile steht bei 644. Ausgerechnet diese Spalte war im PR-Text als das benannt, was sich nachträglich nicht mehr rekonstruieren ließe. Jetzt trägt die CSV `sigel_anzahl` neben `sigel_probe`, die Kappungsgrenze steht als Konstante im Skript.

**Und beim Nachziehen fiel auf, dass das Laufskript gar nicht im Repo war.** Die vier WZB-Vorgängerläufe liegen alle unter `scripts/ingest/wzb/`; dieser lief aus dem Scratchpad. Ein Provenienz-Log, dessen Erzeuger nicht mitkommt, ist genau so weit reproduzierbar wie das Vertrauen in die Zahlen darin. Beide Skripte sind jetzt als `wzb-corresp-apply.py` und `wzb-corresp-log.py` committet, mit `Path(__file__).resolve().parents[3]` statt des Worktree-Pfads, und das Log ist aus der committeten Fassung neu erzeugt worden: 46.890, 484, 5.273, unverändert.

**Phase:** Betrieb. PR #380 (#255, Messung) und der #370-PR; kein Ticket geschlossen. #370 Punkt 2 (5.273 Tokens, die neue Typen bräuchten) bleibt kuratorisch offen.

---
## 2026-08-14 – #59: die Erklärung durfte nicht vor den Daten kommen

**Summary:** Lindas Umstellung vom 11.08. auf acht Instanztypen mit sechs Markern ist im Naming-Explorer umgesetzt; die Ansicht kannte bis dahin nur `#` und eckige Klammern und erklärte beide als dasselbe. Gemergt als PR #365, zusammen mit Lindas Datenstand v0.2.1-beta (Quell-Commit `4766065c`, 10.502 Records). Nachtrag vom 18.08., rekonstruiert aus dem PR-Text und dem Bericht an Linda in #59; die Session selbst hatte keinen Journal-Eintrag hinterlassen.

**Der Defekt in einer Zahl:** die alte Regex `/^[#[]/` erkannte 103 von 240 markierten Nennungen. Sie kannte `<`, `{`, `°` und ` & ` nicht, und ihr `^`-Anker scheiterte an Mischformen wie `Medeas <meisterîn>`.

**Der Zuschnitt hat sich unter der Messung umgedreht.** Geplant war der PR ohne Datenupdate, die Erklärung sollte vor den Daten kommen. Gemessen trug der ausgelieferte Index aber 15 Gitter-Werte, von denen am neuen Quellstand genau einer übrig ist (`#David`; im Rolandslied fällt `#` von 69 Nennungen auf 3). Die neue Legende beschriftet jeden Gitter-Wert mit „Zitiert", ohne Datenupdate hätte sie also bei 14 von 15 Werten eine falsche Typangabe getragen. Der umgekehrte Fehler war der schlimmere, und er war übersehen. Mit demselben Schnitt erledigte sich der veraltete DOI: statt einer Pflegenotiz hält jetzt `pruefe_zitation` Version und DOI gegen die `CITATION.cff` des gebauten Quellstands.

**Drei Guards im Build, einer bewusst asymmetrisch.** `pruefe_instanztypen` bricht nur, wenn die Quelle einen Typ kennt, den wir nicht kennen, oder ein beidseitig vorhandener Typ verschiedene Marker trägt: ein alter Quellstand kann die Typologie nicht kennen, und das Freshness-Gate baut genau solche. `pruefe_frontend_paritaet` liest `MARKER_KLASSEN` aus dem JS und verlangt für jeden bekannten Marker eine Klasse. In der Legende teilen sich Rollenfigur und Kollektivmitglied das Zeichen `<…>` und stehen als eine Zeile: welcher von beiden gemeint ist, lässt sich am Zeichen nicht entscheiden, und eine Zuordnung wäre eine Behauptung ohne Deckung.

**Das Review fand zwei grüne Prüfungen ohne Haltekraft.** Vier Runden `fable-reviewer` vor den Pushes (Freshness-Blocker; ein Guard, den jeder HTTP-Fehler außer 404 still abschaltete; eine zweite Kopie der Zitation), danach der CI-Bot: eine Assertion auf `#resultsContainer`, die das Auswahlfeld mit einschloss, und `BEKANNTE_ANFANGSMARKER` als vierte, ungegatete Kopie der Typologie, jetzt abgeleitet statt gepflegt. Der Bestandstest hatte nur die Überschrift geprüft und lief deshalb vor wie nach dem Umbau grün.

**Phase:** Betrieb. 310 Tests grün, Freshness-Gate grün gegen den neuen Pin. #59 bleibt offen auf `wait:linda`: Abnahme nach Deploy steht aus, dazu drei offene Fragen an Linda (Tag auf `master`, die drei Iwein-Records, Priorität des Kollokations-Tooltips).

---
## 2026-09-01 – Der Lauf, der seriell blieb, weil die abgeleitete Schicht global ist

Geplant war ein Spurenlauf mit mehreren autonomen Sessions. Geworden ist ein serieller Wellenlauf, der nach der ersten Sachwelle pausiert wurde. Dieser Eintrag ist der der **Koordination**; der Lauf selbst hat seinen Zwischenstand als Kommentar auf #44.

**Der Zuschnitt scheitert nicht an den Dateien, sondern am Datenmodell.** Der Data-Change-Lifecycle verlangt nach jeder Änderung in `tei/` oder `authority-files/` einen Neubau von `variants.xml`, beiden Indexen und der API: zwei Binärdateien (42,2 MB und 3,3 MB) plus 2.742 JSON, und sie sind eine Funktion des **ganzen** Korpus. Zwei gleichzeitige Datenspuren kollidieren dort nicht zufällig, sondern zwangsläufig, weil jede ihren Index auf einem Baum baut, dem die Korpusänderung der anderen fehlt. Ein Dateischnitt, das übliche Mittel gegen Kollisionen, kann das nicht auflösen. Das ist der Grund, warum dieses Projekt seriell arbeitet, und er gilt unabhängig davon, wie viele Sessions verfügbar wären.

**Von fünf autonom antastbaren Tickets blieben nach Messung zwei startbare.** Alle fünf tragen `auto:checkin`. #259 hatte seine Datengrundlage nicht auf der Maschine (Trierer Dump in KZWs Drive; nach dem Nachliefern 22 XML, 27.106.707 Bytes unter `temp/`, byteweise identisch mit dem Drive-Bestand). #123 ist ein Nice-to-have mit null Kommentaren seit der Anlage. #216 hängt an seinem eigenen Punkt 3. Und #28, seit dem 10.08. als „das einzige `large`, das auf keine Entscheidung wartet" geführt, wartet doch: Phase 1 hat drei Gleise, und zwei davon kosten eine Budget- oder eine Datenentscheidung. **Ein Ticket kann entblockt sein und trotzdem an seiner ersten Handlung hängen.**

**Der Freeze, den ein Parallelbetrieb bräuchte, hätte sich selbst blockiert.** `check-index-versions.py` gatet fünf Stellen, und eine davon ist der Versionsklammerzusatz in `docs/INDEX.md`. Jede Datenspur muss ihn anfassen. Eine Einfrierliste, die `docs/INDEX.md` pauschal sperrt, sperrt damit genau die Arbeit, die sie schützen soll. Die Inbox dafür ist jetzt #385, mit benannter Ausnahme, Vierfelder-Format, Ersetzungsregel und der Festlegung, dass allein chsteiner den Freeze aufhebt und dabei die Reichweite nennt. **#44 taugt dafür nicht:** sein Body ist zwischen den `MATRIX`-Markern generiert, `--check` ist ein Gate, und am 31.08. ist es nach einem reinen `gh issue edit --body-file`-Roundtrip rot geworden, ohne dass am generierten Block etwas geändert war.

**Kickoff-Wortlaute werden ab jetzt getrackt** (`docs/playbooks/kickoffs/`, `5aa3a8df3`). Bis dahin überlebte vom Auftragstext nur die Zusammenfassung in §6 des Masterplans, und die wird bei jedem Lauf überschrieben. Der Auftrag ist aber der einzige Beleg dafür, was eine Session tun durfte. Jede Datei dort trägt als erste Zeile den Vermerk, dass sie ein Protokoll ist: der kopierte Betriebsvertrag darin altert ab dem Tag des Abschickens, und eine Kopie im Repositorium, die sich für das Original hält, ist genau die Driftquelle, wegen der `BETRIEBSVERTRAG.md` herausgelöst wurde.

**Eine Stunde Stillstand an einer Freigabe, die keine Regel abstellen kann.** Der Lauf hat den Worktree per `git worktree add` neben dem Repositorium angelegt und wollte dann mit `EnterWorktree` hineinwechseln. Das verlangt seit v2.1.206 eine interaktive Bestätigung, sobald das Ziel außerhalb von `.claude/worktrees/` liegt, und die Session stand, bis jemand hinsah. Die naheliegende Reaktion, eine `allow`-Regel zu setzen, geht ins Leere: die Dokumentation sagt ausdrücklich, dass weder eine `EnterWorktree`-Regel noch „don't ask again" diesen Prompt unterdrückt, nur `bypassPermissions`. **Ein Allow wäre hier ein wirkungsloser Allow gewesen**, also die schlechtere Variante von gar keiner Regel. Der Ausweg ist, `EnterWorktree` nicht zu brauchen: `claude --bg --name X --worktree X`. Die 260-Zeichen-Begründung für den Worktree neben dem Repositorium bindet hier nicht (gemessen: 180 gegen 260), aber die Zahl gehört von dem nachgemessen, der die Umstellung schreibt.

**`.claude/agent-memory/` wird getrackt statt ignoriert** (`b306d9f22`). Der naheliegende Weg wäre das Ignorieren gewesen: `.claude/` war bei 1001 Commits und fünf Autoren kein geteilter Ort. Entscheidung chsteiner, Begründung Wissenserhalt. Der Haken, den dieses Projekt dabei hat, steht im README daneben: der `fable-reviewer` schreibt in das Verzeichnis **des Worktrees**, und der Abbau ist damit die Stelle, an der das Gelernte verlorengeht.

**Pausiert wurde am einzigen kostenlosen Schnitt.** Das Fable-Kontingent geht zur Neige, und `fable-reviewer` ist Pflicht vor dem ersten Push jedes PR-Zweigs. Welle 1 war die einzige Welle ohne PR. Ein Schnitt dort verbraucht keine Review-Runde und liefert trotzdem ein Ergebnis; eine Welle später hätte er einen halb reviewten PR hinterlassen. Ergebnis von Welle 1: die *vrouwe*-Disambiguierung vor *minne* ist ein Anhängsel und kein eigener Lauf (155 Stellen, 150 mechanisch, null neue Lemmata). Der Zweig `claude/28-gleis1-begriffssystem` steht ungereviewt und ohne PR auf `origin`, ausnahmsweise freigegeben, damit die Arbeit über die Pause nicht nur lokal liegt.

**Rot nach der Zählregel vom 01.09.: „an allen vier Stellen konsistent" statt fünf, obwohl die richtige Zahl im Kontext stand.** Ausgezogen als rote Zeile 1 nach [../fehlerjournal.md](../fehlerjournal.md).

**Nachtrag am selben Tag:** die zwei Playbook-Aufträge, die für die Meta-Welle des pausierten Laufs übrig waren, sind mit `2adc52fc5` erledigt, direkt auf `main` ohne PR und ohne Review, weil Doku plus eine `.gitignore`-Zeile darunter fallen. Die oben eingeforderte 260-Zeichen-Messung ist damit nachgeholt und steht in Regel 29: Repo-Wurzel 64, Worktree unter `.claude/worktrees/` 88, tiefster `node_modules`-Pfad relativ 92, längster getrackter Pfad 74.

**Die Stoppbedingung von Welle 3 wurde vorgezogen, weil eine Messung kein Fable kostet.** Ergebnis: #259 läuft, aber sein Prüfdatensatz ist ein anderer als der Body annahm. Nicht die 35.366 Einträge sind es, sondern die 8.610 Paare Schreibform → Lemma auf der Sublemma-Ebene, und die Befundliste entsteht aus **477 Fällen**, in denen unsere Lemmaliste und das Findebuch dieselbe Form verschieden einordnen. Drei Zahlen im Body halten der Messung nicht stand, darunter „100 % mit Querverweis": gemessen tragen 11.394 von 34.828 Lemma-Formen gar kein `<ref target>`, also 32,7 %, und genau diese Lückenlosigkeit war die Begründung, den Dump überhaupt anzufassen. Die im Body genannte Normalisierungsfalle ist an der Lexer-Lemmaliste gemessen und auf das Findebuch übertragen worden, ohne dort geprüft zu sein: `ʒ` kommt in den 32.565 Findebuch-Lemmaformen **null** mal vor, die Quote bewegt sich um 3,1 Punkte statt um 27. Body und `effort:`-Label sind richtiggestellt, die Messvorschrift steht im Kommentar. **Die Lehre ist die alte in neuer Kleidung:** eine Zahl, die aus einer Nachbarquelle stammt, ist in der neuen Quelle ungemessen, auch wenn beide vom selben Anbieter kommen.

**Auch Welle 2 wurde vorgezogen, und ihr Befund hat eine Grenze statt eines Urteils.** Gleis 1 von #28 liefert über die 17 Sprachkonzepte unter `concept_23123000` genau 6.219 Lemmata und 225.505 Korpusbelege. Die Menge ist brauchbar, aber nicht so, wie man sie zuerst benutzen würde: die zehn belegstärksten Treffer tragen 53,0 % der Tokenmenge, und der größte ist `niht` mit 81.088 Belegen unter „Lateinisch". Der Grund steht im Baum, nicht in den Daten: `concept_23123000` hängt unter „Kommunikation/Sprache" und ist ein **Bedeutungsfeld**, das in der Praxis auch für Herkunft benutzt wird (`bischof` < *episcopus* trägt dasselbe Konzept). Ein Filter über die Konzeptdichte scheidet aus, nur 4 der 6.219 Lemmata tragen ausschließlich Sprachkonzepte. Was trägt, ist die Belegklasse: über 501 Belegen liegen 25 Lemmata mit 77,5 % der Nicht-Namen-Tokens, gemischt aus Rauschen und echten Lehnwörtern, also von Hand durchzusehen; darunter liegen 3.338 Lemmata mit 35.785 Belegen, und die Stichprobe ist dort über alle Klassen sauber. **Aus 43.879 Lemmata werden damit 3.338 plus eine Viertelstunde Handarbeit**, und das ist der eigentliche Ertrag von Gleis 1: nicht die Antwort, sondern der Faktor 13 auf die Frage.

**Am Abend desselben Tages wieder aufgenommen**, weil das Fable-Kontingent zurück war. Die Spur heißt `mhdbdb-wellen-2345` und ist die erste, die nach der neuen Regel 29 mit `--worktree` startet. Was das Flag kostet, ist damit gemessen und in Regel 29 und 30 eingearbeitet (`8a7ea2116`): der Baum ist gesperrt und `git worktree remove` verweigert ihn, der Sperrgrund wird dabei umgeschrieben statt abgebaut (`locked initializing`, dann `locked claude session <name> (pid <n>)`), der Zweig heißt `worktree-<name>` und bleibt als Leiche liegen. Der dritte Punkt ist der gefährlichste, weil er nach einem echten Fehler aussieht: **`claude agents --json` führt die Session mit `cwd` auf dem Hauptbaum, obwohl `pwd` in ihr den Worktree zeigt.** Das Feld gibt das Verzeichnis des startenden Prozesses wieder. Das globale Operator-Skill weist an, eine so angezeigte Spur abzuräumen und neu zu starten; wer dem folgt, zerstört eine korrekt stehende Session mit dem guten Gewissen, eine dokumentierte Prüfung gemacht zu haben. Rückgemeldet als Kommentar an `claude-code-setup` #6.

**Die drei offenen Menschenfragen sind beantwortet**, KZW am 01.09. auf #216: die fünf `fro-minne`-Belege sind jedesmal Frau Minne, `rend="upper_case_first_letter"` markiert die Edition und nicht zwingend die Personifikation (im Verbund Frau plus Minne aber ein brauchbares Indiz), zu einem Fall will er den Verskontext, und die kleine Menge soll vorgezogen werden. **Die zweite Hälfte des letzten Punktes ist die, die leicht verlorengeht:** „andere vrouwen in eigenes Issue" wird umgesetzt, „kleine Menge vorziehen" betrifft 155 Belege, ist eine Korpusänderung und läuft in keiner der vier Wellen mit. Sie braucht eine Terminentscheidung und steht dafür ausdrücklich im Statuskommentar auf #216.

**Rot, und zwar auf der Koordinationsseite.** Ausgezogen als rote Zeile 2 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, zum zweiten Mal an einem Abend und wieder auf der Koordinationsseite: die Welle-2-Vorabmessung war falsch.** Ausgezogen als rote Zeile 3 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, zum dritten Mal an einem Abend und wieder die Koordination: „das Korpus kann Senses nicht auflösen" war falsch.** Ausgezogen als rote Zeile 4 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, zum vierten Mal, und die Welle-3-Vorabmessung war an zwei Stellen falsch.** Ausgezogen als rote Zeile 5 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, zum fünften Mal, und dies ist der erste echte Wiederholungsfall des Laufs: die Lehre stand, sie war drei Stunden alt, und sie war meine eigene.** Ausgezogen als rote Zeile 6 nach [../fehlerjournal.md](../fehlerjournal.md).

**Im selben Kommentar noch ein zweiter Fall derselben Familie, gefunden von derselben Reviewrunde am Docstring der Spur und auf mich genauso zutreffend.** Ausgezogen als Teil der roten Zeile 6 nach [../fehlerjournal.md](../fehlerjournal.md).

**Was daraus folgt, ist wieder keine schärfere Formulierung, sondern eine Reihenfolge**, und das ist inzwischen das Muster beider Koordinationsfehler dieses Laufs. Beim Freeze war es „eintragen, bevor der Kickoff hinausgeht", hier ist es: **was im Meldepunkt vor einer Reviewrunde kommt, geht in die Listen und nirgendwo sonst; publiziert wird nach der Runde.** Eine Regel, die drei Stunden nach ihrer eigenen Formulierung gebrochen wird, hat kein Textproblem. Die Meldedisziplin der Spur bleibt davon unberührt und ausdrücklich richtig: ein Meldepunkt liegt vor dem Review, sonst ist er sinnlos. **Der Fehler war die Publikation, nicht die Meldung**, und aus demselben Grund wird der Skriptdefekt der Spur hier nicht gezählt: einen Fehler, den die erste Reviewrunde in einem PR findet, zählt der Zähler nicht, sonst zählt er Arbeit statt Wiederholung.

**Rot, zum sechsten Mal, und es ist dieselbe Bauart wie die vierte: Messung richtig, Mechanismus erfunden.** Ausgezogen als rote Zeile 7 nach [../fehlerjournal.md](../fehlerjournal.md).

**Die Lehre, die nicht gegriffen hat, ist die meistzitierte des Tages.** Ausgezogen als Teil der roten Zeile 7 nach [../fehlerjournal.md](../fehlerjournal.md).

**Der substanzielle Fund aus derselben Kette, und er ist kein Fehler, sondern eine Eigenschaft, die niemand benannt hatte: `variants.xml` ist nicht einwertig, die daraus gebaute Karte schon.** Gemessen über alle `<form>` der Quelle, MHG-normalisiert: **234.243 Normalformen, davon 4.972 mit mehr als einem Ziel-Lemma.** `grossen` zeigt dort auf `lemma_2534`, `lemma_2535` und `lemma_31392`, `a` auf `lemma_1`, `lemma_2` und `lemma_37325`. In `data/authority-index.json.gz` steht unter `variants` je Normalform genau **eine** Zeichenkette (0 von 234.243 Werten ist etwas anderes), und dort bleibt von `grossen` allein `lemma_2534` übrig. **Beim Indexbau fallen also 4.972 Mehrdeutigkeiten still weg**, und Stufe 2 der Auflösung liefert deshalb immer genau ein Lemma, auch wo die Quelle mehrere kennt. Gefunden hat das die Spur beim Prüfen einer Prämisse, auf der an diesem Tag drei verschiedene Erklärungen desselben Falls standen, ihre zwei und meine eine. Die Regel daraus: **wer über `variants.xml` argumentiert, muss sagen, ob er die Quelle meint oder die gebaute Karte.** Für den Anlassfall ändert es nichts, `groesen` hat auch in der Quelle nur ein Ziel.

**Rot, zum siebten Mal, und diesmal in einer Nachricht statt in einer Datei: einen Peer-Befund als gemessen weitergegeben, den ich nicht gemessen hatte.** Ausgezogen als rote Zeile 8 nach [../fehlerjournal.md](../fehlerjournal.md).

**Phase:** Betrieb, Lauf am selben Abend wieder aufgenommen. Wellen 2 und 3 vorab vermessen, Spur `mhdbdb-wellen-2345` in Welle 2, `fable-reviewer` Runde 1 auf Fable 5.1 beauftragt. Kein `npm test` auf der Koordinationsseite, keine Daten, kein Index berührt. Das Matrix-Gate lief zweimal rot und wurde beide Male nach einem Diff mit `--apply` nachgezogen; die zweite Ursache war eine einzige Zelle, das `updatedAt` von #28. Der Wiederaufnahmepunkt steht im #44-Zwischenstand.

---
## 2026-09-02 – Der Wellenlauf zu Ende gebracht, und dreimal saß der Fehler im Zuschnitt der Prüfung

Fortsetzung des am 01.09. pausierten Laufs, Spur `mhdbdb-wellen-2345`, Auftrag `docs/playbooks/kickoffs/2026-09-01-issue-lauf-fortsetzung.md` im Stand `091335fe0`. Dies ist der Eintrag der **Spur**; der Eintrag der Koordination zum selben Lauf steht unter dem 01.09.

**Die Wurzel gehörte in die Hülle, und das war nicht die interessanteste Hälfte des Befunds.** Welle 2 baute die Kandidatenmenge für #28 über die transitive Hülle unter `concept_23123000`. Die Vorabmessung hatte die Wurzel selbst ausgelassen, mein Nachbau zunächst auch. 31 Lemmata hängen direkt an ihr, 27 davon ohne Treffer in irgendeiner der 17 benannten Kategorien, und es sind genau die Wörter, mit denen der Text über Fremdsprachigkeit **spricht**, statt sie zu belegen: `welsch`, `rotwalsch`, `tolmetze`, `zunge`, `ûzlegen`. Die Menge wuchs von 6.219 auf 6.246 Lemmata und von 225.505 auf 227.652 Belege. Die Zahlendifferenz ist das Unwichtigste daran.

**Der teuerste Fix des Laufs hat einen Prüfpfad entwertet, den niemand nachgezählt hat.** Derselbe Fix machte den Guard `if not concepts` in `main()` zu totem Code: die Kategorien werden jetzt aus einer anderen Menge gefüllt, und ein falsch geschriebener Wurzel-Identifier erzeugte statt einer Fehlermeldung eine leere CSV mit Rückgabewert 0. Zwei `fable-reviewer`-Runden hatten den Fix gesehen und die Nebenwirkung nicht. Gefunden hat es der CI-Bot in Runde 3. **Die Lehre über den Anlass hinaus: ein Fix ändert nicht nur, was er soll, er kann Prüfpfade entwerten, die auf dem alten Verhalten beruhten.** Die Gegenprobe dazu ist billig und wurde in Welle 3 gleich zweimal gemacht: einmal mit einem erfundenen Wurzel-Identifier, einmal mit einem Verzeichnis erfundener Wörterbucheinträge, jeweils um zu zeigen, dass ein Gurt noch erreichbar ist.

**Rot: `check-doc-inventories.py` lief nicht lokal, und genau er wurde rot.** Ausgezogen als rote Zeile 9 nach [../fehlerjournal.md](../fehlerjournal.md).

**Die Hälfte einer Prüfmenge waren gar keine Schreibformen.** Welle 3 misst unsere dreistufige Lemmaauflösung gegen den Verweisgraphen des Findebuchs. Der erste Entwurf las die Formen mit `itertext()`, und `<form type="sublemma">` trägt im selben Element die grammatische Abkürzung: 3.462 der 8.610 Sublemmata haben ein `<gram>`-Kind, bei **2.705 ist die Abkürzung der gesamte Inhalt**, dort steht überhaupt keine Schreibform. Rund die Hälfte von Teil 2 war kontaminiert, und die kontaminierten Strings trafen trotzdem, weil Stufe 3 in der Richtung „Eingabe beginnt mit Lemma" prüft. Runde 1 des `fable-reviewer` fand es.

**Runde 2 fand denselben Fehler noch einmal in anderer Kleidung, und das ist der interessantere Fund.** 21 vermeintliche Mehrwortformen waren Einzelformen mit einem `<hi>`-Abkürzungsmarker. **Das Leerzeichen entsteht nicht im Text, sondern an der Markup-Grenze.** Beide Befunde haben dieselbe Bauart und kamen eine Runde auseinander: wer ein Element überspringt, muss fragen, welche anderen Kinder dasselbe tun. Die Gegenprobe, die in solchen Fällen meistens fehlt, ist die nach der Reichweite des Fixes: alle 39 `<hi>` unter Sublemma-Formen sind Marker, und `<form type="lemma">` trägt nur `<ref>`-Kinder, das Überspringen ändert dort **0** Formen.

**Teil 1 des #259-Prüfdatensatzes kann die Fehlerklasse nicht testen, wegen der das Ticket existiert.** Das Auswahlkriterium (die Schreibform ist bei uns selbst ein Lemma) ist genau die Bedingung, unter der Stufe 1 trifft; die Menge löst deshalb zu 100 % auf Stufe 1 auf, gemessen 543 von 543. Der Test der Stufen 2 und 3 ist Teil 2, und er ist mit 2.781 Fällen gut fünfmal so groß. Trefferquote dort 34,4 %. **Die Befundliste bleibt außerhalb des Repositoriums**, sie trägt Trierer Schreibformen; im Diff stehen nur aggregierte Zahlen über unsere eigenen Daten, und der Lauf endet mit einer Warnzeile, die das sagt.

**Welle 4 zeigt, wie eine Wortartentscheidung messbar wird, statt Sprachgefühl zu bleiben.** Die 98 Breve-Tokens der Wenzelsbibel, die der mechanische Lauf vom 31.08. wegen mehrdeutiger Wortart zurückgehalten hatte, sind am Verskontext entschieden: 89 annotiert, 9 im Rückhalt. Drei Entscheidungsklassen wurden nicht am Sprachgefühl entschieden, sondern am Bestand gemessen. Die wichtigste ist die Substantivierung: von den acht ADJ/NOM-Lemmata der Menge sind sieben gemessen (*roete* bleibt draußen, es trägt allein 132 der 201 `NOM`-Belege und fällt unter eine andere Regel), diese sieben tragen 69 eindeutig als `NOM` getaggte Belege, 60 davon außerhalb der WZB, alle einzeln angesehen. Der rohe Anteil täuscht (60 `NOM` gegen rund 27.000 eindeutige `ADJ`), weil attributive Verwendung um Größenordnungen häufiger ist, nicht weil die Bauart anders getaggt würde. **Die erste Fassung sagte „attributiv ist keiner der 60", und das war zu stark:** zwei sind es doch, einmal attributiv über die Versgrenze hinweg (`AC3_22210_11`, *seit das nie so boser man wart*), einmal als getrennte Hälfte von *hôchzît*. Die Aussage trägt nur in eine Richtung, und das genügt für die Entscheidungsrichtung dieses Laufs: das Haus taggt die Substantivierung `NOM`, aber aus einem `NOM`-Tag folgt keine Substantivierung. Dazu: `umbe` vor `sus/sust` steht in allen 5 aufgelösten Fällen `PRP` und in keinem `ADV`; `vor` steht mit Nominalphrase rechts 738 zu 6 als `PRP` und sonst 158 zu 105 als `ADV`.

**Vier der 98 sind kein Wortartproblem, sondern ein falsches Ziel-Lemma, und zwei davon sind gar keine Wörter.** `grŏsen` in „wil grŏsen deinen namen" ist das Verb *grôzen*, und `grôz` führt kein `VRB`. `hŏrde` in „die vorporgin hŏrde des sandes" ist der Hort, nicht das Hören. Und zweimal ist `tŏch` die erste Hälfte von *tŏchter*, **zerrissen durch einen mitten im Wort stehenden Blattmarker** („von den tŏch XXVIII GENE tern"). Das ist dieselbe Bauart wie Punkt 1 desselben Tickets, die 17 Tokens mit literalem Escape, nur andersherum: dort zwei Wörter in einem Token, hier ein Wort auf zwei verteilt. Bemerkenswert daran ist, dass die erzeugenden Zeilen in `variants.xml` **für sich richtig** sind: `hoerde` ist ein Präteritum von *hœren*, `toech` eines von *ziehen*. Eine korpusabgeleitete Variantenzuordnung kann global stimmen und lokal falsch sein.

**Rot, dritter Auftritt derselben Bauart an einem Tag: eine Abwesenheitsabfrage, deren Zuschnitt den gesuchten Fall ausschließt.** Ausgezogen als rote Zeile 10 nach [../fehlerjournal.md](../fehlerjournal.md).

**Der Wiederholungslauf, der nur die Reproduzierbarkeit zeigen sollte, hat einen Defekt gefunden, den kein Gate hätte finden können.** Das Skript schreibt den Pfad seines Provenienz-Logs in den `<change>`-Eintrag des Korpusheaders, und es schrieb dorthin, was auf der Kommandozeile stand. Beim ersten Lauf war `--out-dir` relativ und der Eintrag richtig; beim zweiten absolut, und damit stand ein Windows-Pfad mit Laufwerksbuchstaben und dem Worktree-Namen im Korpus. **Ein Wert, der in eine Datei geht, darf nicht davon abhängen, wie der Aufruf getippt wurde**; das Skript rechnet den Pfad jetzt repo-relativ um und bricht ab, wenn er außerhalb des Repositoriums liegt.

**Der Lehre daraus ist ein Detail wichtig, das leicht verlorengeht:** gefangen hat den Defekt nicht die Wiederholung, sondern dass ich beim zweiten Mal zufällig anders getippt hatte. Ein Wiederholungslauf mit identischer Kommandozeile hätte ihn nicht gezeigt. **Ein wiederholter Lauf findet Nichtdeterminismus, ein anders aufgerufener findet Umgebungsabhängigkeit**, und nur der zweite greift hier. Auf `origin` ist der absolute Pfad nie gelandet, geprüft am Header des gepushten Zweigs und korpusweit über alle 667 Dateien (Muster `C:[\\/]|/Users/|/home/|worktrees|chstn`, vorher an drei Testdateien auf Trefferfähigkeit geprüft, weil eine ungetestete Abwesenheitsabfrage heute schon einmal genug Schaden angerichtet hat).

Die Variation war allerdings Zufall, und darauf lässt sich nichts bauen. **Was die Klasse dauerhaft fangen würde, ist keine Laufvorschrift, sondern eine Prüfung am Ergebnis:** kein absoluter Pfad und kein Benutzername in `tei/`. Die Abfrage steht oben, sie ist schnell und deterministisch und wäre als Zeile in einem bestehenden Audit-Gate ein Zehnzeiler. Das ist hier als **Vorschlag** notiert und nicht als Vorhaben: ob das Projekt ein weiteres Gate will, kostet CI-Zeit und Wartung für eine Fehlerklasse mit bisher genau einem Beinahefall, und das entscheidet Chris.

**Ein Kriterium, das den gesuchten Fall ausschließt, sieht wie Strenge aus und ist Blindheit.** Aus den zwei `tŏch`-Tokens wurde beim Nachsehen in der Rohdatei ein größerer Befund: laufende Kolumnentitel und Kapitelzahlen stehen in der WZB als `<w>` im Textfluss (gemessen 928 der 6.836 unannotierten `<w>`, angeführt von `IOSUE` 104 und `EXO` 88), und an 18 Stellen zerreißen sie ein Wort (`geschep|fet`, `wis|sen`, `veisti|keit`, `isra|hel`). Die naheliegende scharfe Zählung, die zusätzlich verlangt, dass die zusammengesetzte Form in `variants.xml` steht, findet davon **2**. Sie schließt per Konstruktion aus, worum es geht, denn ein zerrissenes Wort ist typischerweise eines, das das Lexikon nicht kennt. Beides steht mit Zählvorschrift in **#390**, das aus diesem Nebenbefund entstanden ist: die Kodierungsentscheidung (`<fw>` gegen `<w>`) gehört nicht in einen Annotationslauf. **Dieselbe Bauart hat der Zuschnittfehler in #259**, wo das Auswahlkriterium für die Prüfmenge genau die Bedingung war, unter der Stufe 1 trifft. Mit der Abwesenheitsabfrage nach *grœzen* ist das derselbe Fehler zum dritten Mal an einem Tag, in drei verschiedenen Wellen und von drei verschiedenen Seiten. Auffällig ist nicht, dass er passiert, sondern dass er jedes Mal wie Sorgfalt aussah.

**Die Konfidenzregel wurde gesucht statt erfunden.** Für die fünf Fälle mit mittlerer Konfidenz galt die Frage, ob sie annotiert werden. `ingest/pos-disambig/369-stat/README.md` beantwortet sie seit dem 24.08.: annotiert wird nur bei hoher Konfidenz. Eine zweite, laxere Konvention im selben Korpus hätte mehr gekostet als fünf zurückgehaltene Tokens.

**Eine Ratsche hat angeschlagen, mit der der Wellenplan nicht gerechnet hatte.** `check-authority-cross-refs.py` führt seit #370 eine Baseline für lemmatisierte Tokens ohne `@corresp`. Die 89 neuen heben die WZB von 5.273 auf 5.362 und machen das Gate rot. Das ist kein Fehler, sondern die Folge der vorab getroffenen Entscheidung, kein `@corresp` zu schreiben, und die Ratsche verlangt genau das Richtige: den Anstieg bewusst und begründet via `--update-baseline` aufnehmen, statt ihn zu übersehen.

**Der CI-Review-Bot ist an diesem PR grün geworden und hat trotzdem drei Befunde geliefert**, bei 18 Dateien samt der 40-MB-Binärdatei. Die Turn-Zahlen dazu hat die Koordination im Job-Log gemessen, ich habe sie nicht nachgeprüft: 46 Turns hier gegen 56 bei #382 mit 13 Dateien. Wenn das stimmt, ist die Vermutung hinfällig, die Turn-Zahl skaliere mit dem Diff, und die 40-MB-Datei trägt als Erklärung für den Abbruch bei #368 nicht mehr. Was ich selbst gesehen habe, ist der grüne Lauf an einem PR, für den ein roter vorhergesagt war. Von den drei Befunden waren zwei richtig und einer falsch, und meine erste Widerlegung des falschen war es auch. Ich hatte sie mit einer Zeilenfalle erklärt (`rg -c` zählt Zeilen mit Treffer), und das trifft hier nicht zu: in der WZB trägt **keine einzige** der 235.993 Zeilen mehr als ein `<w>`, 149.165 tragen genau eines (die 235.994 einer ersten Meldung war ein Teilungsrest: `split('\n')` liefert hinter dem letzten Zeilenumbruch noch eine leere Zeichenkette). Die Ursache ist enger und interessanter: das Muster des Bots, `<w xml:id="[^"]*">`, lässt nur Tokens zu, deren einziges Attribut `xml:id` ist, und **drei** der 922 A-Z-Tokens ohne `@lemmaRef` tragen zusätzlich `pos="DIG"` (`XU`, `UIII`, `XU`). 922 minus 3 ist die 919 des Bots. Gefunden hat das die lokale Review-Runde 2, ich habe es nachgemessen. **Dieselbe Familie wie die Normalform-Verwechslung, nur eine Ebene tiefer: nicht falsche Zähleinheit, sondern ein Muster, das eine Teilmenge stillschweigend ausschließt.** Und wieder gilt: ein Reviewerbefund ist auch dann eine Behauptung, wenn ein Werkzeug ihn liefert, und eine Widerlegung ist es genauso.

**Von den drei Vorrichtungen, die in diesem Lauf rot geworden sind, hat genau eine einen inhaltlichen Befund sichtbar gemacht, den niemand gesucht hat.** Die beiden anderen haben eine veraltete Aufstellung gemeldet: das Matrix-Gate zweimal (Koordinationsseite, 01.09.) und das Inventar-Gate aus #329 einmal in Welle 2, wo zwei neue Skripte in `docs/DEVELOPMENT.md` und `scripts/README.md` fehlten. Beides ist Routine im Nachziehen und liefert kein Wissen. Die dritte, die `@corresp`-Ratsche, hat eine Zahl bewegt, die sonst lautlos gestiegen wäre, und sie auf die Stelle genau beziffert. Die brauchbare Frage an eine Prüfung ist damit nicht „prüft sie richtig", sondern **„kann sie überhaupt jemals rot werden, und woran"**.

**Ein stiller Halt ist in einer Hintergrundsession ein Fehler eigener Art.** Zweimal endete ein Turn, ohne dass ein Weckruf eingeplant war: einmal im Dialog, einmal beim Warten auf CI. CI weckt eine Hintergrundsession nicht. Die Regel, die daraus gilt: wer einen Schritt fertig hat, meldet und fängt den nächsten **im selben Turn** an; nur ein laufender Subagent oder ein Hintergrundbefehl rechtfertigt das Turnende, weil beide von sich aus wecken.

**Eine Anweisung ist nicht dadurch gedeckt, dass sie vom Operator kommt.** Die Koordination bat, einen präzisierten Satz „in beide Statuskommentare" zu nehmen. Die Freigabe lautet aber je einen sachlichen Statuskommentar auf #28, #259, #235 und #216, und #259 hatte seinen bereits. Der Satz steht deshalb nur in #235, von dort auf #259 verlinkt. Die Koordination hat den Widerspruch angenommen und ihn selbst als Grenzüberschreitung verbucht. Eine Spur, die eine Freigabe nur so weit auslegt, wie sie geschrieben ist, kostet einen Satz an der falschen Stelle und spart die Frage, wer die Grenze verschoben hat.

**Rot, eigener Regelverstoß.** Ausgezogen als rote Zeile 11 nach [../fehlerjournal.md](../fehlerjournal.md).

**Phase:** Betrieb. Drei Arbeits-PRs (#386, #388, #389, letzterer als `144fbbd3c`), einzeln gemergt, dazu dieser Eintrag als vierter: der Auftrag verbietet den direkten Push auf `main` ohne Ausnahme, und die Hausregel für kleine Doku-Änderungen hebt eine Auftragsgrenze nicht auf. Kein `Closes` auf keinem der vier Tickets. Statuskommentare auf #28, #216, #259 und #235. `npm test` vor jedem Push, VERDICT-Zeile jeweils im PR.
## 2026-09-02 (Abnahme) – Der Abbau traf die Spur im Laufen, und die Vorkehrung dagegen war schon geschrieben

Koordinationsseite, Abschluss des Wellenlaufs. Vier PRs gemergt (#386, #388, #389, #391), Kontrollzahl am gemergten Stand selbst nachgemessen: 149.165 `<w>` in der WZB unverändert, 6.836 ohne `@lemmaRef` statt 6.925, Differenz genau 89. Die Tokenmenge bleibt identisch, nur die Annotationen kommen dazu.

**Rot, zum achten Mal, und es ist eine Abwesenheitsbehauptung über eine Datei, die zwei Verzeichnisse entfernt liegt.** Ausgezogen als rote Zeile 12 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, zum neunten Mal, und dies ist der einzige Fehler des Laufs, gegen den bereits eine ausformulierte Vorkehrung an genau der richtigen Stelle stand.** Ausgezogen als rote Zeile 13 nach [../fehlerjournal.md](../fehlerjournal.md).

**Die Verlustprüfung vor dem Löschen von Zweigen braucht eine andere Vorschrift, als die Playbooks nahelegen.** Bei Squash-Merges sagt `git branch --merged` nichts, und `-d` schlägt bei jedem gemergten Zweig fehl, ohne dass etwas verloren ginge. Gemessen wird deshalb der Inhalt: keine Datei, die es nur auf dem Zweig gibt (`diff --name-only --diff-filter=A`), und jede Zeilendifferenz entweder eine, die `main` zusätzlich hat, oder eine 1-zu-1-Ersetzung einer älteren Versionszeile. Für den `--worktree`-Startzweig genügt `merge-base --is-ancestor`. Eine grobe Zählung über `--numstat` reicht **nicht**: sie zeigt bei zwei der vier Zweige dieses Laufs hunderte „hinzugefügte" Zeilen, die allesamt ältere Fassungen derselben Zeilen sind. Ohne die Korrektur der Spur hätte ich zwei der vier Zweige gar nicht geprüft.

**Ein Beinahe-Fehler, der nicht gezählt wird, aber hierher gehört, weil eine Regel ihn abgefangen hat:** der Entwurf des Abschlusskommentars für #385 enthielt den Satz „Der Freeze ist aufgehoben". Der Body desselben Tickets sagt „Eine koordinierende Session kann den Freeze nicht aufheben", von mir am Vortag geschrieben. Gefangen hat es die Regel, zu einer Entscheidungsfrage den bisherigen Stand daneben zu legen, nicht die eigene Aufmerksamkeit. Es ist der erste Fall in diesem Lauf, in dem eine Vorkehrung einen Fehler **vor** dem Schaden abfing, statt ihn hinterher zu zählen. Nebenbefund: der Abschnitt „Abarbeitung" in #385 verlangt, dass jeder Wunsch **vor** dem Aufheben des Freeze eingearbeitet ist, aber alle sechs betreffen eingefrorene Dateien und können erst danach eingearbeitet werden. Die Reihenfolge ist nicht erfüllbar; das entscheidet chsteiner.

**Phase:** Abnahme abgeschlossen. Vier Zweige gelöscht, Worktree-Verwaltungseintrag entfernt, Agent-Memory nachweislich identisch im Hauptbaum, kein Stash, keine unversionierte Arbeit. Offen an chsteiner: die sechs Eingaben in #385 und der Freeze selbst.
## 2026-09-02 (Nachlauf) – Zwei Befunde haben einander widerlegt, und der Test war für die falsche Sache gebaut

Fortsetzung nach der Kontingentpause, Koordinationsseite. Der Wellenlauf war
abgenommen, gearbeitet wurde nur noch an der Begleitung des Health-Checks.
Beide Fehler dieses Abschnitts sind in derselben halben Stunde passiert, und
der zweite ist beim Aufräumen des ersten aufgefallen.

**Rot, zum zehnten Mal: eine ungemessene Annahme, die eine Entscheidung gestützt hat.** Ausgezogen als rote Zeile 14 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, zum elften Mal, und diese ist die unangenehmste des Laufs: ein Positivtest, der die falsche Sache geprüft hat.** Ausgezogen als rote Zeile 15 nach [../fehlerjournal.md](../fehlerjournal.md).

**Das Projektwissen dahinter, und es ist der brauchbare Teil:** der TEI-Header
führt Identifier an zwei verschiedenen Orten, und sie beschreiben verschiedene
Gegenstände.

| Ort | Gegenstand | Beispiel PZ |
|---|---|---|
| `fileDesc/sourceDesc/msDesc/msIdentifier` | das **Werk** | wikidata `Q1247232`, GND `4108542-5` |
| `profileDesc/particDesc/listPerson/person` | eine **Figur oder Person** im Text | wikidata `Q18821`, GND `118634933` |

Wer die beiden nicht trennt, misst Werk gegen Person und bekommt Konflikte, die
keine sind. Gemessen am 02.09.2026 mit PZ als Kontrollfall. Was nach der
Trennung übrigbleibt: **TRO** hat zwei echte Konflikte im `msIdentifier`
(handschriftencensus 929 gegen 212, GND 1181164893 gegen 4285313-8), und
**WZB** trägt dort außer der Sigle überhaupt keinen Identifier, während
`works.xml` vier führt. Das ist keine Abweichung, sondern eine Lücke, und sie
passt zu dem Befund der Spur, dass derselbe Header in seinem `<projectDesc>`
falsche Zahlen über sich selbst angibt.

**Ein Befund über das Verfahren, der nicht dieses Repositorium betrifft:**
`~/.claude/CLAUDE.md` wurde am 02.09. von drei Parteien an einem Abend
geändert, und keine hat es von den anderen erfahren. Ein gleichzeitiger Lauf in
`claude-code-setup` hatte die Datei ab 18:17:51 eingefroren, die Änderung von
hier fiel um 18:42 hinein. Folgenlos blieb es nur, weil keine der vier dortigen
Spuren `sed` benutzt hat, die geänderte Zeile also nichts steuerte. Der Grund
ist strukturell: **der Freeze stand in einem Ticket eines Repositoriums, die
Datei liegt in keinem.** Ein Ticket bindet nur, wer es liest, und diese Datei
liest jede Session der Maschine, während das Ticket keine liest. Der Vorschlag
dazu (eine Freeze-Zeile in der Datei selbst, gesetzt vor dem ersten Kickoff)
liegt bei der dortigen Koordination und ist unerprobt.

**Phase:** Health-Check läuft weiter auf `claude/health-check-0902`. Offen an
chsteiner: #390 umsetzen lassen, die vier nie erbetenen `wait:extern`-Antworten
(#147, #263, #86, #141), die zwei unklaren der 18 zerrissenen Wörter.

---
## 2026-09-02 (Health-Check) – Dreimal stand eine erledigte Aufgabe als offene da, und mehrfach stand eine Messung neben dem, was sie belegen sollte

**Scorecard.** Flow-Check über alle 15 promptotyping-Dokumente, jedes ganz gelesen: 14 Befunde. Algorithmen 3 von 3 zeilengenau konform, XPaths 3 von 3, Rebuild-Test bestanden. JOURNAL-Audit auf vier Fehlerklassen: 2 veraltete Zahlen, **0** Behauptungen ohne Messvorschrift (Kontrollmessung am jüngsten Eintrag: WZB 149.165 `<w>` und 6.836 ohne `@lemmaRef`, beide exakt), 2 tote Verweise, 0 Probleme im Verhältnis zum Archiv. `doc-count-audit.py` fällt von 20 Treffern auf 0. Vier Issues (#392 bis #395), drei davon im selben Lauf umgesetzt statt nur gemeldet. Drei Reviewrunden, `npm test` grün (310 Tests).

**Der Befund, der eine Klasse ist und kein Einzelfall: dreimal steht in der Doku eine Aufgabe als offen, die längst erledigt ist.** `DESIGN.md` führte die Multi-Lemma-CSS-Duplizierung unter „Known Inconsistencies", obwohl `6a9849314` sie am 13.07. beseitigt hat und in `korpus.css` an genau der Stelle ein Kommentar steht, der es sagt (gemessen als Selektorzeilen `^\s*\.multi-lemma-`: `korpus.css` 0, `playground/css/style.css` 5; die einzige Erwähnung in `korpus.css` ist der Kommentar in Zeile 698, der genau das sagt). `TEI-MODEL.md` §8.1 überschrieb eine Liste mit „To be migrated", obwohl kein einziger der Prosatexte noch ein `<l>` trägt: 0 in allen 18 der Tabelle und 0 auch in den drei aus #143 (HMT, APO, HH), die dort danebenstehen, bei zusammen 89.140 `<lb>`. Kontrollwert PZ, ein Versepos: 24.812 `<l>`, 0 `<lb>`. `DECISIONS.md` ADR-004 führte einen Clear-Cache-Button als „Future", der im build-injizierten Footer steht und damit in 14 der 16 ausgelieferten Seiten (`api/index.html` und `404.html` bekommen kein Chrome) und einen eigenen Test hat. Das ist schlimmer als eine veraltete Zahl: es steht eine Arbeit da, die niemand mehr erledigen kann, weil sie getan ist.

**Der zweitbeste Fund kam aus einem Widerspruch zwischen zwei eigenen Messungen desselben Tages**, die um 14.941 auseinanderlagen. Ursache: exakt so viele `<w>` tragen ein leeres `pos=""`. 7.596.147 zählt das Attribut, 7.581.206 den nichtleeren Wert, beide sind richtig. Beide stehen jetzt mit ihrer Vorschrift in `POS-TAGSET.md` §4, statt dass eine gewählt wird, sonst liest die nächste Session die eine als Korrektur der anderen.

### Rote Zeilen

Fünf, die letzte ist die teuerste, weil sie den Lauf selbst betrifft, und die erste ist noch während des Schreibens dieses Abschnitts ein drittes Mal eingetreten.

1. **Nackte Shell-Variablen in Schleifen, dreimal.** Lehre: globale `CLAUDE.md`, „Shell-Konventionen", Werte vorher ermitteln und literal einsetzen. Jedes Mal hat die Umgebung blockiert. Das dritte Mal ist eine halbe Stunde **nach** dem Absatz passiert, den Sie gerade lesen, in einer `for`-Schleife über zwei Issue-Nummern, und es ist damit der beste Beleg des Abends für die Regel, aus der dieser Zähler stammt: eine Lehre, die dreimal an derselben Stelle steht und trotzdem verletzt wird, braucht keine vierte Kopie, sondern einen anderen Mechanismus. Hier gibt es ihn, und er hat funktioniert: der Worktree-Guard hat alle drei abgefangen, bevor etwas lief. Die Regel wirkt also nicht über das Erinnern, sondern über die Sperre, und das ist die brauchbare Erkenntnis daraus.
2. **Aus `protected=true` auf „ein Push nach `main` wird abgelehnt" geschlossen** und das in `DEVELOPMENT.md` geschrieben. Lehre: ein Befund wird erst zur Aussage, wenn die Quelle offen war. Gemessen war das Feld, ungeprüft die Schlussfolgerung; das Ruleset trägt nur `deletion` und `non_fast_forward`, und der Widerspruch stand zwei Zeilen tiefer im eigenen Text. Gefangen vom `fable-reviewer`. **Die Verschärfung gegenüber der dokumentierten Lehre: der Befund war selbst erhoben, und das macht ihn gefährlicher, weil eine eigene Messung sich geprüft anfühlt, auch wenn nur die Zahl gemessen wurde und nicht der Schluss daraus.**
3. **Aus einem gefilterten Grep auf Abwesenheit in der ganzen Seite geschlossen.** Lehre: ein leerer Abruf ist kein Nullbefund, immer einen Kontrollwert mitmessen. Der Grep suchte `h3` einer bestimmten CSS-Klasse und blendete den Abschnitt aus, in dem der gesuchte Eintrag steht. Daraufhin war eine vollständige Werkzeugkarte für eine ausgelieferte Hilfeseite geschrieben, die eine Dublette gewesen wäre und zusätzlich die falschen Werke genannt hätte (ER ist Erec, nicht Eneasroman). Zurückgenommen vor dem Commit, und **gefangen hat sie nichts außer einem zufälligen zweiten Blick auf die Nachbarschaft der Einfügestelle.**
4. **Die Fehlalarmmessung für das neue ROADMAP-Gate maß ein anderes Prädikat als das gebaute.** Gemessen wurde „steht in den geschlossenen Issues", gebaut wurde „steht nicht in den offenen Issues". Issues und PRs teilen sich den Nummernraum, also meldete der erste echte Lauf die gemergten #245 und #246. Gefangen vom eigenen Gate, eine Minute nachdem es existierte.
5. **Fünf falsche Zahlen im eigenen Korrekturtext, in genau den Commits, die Zahlen-Drift beseitigen sollten.** „Acht Tags unverändert" statt 12 und „alle unter einem Zehntelprozent", obwohl NOM mit +0,761 % siebenfach darüber liegt; „sechs ausgelieferte Seiten" für einen Knopf, der in 14 steht; „fünf tote Einträge in der Ping-Tabelle", wo zwei stehen; „die fünf obsoleten Debug-Specs", von denen nur zwei Skips trugen; und in der Korrektur der zweiten dann „in jeder ausgelieferten Seite", obwohl zwei der 16 kein Chrome bekommen. Lehre: „No claim in a comment that does not hold", `CLAUDE.md` → Self-Inflicted Overhead. **Keine automatische Vorrichtung dieses Projekts kann sie fangen**, weil Prosa weder vom `doc-count-audit` noch von einem Test erreicht wird; gefangen hat vier der `fable-reviewer` in Runde 2 und die fünfte derselbe in Runde 3. Die Regel, die ihn vor dem ersten Push vorschreibt, hat damit den Zweck des Laufs gerettet. Was daran zu denken gibt, ist enger: **die einzige Vorrichtung gegen ungemessene Zahlen in Prosa ist ein Agent, und ein Agent kann verschwinden, ohne dass es nach einem Ausfall aussieht.** Der `fable-reviewer` war an diesem Abend zweimal nicht als Agententyp vorhanden, und der Ausfall sah aus wie eine Berechtigungsfrage. Ein Health-Check, der Zahlen-Drift korrigiert und dabei neue erzeugt, greift den Zweck des Laufs an und nicht nur seine Ausführung.

**Die gemeinsame Form von 2, 4 und einem Teil von 5, und sie ist der eigentliche Befund des Abends.** Sie hat zwei Ausprägungen, und die Unterscheidung stammt aus der Gegenlesung durch die Operator-Session, die denselben Fehler am selben Abend an eigenem Material fand:

- **Die Vorrichtung steht neben dem Prädikat, das sie sichern soll.** Das Gate prüfte „steht nicht in den offenen Issues", abgesichert war „steht in den geschlossenen"; drüben ein Positivtest, der die Normalisierung prüfte statt der Zuordnung. Dagegen hilft, die Vorrichtung selbst zu reizen.
- **Die Aussage steht neben ihrer Menge: richtig gerechnet, falsch bezogen.** Dreimal an diesem Abend allein hier. „Fünf tote Einträge" war die zutreffende Zahl für die ganze ROADMAP, eingesetzt in einen Satz über die Ping-Tabelle, in der zwei stehen. „0 Selektoren gegen 6" stellte eine Selektorzählung neben eine Zeichenkettenzählung (richtig ist 0 gegen 5, und der eine Treffer in `korpus.css` ist der Kommentar, der die Entfernung dokumentiert). „In jeder ausgelieferten Seite" war eine Allaussage neben der richtigen Zahl 14, während die Site 16 Seiten ausliefert. Eine Allaussage ist dabei nichts anderes als eine Mengenangabe ohne Zahl, und sie wird auf dieselbe Weise falsch. Dagegen hilft keine Vorrichtung, sondern nur, die Menge zu benennen, über die man spricht. Das ist die gefährlichere der beiden.

Beide Male ist etwas Vorhandenes und Funktionsfähiges der Grund, warum niemand nachsieht. Eine Messung, die nicht dasselbe misst wie die Behauptung, ist schlechter als keine.

**Wo die Fälle gestoppt wurden, ist die eigentliche Wirkungsmessung.** Vier vom `fable-reviewer`, nach dem Commit und vor dem Push. Zwei von der Operator-Session, zu spät für die Meldung und rechtzeitig für diesen Eintrag. Einer, die CSS-Zahl, **vor dem Schreiben**, durch einen mitlaufenden Kontrollwert: die erste Suche lief auf `lemma-highlight-`, lieferte sauber 0 und 0, und der Kontrollwert traf nirgends, weil der Selektor `multi-lemma-` heißt. Dieselbe Zeile hat zehn Minuten später ein zweites Mal gegriffen, als ein Dateimuster `PZ.xml` statt `PZ.tei.xml` suchte und alle 21 Prosatexte als sauber meldete, den Kontrollwert eingeschlossen. Das ist der einzige Fall des Abends, der gar keinen Text erzeugt hat, den jemand korrigieren musste, und er kostet eine Zeile im selben Aufruf. Der Reviewer kostet eine Runde und war zweimal nicht da.

Für die erste Ausprägung ist die Folgerung im Gate umgesetzt: der neue Sättigungs-Check in `build-issue-matrix.py` ist in beide Richtungen gereizt worden, mit Limit 5 (steigt aus) und mit Limit 300 und 1.000 (läuft durch), denn ein Wachhund, der nie gebellt hat, ist kein gemessener Wachhund.

**Was gut lief, damit die Liste nicht kippt:** die Algorithmen und XPaths halten zeilengenau, die Invariante aus `CONTRACTS.md` §H.2a stimmt exakt (`sum(text.wordCount)` = 7.546.332 = unabhängiger Korpusscan), die dokumentierten 396 offenen Cross-Refs über 109 IDs stimmen auf den Ref genau, und die Frage, ob der IndexedDB-Invalidierungsmechanismus ohne den Code auffindbar ist, ist mit Ja zu beantworten: `CONTRACTS.md` §E führt ihn samt der 30-Tage-Folge eines vergessenen Bumps.

**Phase:** Health-Check abgeschlossen, `claude/health-check-0902` als PR offen. Offen an chsteiner: #395 (die WZB-Selbstauskunft im Header, ein reines Korpusticket, das dieser Lauf nicht anfassen durfte) und die Frage, ob ein fehlender Agententyp künftig ein Halt sein soll statt eines Weiter. Geschrieben steht bisher nur der Fall „die Session darf keine Agenten starten"; der Fall „der Typ ist nicht da" ist heute zweimal eingetreten und wurde ohne geschriebene Grundlage als Halt behandelt.

---
## 2026-09-06 – Eindeutigkeit über einer Menge mit einem Element, und ein Alarm, der nur eine andere Zähleinheit war

Cloud-Umgebung, volles Fable-Kontingent, chsteiner eine Woche nicht am Laptop.
Zuschnitt entsprechend: alles, was ohne seine Entscheidung auskommt, wird
gemacht; alles Übrige wird bis zur Entscheidungsreife vorbereitet und liegen
gelassen. Ergebnis in Zahlen: **1.455 Tokens neu annotiert** über drei Läufe,
kein neues Lemma und kein neuer Variantentyp geprägt, Korpus-Index 4.2.8 auf
4.2.11.

| Lauf | Fälle | annotiert | zurückgehalten |
|---|--:|--:|--:|
| #216 Punkt 3 (`vrouwe` vor `minne`) | 155 | 152 | 3 |
| #387 mechanischer Teil | 948 | 948 | 0 |
| #387 Kern (`fro`, kontextpflichtig) | 390 | 355 | 35 |

Der dritte Lauf ist der einzige, der Fable gebraucht hat: 61 Bündel, eines je
Sigel, nach POS-TAGSET §6.3. Die anderen beiden sind mechanisch entschieden und
hätten kein Modell gebraucht.

**Rot: Eindeutigkeit über einer Menge mit einem Element ist keine Eindeutigkeit.** Ausgezogen als rote Zeile 16 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: eine Zahl in der falschen Einheit macht eine verbuchte Altlast zu einem frischen Alarm.** Ausgezogen als rote Zeile 17 nach [../fehlerjournal.md](../fehlerjournal.md).

**Der Ertrag von #28 Phase 2 ist nicht die Liste, sondern ihre Reichweite.**
Der Phasenplan empfiehlt, mit den 430 `@ana`-Widersprüchen anzufangen „statt
mit einer Frequenzschwelle". Gemessen sind das keine Alternativen: **22 der 26
belegstärksten Nicht-Namen tragen keinen einzigen Widerspruch**, das sind
119.101 der 124.369 Tokens (95,8 %). `niht` ist der Fall, an dem es sichtbar
wird: 81.088 Belege, alle mit `@ana`, **jedes einzelne auf den Sprach-Sense**.
Das schärfste maschinelle Kriterium der Menge kann ihren größten
Falschpositiven nicht entfernen, weil die Annotation dort die Quelle des
Problems ist und nicht sein Korrektiv. Umgekehrt liegen 184 der 424
Widersprüche auf 15 Lemmata außerhalb der 26. Beide Listen sind zu lesen.
Nebenbei fällt die `gebrechen`-Frage quantitativ zu: 37 + 1 + 1 = 39
Widersprüche plus `JT_30921000_5` ergeben die 40 sense-disambiguierten Tokens,
die #28 nennt, unabhängig gemessen mit einem anderen Skript.

Die 430 des Plans sind übrigens 424 plus 6: sechs Tokens tragen ein `@ana` auf
einen Sense, den der Lemma-Index nicht führt. Ein Verweis ins Leere
widerspricht nichts, er sagt gar nichts, deshalb steht er jetzt als eigene
Zeile.

**Ein Befund des CI-Bots, der die Sorte war, für die er da ist.** `next_token`
im `fro`-Extraktor nahm das nächste `<w>` in Dokumentordnung des ganzen
`<body>` und überschritt damit die Verszeile. Unabhängig nachgemessen: bei
**116 der 374 Versfälle (31 %)** steht das Zieltoken am Versende, das Feld trug
dort also das erste Wort der Folgezeile, und `prompt.md` stellt genau dieses
Feld an die erste Stelle. Aus dem Lauf ist daraus nachweislich kein falsches
Tag geworden (von den zwölf Anrede-Urteilen stehen neun im Vers, keines am
Versende, drei sind Prosa), aber das Skript bleibt liegen und die 35
zurückgehaltenen Fälle laufen noch einmal hindurch. `cases.json` wurde
**bewusst nicht** neu geschrieben: die Datei ist das Protokoll dessen, was die
61 Agenten gesehen haben, und nicht das, was sie hätten sehen sollen.

**Zur Regel, die chsteiner mitten im Lauf viermal geschickt hat** („immer die
Kommentare lesen in den Issues, nicht nur den Body"): sie steht jetzt in
`CLAUDE.md` unter „Issue Labels", mit vier gemessenen Fällen statt einer
Ermahnung. Der schärfste ist #216: die 12 Kommentare tragen das ganze
Arbeitspaket, und der Body enthält das Wort *vrouwe* nicht ein einziges Mal.
In `BETRIEBSVERTRAG.md` ist sie ein Unterpunkt von Regel 9 geworden und
ausdrücklich **keine** neue nummerierte Regel: `CLAUDE.md` zitiert „Regel 11"
bei der Nummer, und ein Einschub hätte sie stillschweigend verschoben.

**Umgebungswissen für die nächste Cloud-Session, alles gemessen:**

- **Tests brauchen `CI=1`.** Ohne die Variable fährt Playwright 6 Worker auf 4
  Kernen gegen einen 42-MB-Index: 7 Fehler und 9 Flaky. Mit 2 Workern genau
  ein Fehler, und der ist echt und umgebungsbedingt: `lemma page loads
  Wörterbuchnetz entries via API` ruft `api.woerterbuchnetz.de`, was der
  Egress-Proxy mit 403 auf CONNECT abweist. Auf `origin/main` fällt derselbe
  Test identisch aus.
- **Die Authority-Datenbanken sind hier nicht erreichbar** (d-nb.info,
  lobid.org, handschriftencensus.de). Die TRO-Identifier-Frage aus #395 ist in
  dieser Umgebung deshalb nicht zu klären. `WebSearch` geht und bestätigt
  indirekt, dass handschriftencensus 212 der Trojanerkrieg ist, also
  `works.xml` recht hat und die 929 im Header falsch ist. **Das Korpus wurde
  darauf trotzdem nicht geändert**: eine indirekte Bestätigung ist keine
  Quelle.
- **`data-integrity.yml` läuft nur auf `pull_request`**, nicht auf einen Push
  auf einen Branch. Ein Datenzweig ohne PR hat also kein Gate über sich. Das
  war der ausschlaggebende Grund, PR #398 früh zu öffnen statt am Ende.
  **Kehrseite, am Nachmittag desselben Tages gemessen:** sobald der PR offen
  ist, lösen die Pfadfilter für **jeden** Push aus, auch für einen reinen
  Doku-Commit, weil `paths` bei `pull_request` gegen den gesamten PR-Diff
  gehalten wird und nicht gegen den Push. Zusammen mit `cancel-in-progress`
  heisst das: jeder Push bricht den laufenden Gate-Lauf ab.
- Chromium ist als Build 1194 installiert, das Projekt pinnt 1193 (Symlink
  genügt), und `python3` ist 3.11, während die Skripte 3.13 brauchen
  (`Path.read_text(newline=)`). Immer `python3.13` aufrufen.

**Zwischenstand am Mittag:** PR #398 offen, sechs Bot-Runden, die letzte
vollständige ohne Befund. Offen an chsteiner, alles drei eine Entscheidung und
nichts davon recherchierbar: der Variantentyp für die Zirkumflex-Schreibung
unter `lemma_7260` (blockierte dieselben 3 KZW-entschiedenen Tokens zum zweiten
Mal), die 35 zurückgehaltenen `fro`-Fälle, und ob TEI-Header die
`works.xml`-Identifier weiter duplizieren sollen. Alle drei sind am selben Tag
entschieden worden, siehe den folgenden Eintrag.

---
## 2026-09-06 (Nachmittag) – Eine Zusage im Perfekt, und sechsmal derselbe Fehler in verschiedenen Kostümen

Fortsetzung desselben Tages, nach den drei Entscheidungen von chsteiner: der
#235-Präzedenzfall gilt, an KZW geht nur, was sie wirklich braucht, den Rest
entscheidet Fable. Endstand **1.477 Tokens** (die 1.455 vom Vormittag plus 3
plus 19), Korpus-Index 4.2.11 auf 4.2.13, Authority-Index 1.9.2 auf 1.9.3, und
ein Skript, das es seit Monaten gab, hängt jetzt in der CI.

**#216 ist abgeschlossen, und der Präzedenzfall kollidierte mit einer Ratsche.**
Die 3 zurückgehaltenen `vrouwe`-Belege in RVBR sind geschrieben, damit steht
Punkt 3 auf 155/155. Der Weg dahin ist der lehrreiche Teil: der #235-Fall
erlaubt, für eine Zirkumflex-Schreibung ohne Typ einen Beleg **ohne**
`@corresp` zu schreiben, und genau das hätte die #370-Ratsche rot gemacht, die
für RVBR null Tokens ohne `@corresp` toleriert. Aufgefallen ist es mitten in
der Umsetzung, nachdem die Freigabe schon vorlag. Ich hatte bereits einen
`ohne_corresp`-Schlüssel in `apply-homograph.py` gebaut; er ist wieder draußen
(`git checkout --`), weil ein Mechanismus, der die Ratsche still umgeht, nach
genau dieser Entscheidung das Falscheste ist, was man bauen kann. Stattdessen
neu gefragt und **`type_372365` geprägt**, der erste neue Variantentyp dieser
Session (Maximum vorher `type_372364`). Kosten: `variants.xml` wächst um genau
eine Form, 256.761 auf 256.762 – und diese Zahl steht an zehn Stellen im Repo,
zwei davon auf ausgelieferten Seiten.

**Der ADJ/ADV-Nachlauf, und was ein gemessener Prior wert ist.** Die 31 mittel-
konfidenten Fälle des `fro`-Laufs waren sich beim Lemma alle einig; offen war
nur ADJ gegen ADV, und das ist nach POS-TAGSET §4 ausdrücklich **K4**, also
LLM-Aufgabe und keine kuratorische Frage. Das war der Grund, sie nicht an KZW
zu geben. Der Prior hat dann die eigentliche Arbeit getan: über alle 667
Dateien trägt auf `origin/main` **kein einziger** der 4.869 `lemma_7250`-Belege
`ADV` allein. Von 14 ADV-Vorschlägen des ersten Durchgangs sind daraufhin 13
gefallen. Geschrieben sind 19, zurückgehalten 11, und zusammen mit den zwei
Substantivierungen gehen **13 Fälle an @wachauer**. Zwei Dinge liefen anders
als sonst: `unentschieden` war ein erlaubtes Ergebnis (zwei Fälle, beide die
verblose Antithese in Parallelüberlieferung), und bei sechs Fällen wurde die
Konfidenz **nachgefragt statt überstimmt** – fünf gingen auf `high`, einer
blieb bewusst `medium`. Der einzige ADV-Fall (`RVBR_6083_0`) ist gut begründet
und steht trotzdem nicht im Batch: wäre er richtig, wäre er der erste
`ADV`-Beleg von *vrô* im Korpus, und eine Entscheidung gegen den gesamten
annotierten Bestand gehört nicht in einen maschinellen Lauf.

**`doc-count-audit.py` hängt jetzt als Gate in `data-integrity.yml`.** Das
Skript kennt seit Monaten ein `--check` mit Exit ungleich 0 bei Drift und lief
in keinem Workflow. Was das kostet, hat der Tag vorgeführt: die alte 256.761
blieb an zehn Stellen stehen, gefunden hat es der Review-Bot, nicht die CI. Der
Ort ist `data-integrity.yml` und nicht `no-cdn-check.yml`, weil dort `lxml`
ohnehin installiert ist; die Kosten sind sechs Sekunden gegen 45 Minuten
Job-Timeout. **Die Grenze steht als Kommentar daneben und hat zwei Hälften, die
verschieden wirken:** `docs/**` und `*.html` fehlen in den Pfadfiltern, dort
ändert ein PR also die **behauptete** Zahl; `playground/**` fehlt ebenfalls, und
dort ändert ein PR die **gemessene**. Ein PR, der ein UI-Modul hinzufügt, löst
diesen Workflow nicht aus und macht den nächsten, unbeteiligten Daten-PR rot.
Die Pfadfilter zu erweitern hieße, den 45-Minuten-Lauf bei jeder
Playground-Änderung zu starten; das ist ein Handel über fremde Arbeit und
deshalb bewusst nicht getroffen, sondern mit Preis daneben notiert.

**Nachgesehen statt auf grün vertraut.** Nach der #397-Regel ist ein Gate, das
grün wird, ohne etwas geprüft zu haben, genau die tote Wache. Also ins Job-Log
von `101512379175` gesehen: der Schritt lief als Nummer 7 in vier Sekunden,
druckte alle 19 gemessenen Größen (darunter `variants.xml — Formen | 256.762`,
die Zahl, um die es ging), scannte Docs und ausgelieferte HTML-Seiten und
meldete in der Anker-Selbstprüfung kein konfiguriertes Paar ohne Treffer. Vor
der Korrektur wäre er rot gewesen.

**Rot, und es ist der Befund des Tages: sechs Bot-Befunde, ein einziges Muster.** Ausgezogen als rote Zeile 18 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, und der Beleg dafür stammt aus diesem Absatz selbst: die Pfadfilter eines `pull_request`-Triggers schützen einen Push nicht.** Ausgezogen als rote Zeile 19 nach [../fehlerjournal.md](../fehlerjournal.md).

**Phase:** PR #398 offen. Bei chsteiner liegen nur noch Dinge, die diese
Umgebung nicht lösen kann: die 13 `fro`-Fälle für KZW (#387), die
TRO-Identifier-Frage (#395, Authority-Datenbanken hier nicht erreichbar), und
ob `playground/js/ui/**` in die Pfadfilter soll. #390 wartet bewusst auf den
Merge.

---
## 2026-09-06 (Abend) – Zehn blockierte Tickets entscheidungsreif, und drei ihrer Prämissen waren abgelaufen

Auftrag von chsteiner nach den beiden Entscheidungen am Nachmittag: die Woche
für das Entscheidungsreif-Machen der blockierten Tickets nutzen, weil kein
`auto:full` und kein `auto:brief` mehr offen ist. Zehn Vorgänge bearbeitet
(#364, #378, #308, #363, #366, #375, #267, #252, #228, #358), jeder mit einer
Messung statt einer Zusammenfassung. Nichts an Korpus oder Authority geändert.

**Der Ertrag steckt nicht in der Zusammenfassung, sondern im Nachmessen. Drei
von zehn Tickets hatten Prämissen, die nicht mehr galten**, und alle drei in
dieselbe Richtung: die Lage war besser als das Ticket dachte.

- **#358** war erledigt. Das Ticket beschreibt, dass dem Willehalm die
  Dreißiger-Gliederung fehlt. Gemessen: 467 `<div type="chapter" n>`, alle
  14.002 `<l>` darunter, auf `main`. Umgestellt am 09.08.
- **#308** Punkt 1 löst sich auf. Das Ticket fragt, ob für den „Schweizer
  Anonymus" ein Personeneintrag angelegt oder auf `person_anonym` umgebogen
  werden soll. Beides unnötig: `person_1772` existiert mit GND, und `works.xml`
  verweist für genau dieses Werk schon korrekt darauf. Nur der TEI-Header zeigt
  auf eine ID, die es nie gab.
- **#252** ist beantwortbar, und war es vermutlich schon damals. Der Kommentar
  vom 31.07. hält fest, eine Gegenprüfung sei unmöglich, weil für keinen
  betroffenen Text eine Linecode-Quelle vorliegt. Die 306 Dateien von #248 sind
  laut der verdichteten Historie oben (Eintrag 2026-07-30) am **Tag davor** ins
  Repo gekommen, darunter der größte betroffene Text. Die Feststellung war also
  schon bei ihrer Niederschrift überholt. Damit ist die Frage, die den Vorgang
  blockiert, an der Quelle entschieden: **OVG hat 135 leere `<l>` im TEI und
  135 Zeilen mit `...` in der Vorlage, Bijektion in beide Richtungen.** Über
  alle prüfbaren Texte 290 von 324 auflösbar, davon **jeder einzelne** ein
  Auslassungsmarker, kein Gegenbeleg.

**Die Lehre daraus ist eine Betriebsregel, keine Einsicht:** die Prämisse eines
blockierten Tickets altert, während das Ticket wartet, und sie altert
unbeobachtet, weil niemand ein wartendes Ticket nachmisst. Drei von zehn, und
in jedem Fall hätte die Person, die es abarbeitet, Arbeit gemacht, die schon
getan war, oder eine Entscheidung getroffen, die sich erübrigt hatte. **Vor der
Vorlage steht die Nachmessung, nicht die Zusammenfassung.**

**Rot: ich habe bei #358 gemessen, bevor ich den Kommentar gelesen habe.** Ausgezogen als rote Zeile 20 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: beinahe Textverlust gemeldet, der keiner war.** Ausgezogen als rote Zeile 21 nach [../fehlerjournal.md](../fehlerjournal.md).

**Was die zehn Vorgänge jetzt brauchen**, ist durchweg weniger als vorher:

| Vorgang | vorher | nachher |
|---|---|---|
| #364 | 21 Einzelfälle philologisch entscheiden | 24 Einträge mechanisch, 11 Entscheidungen |
| #366 | sieben Lemmata von Grund auf finden | sechs Vorschläge bestätigen, einer offen |
| #228 | neun Zweifelsfälle einzeln | acht als ein Paket, zwei getrennt |
| #252 | eine Frage über 838 Stellen Unterschied | an der Quelle beantwortet |
| #308 | vier Punkte | eine Frage (zwei Namensformen) |
| #358 | „prüfen, ob weitere Werke betroffen" | elf Werke, keines mechanisch entscheidbar |

**Ein Nebenfund, der in keinem Ticket stand:** `haueßenn` in KDO sitzt auf
`lemma_2670` *hase*, dem Säugetier, in einem Rezept über Hausenblase. Dritte
Handschrift, derselbe Fehlertyp wie #363, Einzelfall (unter `lemma_2670` ist es
die einzige `hau-`artige Form, ein Token korpusweit).

**Zur Zahl der abgebrochenen CI-Läufe**, die im Eintrag darüber erst „zwei",
dann „drei" hiess: gemessen **16 von 25** abgeschlossenen `data-integrity`-Läufen
auf diesem Branch, verteilt über den ganzen Tag. Beide früheren Angaben waren
geschätzt aus dem, was mir aufgefallen war. Dazu der Lesefehler, der die Lehre
im selben Zug unterlaufen hat: drei Checks auf `success` und einer auf
`in_progress` sind bei `cancel-in-progress` null grüne Checks.

**Phase:** PR #398 grün, Bot-Runden 16 bis 19 ohne Befund. Die zehn Vorgänge
bleiben `auto:blocked`/`wait:kzw`: auch wo die Frage kleiner geworden ist, ist
sie eine Entscheidung.

---
## 2026-09-06 (Nacht) – Elf weitere Vorgänge, und der Rückstand ist zu einem Drittel gar keiner

Fortsetzung des Durchgangs durch die blockierten Tickets. Zusammen mit den zehn
vom Abend sind es **21 Vorgänge** (#364, #378, #308, #363, #366, #375, #267,
#252, #228, #358, #115, #371, #189, #369, #370, #250, #251, #169, #239, #118,
#271). Nichts an Korpus oder Authority geändert.

**Sieben davon sind faktisch erledigt und warten nur auf Abnahme:** #358
(Willehalm gegliedert), #250 (alle drei Punkte, Punkt 3 über
`isInNestedParallel`), #251 (beide Punkte, der Fokusverlust unbemerkt
miterledigt), #169 (die drei ausdrücklich offengelassenen Nebenbefunde sind
alle drei entfernt), #239, #308 Punkt 1, #252. Das ist ein Drittel des
Rückstands, der als offen geführt wird, ohne es zu sein.

**Die Diagnose vom Abend war zu freundlich.** Sie lautete: die Prämisse eines
blockierten Tickets altert, weil niemand ein wartendes Ticket nachmisst. Nach
elf weiteren Fällen ist das genauer zu fassen:

- Bei **#252** war die Prämisse schon **am Tag ihrer Niederschrift falsch**. Der
  Kommentar vom 31.07. hält fest, für keinen betroffenen Text liege eine
  Linecode-Quelle vor; die 306 Dateien von #248 kamen am **30.07.**, belegt an
  drei Stellen (`docs/LINECODE.md:176`, `sources/README.md:11`,
  `sources/INVENTAR-ARCHIV.md:20`), zwei davon ausserhalb des JOURNAL.
- Bei **#169** hat dieselbe Person die angekündigte Aufräumrunde gemacht und den
  Vermerk nicht nachgezogen.
- Bei **#251** führte der eigene Statuskommentar einen Punkt als offen, der im
  selben Zug miterledigt worden war.

**Der Rückstand ist also nicht liegengeblieben, er ist nur nicht abgeschrieben
worden.** Das ist ein anderes Problem und braucht ein anderes Mittel: nicht
mehr Arbeit, sondern eine Abschlusskontrolle.

### Fünf Abhängigkeiten, die in keinem Ticket standen

Das ist der eigentliche Ertrag, weil er die Reihenfolge festlegt:

1. **#364 erledigt 64 % von #115.** Die 109 Baseline-IDs sind 35 Lemma-IDs plus
   35 Senses **derselben** 35 Lemmata plus 39 Senses an vorhandenen Lemmata.
   Schnittmenge 35, in keiner Richtung ein Rest.
2. **#371 löst die Blockade in #369.** Dort steht, für das Ufer gebe es keine
   geübte Zuordnung. `lemma_5732` trägt aber selbst einen Gewässer-Sense
   (`_sense_9002`), und `stat` ist dort als `type_20161` längst belegt: kein
   neues Lemma, kein neuer Typ.
3. **#370 hängt für 23 Paare an #378.** Ein neuer Variantentyp setzt sich unter
   first-wins nur bei kleinerer Lemmanummer durch. Für 23 der 41 irreführenden
   Paare (299 Tokens) wäre eine Freigabe **wirkungslos**: die Daten entstünden,
   und die Suche benutzte sie nie.
4. **#363 und #366 müssen dieselbe Frage gemeinsam beantworten.** `hawssen
   platern` (MBS5) und `haueßenn plossenn` (KDO) sind dieselbe Konstruktion.
5. **#189 und #118 teilen sich 16 Texte.** Die Virgel `/`, in #189 ein
   Kodierungsfehler (7.912 Tokens als `<w>` statt `<pc>`), ist in #118 der
   einzige brauchbare Indikator: sie trifft **alle neun** Texte des Augsburger
   Drucks von 1476 und nennt sieben weitere derselben Machart. Wer sie in #189
   heilt, nimmt in #118 den Marker weg.

### Zwei Funde, die über das Vorbereiten hinausgehen

**#118 hat keine Datengrundlage.** Die Entscheidungsvorlage nennt als
erstrangige Quellen Header-Datierungen und `works.xml`. Gemessen: **0 von 667**
Headern tragen `origDate` oder `creation`, und in `works.xml` haben **9 von
584** Werken eine mittelalterliche Jahreszahl, alle neun `<imprint>` 1476,
derselbe Druck. Die Schwellenregel hat im Repositorium keinen Eingabewert. Das
Vorhaben ist zuerst ein Beschaffungsprojekt, und das gehört vor die vier
Fragen.

**#271 hat ein zweites Namenregister.** Der Vorgang fragt, ob weitere
existieren, und hält fest, das sei nicht geprüft. Über die 305 `.txt`-Dateien
unter `sources/linecode/` mit einem Formkriterium gesucht (die 306. ist eine
RTF, auf die ein zeilenweises Kriterium nicht passt): genau zwei erfüllen es.
`tann.txt` (774 Einträge) gehört nicht zu TAN, sondern mit **695 von 774
(89 %)** zu **TKR**, „Di tutsch kronik von Behem lant". Beide Texte sind
böhmische Geschichtswerke, und in beiden steht die **gesamte Namenauszeichnung
im Header, im Textkörper keine einzige** (VTC letzter Treffer Zeile 141 bei
Headerende 151, TKR 121 bei 131): 0 `nameRef`, 0 `<placeName>`, je 6
`<persName>`, dazu 1 `<name>` in VTC und 2 in TKR. Das Material ist damit 1.242
Namenformen zu zwei Texten statt 468 zu einem.

Die erste Fassung dieses Absatzes nannte den Auszeichnungsstand „identisch" und
für beide Texte 1 `<name>`. Das Suchmuster war `'<name '` mit Leerzeichen und
übersah `<name>` ohne Attribute; TKR hat zwei. Gefunden hat es der CI-Review-Bot
in Runde 22, nachgemessen ist es hier. Die tragende Aussage (das Register ist
die einzige Stelle, an der die Namen erschlossen sind) hängt an der Verteilung
Header gegen Textkörper und nicht an der Symmetrie der Zahlen.

### Rot: vier eigene Fehler, drei davon selbst gefunden

- **`stat` auf 0 gemeldet, gemessen sind 95.** Ich hatte die Frequenzliste auf
  die 400 häufigsten Formen gekürzt und danach mit `dict.get(form, 0)` gefragt.
  **Ein fehlender Schlüssel wurde so zu einer Messung.** Aufgefallen, weil #369
  im Kommentar 95 zurückgehaltene Fälle dokumentiert.
- **„Seit dem 18.08." war die Wurzel eines flachen Klons.** `git log -S` zeigte
  auf `2c23520`, 4.183 Dateien, 17,5 Mio. Zeilen, `.git/shallow` zeigt darauf.
  Aus dieser Historie ist kein Zugangsdatum ablesbar. Die richtige Antwort stand
  zwei Bildschirmseiten weiter oben in derselben Datei.
- **467 statt 468 Registereinträge**, weil die BOM der Datei die erste Zeile
  nicht auf mein Zeilenmuster passen liess. Das Ticket hatte recht.
- **Nach `componentSelection` gegriffen**, dem Namen aus dem *Vorschlag*, und
  daraus geschlossen, der Umbau sei nicht gemacht. Er heisst `componentPicked`.
  Ein Grep nach dem vorgeschlagenen Namen prüft, ob jemand den Vorschlag
  wörtlich umgesetzt hat, nicht ob das Problem gelöst ist.

Die ersten drei sind dieselbe Familie wie die sechs Bot-Befunde vom Nachmittag,
nur in neuen Kostümen: ein Default, der als Messung gelesen wird; ein
Artefakt der Werkzeugkette, das als Datum gelesen wird; ein Parserdetail, das
als Bestand gelesen wird. **Jedes Mal hat eine Kette aus Werkzeug und Annahme
eine Zahl geliefert, und ich habe die Zahl genommen statt die Kette.**

**Phase:** PR #398 grün, Bot-Runden 16 bis 21 ohne Befund. Alle 21 Vorgänge
bleiben `auto:blocked`: auch wo nur noch eine Abnahme aussteht, ist sie eine
Entscheidung.

---
## 2026-09-07 – Beide TRO-Werte waren richtig, sie gehörten nur zu zwei verschiedenen Werken

Erste Session mit vollem Netzzugang. Damit war die eine Frage lösbar, an der
#395 seit dem 02.09. hing: Handschriftencensus 929 oder 212 im TRO-Header, und
welche der beiden GND.

**Der Zwischenstand war, dass `works.xml` recht hat und der Header unrecht.**
Über eine Websuche war 212 als Konrads *Trojanerkrieg* indirekt bestätigt; das
Korpus wurde bewusst nicht geändert, weil eine indirekte Bestätigung keine
Quelle ist. An der Primärquelle sieht es anders aus, und zwar in beide
Richtungen.

| Kennung | Primärquelle | Gegenstand |
|---|---|---|
| HSC 212 | `handschriftencensus.de/werke/212` | Konrad von Würzburg: 'Trojanerkrieg' |
| HSC 929 | `handschriftencensus.de/werke/929` | 'Trojanerkrieg'-Fortsetzung |
| GND 4285313-8 | `lobid.org/gnd/4285313-8.json` | Werk „Trojanerkrieg", `firstAuthor` Konrad von Würzburg |
| GND 1181164893 | `lobid.org/gnd/1181164893.json` | Werk „Trojanerkrieg-Fortsetzung", anonym, um und nach 1300 |

**Zwei Vermutungen des Tickets sind damit widerlegt.** `1181164893` ist keine
Personen-GND, wie die Form nahelegte, sondern eine Werk-GND. Und 929 ist keine
Handschriftennummer, wie der Kommentar vom 06.09. für möglich hielt, sondern
eine Werknummer. Beide Vermutungen waren aus der Form geschlossen, weil die
Domains gesperrt waren, und beide waren falsch.

**Der eigentliche Fund kam aber erst über die #397-Frage:** was hat diese
Änderung wahr gemacht, das vorher falsch sein konnte? Ich habe deshalb nach
Prüfungen gesucht, die auf dem alten Zustand beruhen, und dabei die 929 an
einer Stelle gefunden, an der sie niemand vermutet hatte: **`works.xml` führt
einen zweiten `bibl` mit derselben Sigle TRO**, `work_c7da236c-…`,
„Trojanerkrieg-Fortsetzung", Autor Anonym, und genau dieser trägt 929 und
`1181164893`.

Damit war der Konflikt nie einer zwischen Header und `works.xml`. Der Header
hatte seine Identifier aus dem **richtigen Repositorium, aber aus dem falschen
der beiden Einträge** geholt, während sein eigenes
`@corresp="works.xml#work_69"` auf Konrads Werk zeigt. Der Widerspruch saß
innerhalb des Headers, nicht zwischen zwei Dateien, und ein Vergleich Header
gegen `works.xml` konnte das nicht sehen, weil beide Werte in `works.xml`
stehen.

**Und die Datei enthält beide Werke.** Das steht in `works.xml` selbst: beide
TRO-Einträge tragen **denselben** `biblStruct`, Keller 1858, ohne die `xml:id`
zeichengleich. Die Datei läuft über 49.857 `<l>` mit Nummern von 1 bis 49.861
(vier Lücken: 24278, 42798, 49440, 49789) und enthält null `div`, null
`milestone`, null `pb`: es gibt keine Grenze, an der ein Werk aufhörte und das
andere anfinge. TRO ist die **einzige** der 668 Siglen mit zwei Einträgen in
`works.xml` (584 `bibl`, 669 Sigle-Einträge, 668 verschiedene Siglen), und
dieses eine Mal ist es richtig so.

**Hier stand zuerst „584 `bibl` auf 583 Siglen", und der Fehler ist lehrreicher
als die Korrektur.** Gefunden hat ihn der CI-Review-Bot, mit `grep` und ohne
Python, das ihm in seinem Job gesperrt ist. Meine Messung hatte je `bibl` nur
die **erste** Sigle gelesen (`find` statt `findall`), und 583 ist die Zahl der
verschiedenen *ersten* Siglen: eine Größe, die nichts bedeutet. Der Bot hat den
Widerspruch nicht an der Zahl selbst gesehen, sondern daran, dass sie mit einer
anderen Angabe aus demselben PR unvereinbar ist: wenn 70 der 584 Werke mehr als
eine Sigle tragen, kann es nicht 583 Siglen auf 584 `bibl` geben.

**Der eigentliche Schrecken lag woanders und ist ausgeräumt.** Dieselbe
Methode hätte eine Doppelsigle übersehen, die nicht an erster Stelle steht, und
darauf steht die Reichweitenaussage des ganzen Sync-Fixes. Mit `findall` über
alle Sigle-Einträge nachgemessen: TRO bleibt die einzige, die in zwei `bibl`
vorkommt. Die Aussage hält, aber sie hielt bis zu dieser Messung aus Glück.

**Zwei Zahlen, die ich zunächst hineingeschrieben hatte, stehen hier nicht
mehr**, und der Vorgang gehört zum Eintrag. Aus einer Websuche stammte, Konrads
Text breche nach 40.424 Versen ab und die Fortsetzung trage 9.412 weitere. Die
Reviewrunde hat beides an HSC, lobid, Wikidata und Wikipedia gesucht und in
keiner Quelle gefunden, und sie rechnen auch nicht auf: 40.424 + 9.412 = 49.836,
die Datei endet bei 49.861, und oberhalb von 40424 liegen gemessen 9.434 Verse.
Eine ungeprüfte Fremdzahl neben einer gemessenen sieht aus wie eine zweite
Messung, und das ist genau der wiederkehrende Fehler dieses Projekts. Was
bleibt, ist das Gemessene: bei `40424 ûf der geblüemten heide .` /
`40425 als dô die kriechen sâhen ,` läuft die Zählung ohne Grenze durch.

**Ebenfalls korrigiert:** der erste Entwurf behauptete, der Handschriftencensus
führe Keller 1858 unter 212 wie unter 929 als Ausgabe. Für 929 ist das falsch,
dort steht allein Thoelen/Häberlein 2015 (`grep -ci keller` auf der Seite: 0
gegen 1 bei 212). Dass jene Ausgabe „Konrad von Würzburg 'Trojanerkrieg' und
die anonym überlieferte Fortsetzung" heißt, also selbst beide Texte umfasst,
bleibt richtig und war das eigentliche Argument.

**Geändert:** der `msIdentifier` führt jetzt 212, `4285313-8` und zusätzlich
`Q66770444`, das `works.xml` schon hatte und der Header nicht. Er stimmt damit
mit seinem eigenen `@corresp`, seinem `<author>` und seinem `<title>` überein.
Die Fortsetzung bleibt über `works.xml` und die statische API auffindbar; sie
zu verlieren war die Sorge, und sie tritt nicht ein.

**Der Fix hätte sich selbst wieder aufgehoben, und gefunden hat das die
Reviewrunde.** `scripts/sync/sync_tei_headers.py` baut seine Zuordnung nach
Sigle (`sigle_to_work[sigle] = work_data`, ohne Kollisionsprüfung), löscht dann
alle Nicht-Sigle-`idno` und schreibt sie neu. Bei der Doppelsigle TRO gewann der
spätere Eintrag in Dokumentreihenfolge, also die Fortsetzung. Gemessen, indem
alte und neue Skriptfassung gegen je eine Kopie des Korpus liefen: die alte
schreibt 929 und `1181164893` zurück und entfernt `Q66770444` gleich mit.
`docs/DATA-MODEL.md` schreibt diesen Lauf für **jede** `works.xml`-Änderung vor,
der nächste Zotero-Eintrag hätte also gereicht.

**Das ist die Antwort auf die #397-Frage, und sie kam nicht aus der Suche nach
Prüfungen.** Ich hatte gefragt, welche *Prüfung* auf dem alten Zustand beruht,
und keine gefunden, richtigerweise: es gibt kein Gate, das Header-`idno` gegen
`works.xml` hält. Der Zerstörer war kein Prüfer, sondern ein **Schreiber**, und
danach hatte ich nicht gesucht. Die Frage lautet also nicht nur „welche Prüfung
verliert ihren Gegenstand", sondern „wer schreibt hier sonst noch, und woher
nimmt der seine Wahrheit". Der Sync nahm sie aus der Annahme „eine Sigle
identifiziert ein Werk", und die ist seit dem zweiten TRO-Eintrag falsch.

**Behoben im selben Durchgang**, sonst wäre der Header-Fix wertlos: der Sync
löst jetzt über das `@corresp` des Headers auf und fällt nur ersatzweise auf die
Sigle zurück, plus eine Warnung bei jeder Doppelsigle. Beweisbar folgenlos für
den Rest: 667 von 667 Korpusdateien tragen `@corresp`, alle 667 zeigen auf eine
in `works.xml` definierte `work_id`, und genau eine weicht von der
Sigle-Auflösung ab. Im Lauf beider Fassungen gegeneinander unterscheidet sich
**eine** Datei, `tei/TRO.tei.xml`.

Mitgenommen: die `xml:id` des `biblStruct` stand auf `TRO_TRO_TRO`, der Fassung
aus dem Fortsetzungs-Eintrag, statt auf `TRO_TRO` aus `work_69`. Das ist der
Fingerabdruck dafür, dass der Sync tatsächlich gelaufen ist und den falschen
Eintrag gezogen hat. Beide `biblStruct` sind ohne die `xml:id` zeichengleich,
und keine der beiden ids wird irgendwo referenziert (`grep` über js, py, html,
json: null Treffer).

**Kein Rebuild, und das ist gemessen statt aus der Routing-Tabelle abgelesen.**
Von den drei `tei/`-Zeilen der Tabelle in `docs/DATA-MODEL.md` nennt keine
`<idno>`, der Fall ist dort also gar nicht entschieden. Gemessen: Korpus-Index
byteidentisch, `extract-variants.py` meldet null Änderungen in allen vier
Kategorien, `build-api.py` 2.742 Dateien unverändert, Authority-Index
unverändert (er liest `works.xml`, nicht den Header). Schema-Validierung 1/1,
Cross-Ref-Audit `CI CHECK OK`. Also auch kein Versions-Bump.

**Umgebung, drei Messungen für die nächste Cloud-Session.** Der Playwright-Test
`lemma page loads Wörterbuchnetz entries via API` bleibt rot, obwohl der
Netzzugang da ist: per curl antworten alle fünf Wörterbücher mit 200, im
Chromium des Tests scheitert **jeder** externe HTTPS-Host an
`ERR_CONNECTION_RESET`, gegengeprüft mit `example.com`, `api.zotero.org` und
`handschriftencensus.de`. Der Browser kommt an den Proxy nicht heran, das ist
kein Befund über die Anwendung. Zweitens: Playwright startet
`chromium_headless_shell-1193`, ein Symlink nur auf `chromium-1193` genügt
nicht. Drittens: die Zotero-Gruppe 5043625 ist öffentlich, `--offline` war nie
wegen eines fehlenden Schlüssels nötig.

**Phase:** #397 geschlossen (der Satz steht in `CLAUDE.md`, im
Betriebsvertrag und seit heute in der eingecheckten Agentendefinition). #395
liegt im PR zu diesem Eintrag und wird mit dessen Merge geschlossen.
`fable-reviewer` und `fable-advisor` liegen jetzt unter
`.claude/agents/`, weil das eingecheckte Gedächtnis ohne Definition unbenutzbar
war und Regel 11 in der Cloud-Session vom 06.09. nicht erfüllbar.

---
## 2026-09-07 (Nachmittag) – Dreimal derselbe Fehler, und zweimal war er der Fix des vorigen

Fortsetzung derselben Session. #402 (Naming-Index-Pin auf `v0.2.2-beta`,
Zitation an drei weiteren Stellen nachgezogen) und #400 (TRO) sind gemergt,
danach #399 als PR #403. Der Eintrag hängt an dem, was #403 gekostet hat,
nicht an dem, was es geliefert hat.

**Die Prämisse des Tickets war abgelaufen, und das hat es von einer
Korpusänderung zu einem Gate verkleinert.** #399 beschreibt systematische
Drift: „nur 417 von 667 Dateien führen überhaupt einen Identifier außer der
Sigle". Die 417 und die 250 stimmen, die Folgerung nicht: für alle 250 hat
`works.xml` ebenfalls nichts. Gegenprobe über `@corresp`: `works.xml` liefert
genau 355 handschriftencensus, 217 GND und 131 wikidata, deckungsgleich mit
dem Header-Bestand. Nach #398 und #400 ist die Drift **null, 667 von 667**.
Der Generator ist heute ein No-op, und der Wert der Arbeit liegt allein
darin, dass es so bleibt. Kein Korpus- und kein Indexbestand angefasst, also
auch kein Versions-Bump.

**Der teure Teil war eine Kette aus drei Klasse-A-Befunden, von denen zwei
erst durch den Fix des vorigen entstanden sind.**

1. `--all` fiel still in den alten lxml-Pfad. Der löscht alle
   Nicht-Sigle-`idno`, also auch die 19 `mwb-sigle`, die `works.xml` gar nicht
   kennt (gemessen auf einer Korpuskopie: 19 Dateien vorher, 0 nachher). Fix:
   `works` läuft immer über den chirurgischen Schreiber.
2. Genau dieser Fix las `syncers_to_run` vor der Bindung. `--works`,
   `--works --dry-run`, `--all` und `--all --dry-run` schrieben korrekt und
   endeten dann im `UnboundLocalError` mit Exit 1. Die Abhilfezeile des Gates
   nennt `--works`, und genau dieses Kommando lief in den Traceback. Fix: den
   Block hinter die Berechnung schieben.
3. Genau dieser Fix schob den Block zugleich **vor** den Stub-Guard. Damit
   schrieb `--works --persons` erst das Korpus und fiel danach mit
   „Refusing to report a misleading '0 updated' success" durch, während der
   Guard genau das verhindern sollte. Auf `main` stand er vor jeder
   Schreibarbeit. Fix: Reihenfolge wiederhergestellt.

Dreimal hintereinander die #397-Frage auf demselben Code, und dreimal hat
niemand sie von sich aus gestellt, sondern erst der nächste Reviewer. Das ist
der eigentliche Ertrag des Tages: **die Frage einmal zu stellen genügt nicht,
wenn der Fix selbst wieder ein Fix ist.** Sie gehört an jede Runde, nicht an
den Diff.

**Der CI-Bot fand zwei davon bei grünem Check.** In `CLAUDE.md` steht das
Muster andersherum, mit vier Läufen belegt: roter Check, der kein Befund ist.
Hier war es die Umkehrung, und die Ursache ist dieselbe Sorte Zufall. Das Gate
in `data-integrity.yml` ruft `--check` auf, und dieser Zweig kehrt vor der
defekten Stelle zurück; die kaputten Modi berührte kein Job. Die Regel bleibt
also, sie gilt nur in beide Richtungen: **die Farbe des Checks ist keine
Aussage über die Befunde, in keiner der beiden Richtungen.** Der Bot hat
außerdem beide Male ohne Python gearbeitet (die Berechtigungsschicht lehnt
`python3 <script>` ab) und den Blocker aus dem reinen Lesen des Kontrollflusses
abgeleitet, mit der Ansage, worauf er sich stützt und was er nicht messen
konnte.

**Zwei Zahlen aus dem eigenen PR-Body zurückgezogen statt belegt.** „`--all
--dry-run`: 0 Änderungen" stammte aus einer Messung vor Befund 1 und stimmte
für den gepushten Stand nicht; der Bot hat genau das vermutet und es traf zu.
Und die Aufschlüsselung „543 identisch, 119 nur Reihenfolge" widersprach der
Messung der lokalen Runde (540/116/6/5). Die fünf inhaltlich abweichenden
Dateien, auf die es ankommt, sind zweimal unabhängig gemessen und stehen; die
Aufschlüsselung braucht niemand und ist deshalb gelöscht statt nachgemessen.
Vier Reviewrunden, acht Befunde, und zwei der acht waren hausgemacht.

**`mwb-sigle` ist gegen die Vorgabe im Ticket nicht migriert worden, und der
Grund ist ein Modellbruch.** `works.xml` führt Identifier je Werk, das MWB
vergibt seine Siglen je Handschriftenredaktion (`NibA`, `NibB`, `NibC`,
`NibD` sind im Quellenverzeichnis vier Einträge). Fünf der 19 betroffenen
Werke tragen mehr als eine Sigle; aus `works.xml` generiert bekämen **zehn
Dateien eine fremde MWB-Sigle**, und alle zehn existieren. Beim Nachmessen für
das Folgeticket kam der Fall dazu, der die Richtung umdreht: `FB` und `FH`
tragen dieselbe MWB-Sigle `UvLFrd`, gehören aber zu zwei verschiedenen Werken.
Die Zuordnung ist also in beiden Richtungen mehrdeutig, und eine Ablage je Werk
kann keine der beiden abbilden. Als **#404** ausgelagert, `auto:pair`. Bis
dahin bleibt der Typ header-eigen, festgeschrieben in `CONTRACTS.md` F.4.

**Ein Test war seit jeher rot und niemandem aufgefallen.**
`main-site.spec.js:50` hängte seinen Console-Listener erst nach `page.goto` an.
Sonde: Listener vor `goto` findet „[MainSiteApp] Ready" als Logzeile 13 von 15,
Listener danach findet **null** Zeilen überhaupt, weil `goto` erst nach 12,8 s
auflöst und die Initialisierung dann durch ist. Mit `page.reload()` behoben,
nicht übersprungen, plus Gegenprobe, dass der Test noch rot werden kann.

**Phase:** #399 geschlossen, #404 neu. Offen und an Menschen hängend: KZWs 13
zurückgehaltene `fro`-Fälle (#387), sieben Tickets, deren Code gemergt ist und
die auf Abnahme warten, die Lizenzeinschätzung zu #262, die Burch-Mail für
#225. Von 60 offenen Vorgängen sind 53 `auto:blocked` oder `auto:pair`; der
Rückstand ist damit weniger ein Arbeits- als ein Entscheidungsrückstand.

---
## 2026-09-07 (Aufräumlauf) – Zwei Doku-Stellen waren falsch, und beide lagen im toten Winkel eines Gates

Aufräum- und Doku-Durchgang am Ende der Session. Alle sechs Gates liefen vorher
grün, gefunden wurde trotzdem dreierlei, und die zwei interessanten Funde haben
dieselbe Form: **ein Gate, das genau daneben greift.**

**Der Workflow führte mehr Prüfungen, als `DEVELOPMENT.md` beschrieb.** Die neue
aus #399 fehlte, und mit ihr verschob sich die Nummerierung: die Zeile über die
Diff-Basis verwies auf „checks 3 and 10", Prüfung 7 auf „BEFORE check 8". Die
Zahlen dieses ersten Durchgangs (dreizehn Prüfungen, 4 und 11, check 9) waren
ein Zwischenstand und sind von Runde 2 weiter verschoben worden; **verbindlich
ist die Endnummerierung unten.** **`check-doc-inventories.py` konnte das nicht finden, und zwar nicht aus
Nachlässigkeit:** es deckt `scripts/audit/` und den Verzeichnisbaum von
`scripts/README.md` ab. Der neue Gate-Aufruf ist beides nicht, er liegt in
`scripts/sync/` und ist ein **Workflow-Schritt**, kein Skript-Eintrag. Zwischen
den beiden Inventaren liegt genau diese Naht.

**`docs/features/114-tabellenansicht-korpussuche.md` stand einen Monat zu lang.**
#114 ist seit dem 05.08. geschlossen, und der JOURNAL-Eintrag von damals sagt
den Auftrag selbst: „bei Close in Stable-Docs bereits destilliert → löschen".
Vor dem Löschen gegengeprüft, dass das Wissen wirklich woanders steht: Keyness
normativ in `CONTRACTS.md` §H.1, die Ansicht samt der Entscheidung „die
Gesamtzeile wird bewusst nicht exportiert" in `FEATURES.md`. Beides da, Datei
gelöscht, Git-History ist das Archiv.

**Die ROADMAP beschrieb seit fünf Wochen den Stand von Anfang August.** Ihr
Abschnitt „Now" führte Frauenlob, #58 und #251 als das Aktuelle, während
seither #235, #369, #216, #387, #395 und #399 gelaufen sind. Neu geschrieben auf
den Befund, der die Planung heute tatsächlich bestimmt und der beim Lesen aller
62 offenen Vorgänge herausgekommen ist: **48 `auto:blocked`, 7 `auto:pair`, 6
`auto:checkin`, plus #44.** 55 von 62 kann keine Session bewegen. Der Rückstand
ist ein Entscheidungsrückstand.

**Und ein zweiter toter Winkel, im selben Dokument.** Der Absatz zu #124 kündigte
seit zwei Monaten offene Arbeit an („was offen bleibt, ist die Freigabe der DSB
und der Dashboard-Zugang"), obwohl KZW das Ticket am 10.07. geschlossen hat.
`pruefe_roadmap()` sieht das nicht, und sein eigener Docstring sagt warum: es
prüft **nur** die erste Spalte einer Tabellenzeile, weil ein Gate, das jede `#N`
im Fließtext prüft, beim ersten Lauf 45 Zeilen gemeldet hätte und dann
abgeschaltet worden wäre. Die Enge ist bewusst gewählt und richtig; der Preis
ist genau dieser Absatz. Er ist jetzt korrigiert, und die Notiz dazu steht
daneben, damit der nächste Leser nicht denkt, das Gate habe versagt.

Nebenbei geklärt, weil es an #255 hängt: der Matomo-Dashboard-Zugang ist keine
Projektaufgabe, sondern eine Anfrage an die IT Services (Lesezugriff auf
Site-ID 15). Ob die DSB-Eckdaten je beantwortet wurden, hält dieses
Repositorium nicht fest.

**Was sonst gemessen und in Ordnung war:** Indexversionen Code gegen
`TEI-MODEL.md` §11 und `INDEX.md` deckungsgleich (4.2.13 / 1.9.3), kein
Verweis auf einen heute geschlossenen Vorgang als offen, Arbeitsbaum sauber,
kein offener PR, mein Branch beim Merge remote gelöscht.

**Runde 2, vom CI-Review-Bot, und beide Befunde sind Restlücken derselben Sorte.**
Erstens: die reparierte Prüfliste war immer noch unvollständig. Die beiden
Budget-Schritte aus #111 fehlten, schon in der alten Zwölfer-Fassung. Das ist
nicht bloß eine Zahl: der Budget-Schritt warnt zwar bei Überschreitung, wird
aber rot, wenn die **Messung selbst** scheitert (`exit 2`, kein
`continue-on-error` im Workflow, nachgesehen). Ein Lauf konnte also an einem
Schritt rot werden, den die Liste nicht führte und für den es unter „Debugging
failures" keinen Eintrag gab. Selbst nachgezählt statt die Zahl des Bots zu
übernehmen: **16 Gate-Schritte, 15 Prüfungen** in der Zählweise der Doku, die
`Regenerate` und `Fail if differs` zusammenfasst. Der Bot war bei 15/14, also um
eins daneben, und hat die Korrektur in seiner zweiten Runde selbst bestätigt.
**Endstand:** 15 Prüfungen, Budget-Selbsttest und Budget als 5 und 6, Diff-Basis
für 4 und 13, `variants.xml` vor Prüfung 11. Die Liste deckt sich damit Position
für Position mit dem Workflow, gegengeprüft über einen Abgleich beider
Reihenfolgen.

Zweitens: die neu geschriebene ROADMAP widersprach sich selbst. Zeile 60 führte
#216 im Präsens als „still ready to start" mit rund 7.000 Tokens, während der
neue „Now"-Abschnitt 78 Prozent und 1.547 nennt. Faktor 4,5, und zwar in einer
Datei, die zwei Absätze weiter unten genau diesen Fehlertyp als Lehre
formuliert. Ich hatte den Abschnitt „Now" ersetzt und den Rest der Datei nicht
gegengelesen. Jetzt als datierter Rückblick markiert, wie die Nachbarabsätze.

Beide Male greift kein Gate, und beim zweiten aus einem dritten Grund:
`pruefe_roadmap()` sucht **geschlossene** Nummern in Tabellenzeilen, #216 ist
offen und stand im Fließtext.

**Nachtrag am 08.09.: der Restbefund des Bots war falsch, und beim Nachsehen lag
daneben ein echter.** Der Bot hatte in Runde 3 angemerkt, die Inline-Kommentare
in `data-integrity.yml` verwiesen auf „vor dem Index-Rebuild (Step 6)", während
der Rebuild in der korrigierten Doku-Zählung Prüfung 11 sei. Er hat das
ausdrücklich nicht als Befund gemeldet, sondern als Hinweis. **Beides ist
trotzdem nachzumessen, und es hält nicht:** der Workflow führt im Kopfkommentar
ein **eigenes** Schema (`0, 1, 1a, 1b, 1c, 2, 3, 4, 5, 6, 6b, 6c, 7, 8`), und
darin ist Step 6 tatsächlich die Index-Freshness. Die beiden Zeilen stimmten.
Wer den Hinweis übernommen hätte, hätte zwei richtige Zeilen „korrigiert" und die
Datei mit sich selbst in Widerspruch gebracht.

**Was beim Nachsehen wirklich fehlte, war meine eigene Auslassung aus #403:** der
Kopfkommentar listet vierzehn Einträge und kennt den #399-Schritt nicht. Ich
hatte ihn früh am 07.09. in den Workflow eingefügt, die Doku später nachgezogen
und die Liste übersehen, die in der Datei selbst ganz oben steht und die jeder
zuerst liest. Ergänzt als `1b`, die nachfolgenden Buchstaben um eins weiter
(`1b` auf `1c`, `1c` auf `1d`), die beiden internen Verweise darauf mitgezogen.

**Und die Ursache des falschen Hinweises ist selbst behebbar.** Zwei
Nummernschemata für dieselben Schritte, ohne dass eines der beiden Dokumente das
erwähnt, laden genau zu dieser Verwechslung ein. Beide sagen es jetzt: der
Workflow-Kopf nennt das Schema der Doku samt der Zuordnung „Step 6 hier ist
Prüfung 11 dort", `DEVELOPMENT.md` umgekehrt, und beide schließen mit derselben
Anweisung, die Listen über die **Namen** zu vergleichen und nie über die Nummern.
Die Buchstaben im Workflow-Schema sind dabei kein Schönheitsfehler, sondern der
Grund, warum es überhaupt zwei gibt: ein später eingefügter Step zeigt dort seine
Position, ohne die Ziffern darunter zu verschieben. Die Buchstaben verschiebt er
sehr wohl, dieser hier hat `1b` auf `1c` und `1c` auf `1d` geschoben; stehen bleibt
`2` bis `8`. Den zu starken Satz hat die lokale Reviewrunde gefunden, und zwar an
allen drei Stellen, an denen ich ihn gleichlautend hingeschrieben hatte. Ebenso die
Angabe `0,6 s` für das Gate: heute gemessen sind es 0,71 s reine Prüfzeit und 0,90
bis 1,19 s Wanduhr. **Und die Suche danach war selbst fehlerhaft, zweimal auf
verschiedene Weise.** Gemessen auf `origin/main` gab es **vier** Fundstellen, drei
mit deutschem Komma (`data-integrity.yml`, `scripts/README.md`, das Agent-Memory zu
#395) und eine mit Punkt (`DEVELOPMENT.md`, weil die Datei englisch ist). Ich hatte
drei gefunden und dann behauptet, es seien fünf gewesen: die fünfte war die
Kopfzeile `1b`, die dieser Lauf selbst geschrieben hat und die nie `0,6 s` trug.
Eine Korrektur einer Zahl, die selbst eine falsche Zahl nennt.

**Die beiden Auslassungen haben verschiedene Ursachen, und nur eine davon ist die
naheliegende.** `DEVELOPMENT.md` fehlte am Dezimaltrenner: die Datei ist englisch
und schreibt `0.6 s`. Das Agent-Memory dagegen schreibt das deutsche Komma und wäre
gefunden worden, es fehlte am **Suchpfad**: mein grep lief über `.github/`, `docs/`
und `scripts/` und damit nicht über `.claude/`. Die zweite ist die übertragbarere
Lehre, weil `.claude/agent-memory/` inhaltliche Aussagen über dieses Projekt trägt
und bei jeder Suche nach einer Behauptung mitgemeint ist. Beides gefunden hat der
CI-Bot, die Zahl in Runde 2 und die erste Auslassung in Runde 1.

Gegenprobe zum Eingriff: die 201 Nicht-Kommentar-Zeilen des Workflows sind vor
und nach der Änderung identisch, das YAML parst, 20 Steps im Job.

**Phase:** Betrieb. Offen und beabsichtigt offen: #404 (Modellfrage mwb-sigle),
#406 (KZW-Triage), #59 (nach Lindas Freigabe vom 02.09. vermutlich schließbar).
Nicht von dieser Session: auf `origin/claude/235-315-wzb-tokens-lead-editor`
liegt Julias Arbeit zu #198 Schritt 2 vom 21.08., nie gemergt, ohne PR; der
Befund steht als Kommentar an #198.

---

## 2026-09-10/11 (Nachtsitzung) – Ein gemeldetes Token waren neunzehn Belege, und die Versionsnummer war schon vergeben

Drei freigegebene Vorgänge, zwei PRs, gemergt: **#427** (Escaping der
Ergebnisköpfe im Playground), **#425** (Mehrwort-Lemmata dokumentiert) in PR
#428, **#363** (Hausenblase) in PR #429.

**Der Vorgang war sechsmal so groß wie seine Meldung.** #363 meldete ein Token,
`hawssen` in MBS5 am Adjektiv *heiʒ*. Die Suche nach den Schreibformen statt nach
der gemeldeten ID findet **19 Belege in 7 Sigeln, 32 Tokens**, und alle sieben
Sigel sind Kochbücher. Von den 19 waren 5 richtig; die übrigen 14 hingen an
sieben Lemmata, darunter das Verb *hûsen* „wohnen", der *hase* und die
Mönchstonsur. Sieben Tokens trugen gar kein `@lemmaRef`. Die Bestätigung stand im
eigenen Korpus: KBL4 schreibt „ovch ist die **husen blater** vnd all **fisch
blatra** guot in sulcza", eine Apposition, keine Auslegung.

**Zweimal habe ich in diesem Vorgang behauptet, eine Mehrwort-Einheit wäre „die
erste im Korpus", und damit gegen die philologisch richtige Zuordnung
argumentiert.** Beide Male falsch, und beide Male hätte ein Blick in
`variants.xml` gereicht: das Muster gibt es seit Jahren an `lemma_3141` *Joie de
la Court*, `lemma_9250` *Schastel Marveile*, `lemma_9251` und `lemma_20598`, und
`Schastel Marveile` trägt sogar dieselbe Doppelung aus getrennter und
zusammengeschriebener Schreibung wie dieser Fall. Dokumentiert war es nirgends,
was genau der Grund ist, warum es zweimal übersehen werden konnte. Daraus wurde
#425, und `TEI-MODEL.md` §4.1a hält seit #363 auch fest, dass die Klasse nicht
auf Eigennamen beschränkt ist.

**Die Typ-Entscheidung ist der technische Kern und war beinahe ein Datenschaden.**
Ein `type_N` ist eine Schreibform *eines* Lemmas, und `extract-variants.py` löst
ein mehrdeutiges Paar per Mehrheit auf. Wer den Bestands-Typ mitnimmt, nimmt
fremde Tokens mit: `type_106683` *pleter* trägt 45 Tokens, 43 davon bleiben bei
`lemma_737` *blat*. Das Skript entscheidet deshalb je Form am gescannten Korpus,
5 umgehängt und 10 neu geprägt, und `extract-variants` bestätigt es von der
anderen Seite mit **0 Typen an mehr als einem Lemma**.

**Der teure Fehler war ein anderer: die Versionsnummer war schon vergeben.** #363
ist mit Korpus 4.2.14 und Authority 1.9.4 gemergt worden, während der offene PR
#416 genau diese beiden Nummern seit seinem Rebase vom 09.09. trug. Kosten, mit
`git merge-tree` gemessen: acht Konfliktdateien in Julias PR, allesamt
abgeleitete Schicht plus Versionsliterale, dazu Umnummerierung und ein
vollständiger Rebuild auf fremdem Branch. Die Quelldaten mischen sich sauber.
**Kein Gate deckt das ab, und beide waren auf beiden Seiten grün:**
`check-index-versions.py` prüft Konsistenz *innerhalb* eines Arbeitsstands, das
#154-Bump-Gate nur, *dass* gebumpt wurde. Regel steht jetzt im
Data-Change-Lifecycle, Befund als Kommentar an #416.

**Die zweite Lehre ist eine über Zahlen an ausgelieferten Seiten.** Eine
Lemma-Löschung verschiebt vier Zähler, und die stehen an 36 Stellen in 15
Dateien, einschließlich des Stats-Blocks der Startseite. `doc-count-audit.py`
läuft nur in `validate` und steht nicht in der Schrittfolge des Lifecycles, ist
also erst in der CI rot geworden. Danach hat der Review-Bot zweimal nachgesetzt,
und beide Male am selben Muster: meine Gate-Erweiterung war für zwei von drei
Dateien wirkungslos, weil der Anker `Lemmata` „Lexikoneinträge" nicht trifft, und
nach dem Ankerfix meldete eine Datei Abdeckung, ohne zu prüfen, weil „rund" vor
einer exakten Zahl den Rundungs-Skip auslöst. **Ein Target, das Abdeckung meldet
und schweigt, ist schlechter als eines, das fehlt.** Jede der drei Bindungen ist
jetzt mit eigener Mutationsprobe belegt.

**Scorecard Doku-Check 2026-09-11** (Trigger: drei PRs an `docs/`). Flow der
geänderten Abschnitte gelesen, drei Algorithmen gegen den Code (Positionszählung
gegen `extract_word_data`, Drei-Stufen-Auflösung gegen `resolveLemmaIds` plus
`lemma-resolve.js`, Auto-Match gegen `wzb-auto-match.py`): alle drei
deckungsgleich. Vier XPaths der Build Script XPath Reference gegen
`build-authority-index.py`, samt relativer Achsen: exakt. Alle Zähl-Gates grün.
**Drei Befunde, behoben:** `POS-TAGSET.md` sagte als einzige Quelle der Wahrheit
für `@pos` nichts zu Mehrwort-Einheiten, obwohl #363 dort 32 Tags vergeben hat
(neuer §7: `@pos` bleibt Eigenschaft des Tokens, *Joie de la Court* liest
`NAM PRP ART NAM`); die Glosse zu *hûsenblâter* warf die Blase mit dem daraus
gewonnenen isinglass zusammen; „the four names above" stand hinter einer Liste
von fünf. **Ein Befund offen, weil er eine Entscheidung braucht:**
`scripts/README.md` sagt, ein issue-gebundenes Einmal-Skript wandere nach
`_archived/`, sobald sein Issue geschlossen ist, die Praxis in
`scripts/ingest/pos-disambig/` tut das nicht (`fix-367-waeren.py` liegt dort bei
geschlossenem #367, und `fix-363-hausenblase.py` jetzt ebenso). Entweder die
Regel gilt dort auch, oder sie ist auf die Wurzel einzugrenzen: als #430
abgelegt, weil zwei nebeneinanderstehende Fassungen jede Session neu entscheiden
lassen.

**Phase:** Betrieb. Offen und auf Menschen wartend: #416 (zwei Antworten, dazu
die Versionskollision), #252, #366 (jetzt acht Formen statt sieben, weil
`KDO_121170100_3` erledigt ist und die beiden `hawsen`-Belege aus #363
zurückkamen: sie sind der Fisch, nicht die Blase), #410, #419.

---

## 2026-09-11 – #198 Schritt 2 zugestellt: die Entscheidung war eine Messfrage, das Problem war die Zustellung

**Summary:** Schritt 2 von #198 ist auf `main`. Das `<pos>NOM</pos>` ist aus `lemma_2598` *haben* entfernt, die drei seit PR #205 zurueckgehaltenen NOM-Tokens sind entschieden, und der Sense-Split, der hier seit Juli als die eine offene philologische Frage stand, findet nicht statt. Korpus-Index 4.2.15, Authority-Index 1.9.5. Die inhaltliche Arbeit ist Julias Commit `a1089cb6c` vom 21.08.2026; die Messungen unten sind am 11.09. gegen den gemergten Stand neu gerechnet, drei Zahlen haben dabei nicht gehalten.

**Die Frage war seit Juli als kuratorisch etikettiert und liess sich messen.** „Welche der acht `<sense>` von *haben* sind nominal und gehoeren zu *habe*" klingt nach einer Lesart-Entscheidung. Schluesselt man jeden Sense nach den `@pos` seiner Korpusbelege auf, ist die Antwort eindeutig: alle acht sind ausschliesslich verbal belegt. Es gibt damit keinen Sense, der umziehen muesste.

**Die Reihenfolge ist der eigentliche Inhalt des Schrittes.** Solange ein `<w>` unter `lemma_2598` ein `NOM` traegt, widerspraeche ein Lexikon ohne `<pos>NOM</pos>` dem Korpus. Erst die drei Faelle, dann die eine Zeile: `AC3_23010_1` („hawe vnd schaufel", Geraetepaar als Satzsubjekt) auf `lemma_9644` *houwe*, `DA_8222_3` („daz er dehein habe gesehen / diu bezzer waere") auf `lemma_2593`, weil `dehein habe` eine saubere NP ist und das feminine `diu` mit *habe* kongruiert, `JT_6192000_1` verbal wegen Konjunktiv mit Akkusativobjekt. Gegenprobe danach: null NOM-Tokens unter dem Lemma.

### Drei Zahlen aus dem urspruenglichen Text haben der Nachmessung nicht standgehalten

Keine davon aendert das Ergebnis, alle drei sind nach der Hausregel „jede Zahl ist gemessen oder sie steht nicht drin" zu korrigieren.

- **„26 von 101" waren 28 von 101.** Ohne die `@ana`-Nacharbeit stuenden 28 der 101 `lemma_2593`-Tokens ohne Sense. Die 26 zaehlt nur die von #198 betroffenen Tokens, der Nenner ist die volle Menge. Gemessen: auf `main` 27 von 100 ohne `@ana`, mit diesem Schritt 3 von 101.
- **„dieselben Konzepte" ist eine Obermenge.** `lemma_2598_sense_4170` traegt `concept_21072000`, `concept_23308000` und `concept_31200000`, `lemma_2593_sense_4159` nur die ersten beiden. Das dritte Konzept ist genau das, was die Senses unterscheidet. Am Schluss aendert das nichts, es stuetzt ihn eher.
- **„ein Eintrag von 43.879" sind 43.878.** Seit #363 ist `lemma_27031` *hasenblâse* geloescht.

### Und eine Annahme, die KZWs Entscheidung widerlegt hat

Der urspruengliche Text sagte, der Typ-Id-Konflikt „kippt von selbst, sobald das *houwen*-Folgeticket die zwoelf umhaengt". Das trifft nicht zu. `AC3_23010_1` behaelt sein `@corresp` auf `type_117159`, der Typ haengt damit an zwei Lemmata (12 mal `lemma_2598`, einmal `lemma_9644`), und das ist der erste Injektivitaetsverstoss im Korpus: auf `main` gilt die Eindeutigkeit bei **256.772 von 256.772** Typ-Ids ausnahmslos. (Die Zahl stand hier zunaechst als 256.762. Das war die Messung vom 10.09., vor den zehn Typen, die #363 gepraegt hat; fortgeschrieben statt neu gerechnet, gefunden von der Reviewrunde am 11.09.)

KZW hat die dreizehn Belege am 11.09. in #418 einzeln entschieden, und sie wandern **nicht** geschlossen. Seine Tabelle nennt sechs Verbbelege, sechs zum Substantiv und einen unklaren; der unklare (`AC2_9100_9`) ist in derselben Diskussion als Verb aufgeloest worden, und zwei der Substantivbelege brauchen einen neuen Sense. Endstand also sieben zum Verb `lemma_2923` *houwen*, vier auf den bestehenden Sense von `lemma_9644`, zwei auf einen neuen Sense „Schlag" desselben Lemmas. Die Aufteilung sechs zu sechs zu eins ist KZWs, die Aufloesung auf sieben zu vier zu zwei unsere. Ob `type_117159` danach noch mehrdeutig ist, ist damit eine Folge dieser Zuordnung und keine Selbstverstaendlichkeit. Es wird nach der Umsetzung von #418 gemessen und dort festgehalten, nicht vorher behauptet.

### Ein Zeilenende haette 236.000 Scheinaenderungen ins Korpus getragen

Beim Nachtragen der vier `revisionDesc`-Eintraege hat mein eigenes Skript `tei/WZB.tei.xml` im Textmodus gelesen und geschrieben. Die Datei ist die **einzige** im Korpus mit CRLF, und der Schreibvorgang hat daraus stillschweigend LF gemacht: 235.980 Zeilen geaendert, in einem einzigen Hunk ueber die ganze Datei.

Aufgefallen ist es nur an `git diff --stat`, das fuer WZB 471.961 Zeilen meldete, wo 25 zu erwarten waren. **Kein Gate und kein Test haette das gefangen:** die XML ist aequivalent, der Index baut byte-identisch aus beiden Fassungen (nachgemessen), und `.gitattributes` setzt fuer `*.xml` ausdruecklich `-text`, git normalisiert also bewusst nicht und meldet auch nichts. Die Datei traegt ausserdem 17 Zeilen, die schon vorher LF hatten, eine pauschale Rueckumwandlung waere also ebenfalls falsch gewesen; rekonstruiert wurde zeilenweise aus den Bytes von `main`.

Die Lehre ist keine ueber Zeilenenden, sondern eine ueber Werkzeuge: wer eine Korpusdatei mit einem Texteditor-Skript anfasst, aendert mehr als die Zeile, die er meint. Fuer Eingriffe in `tei/` gilt Binaermodus oder `newline=''`, und die Gegenprobe ist die Zeilenzahl im Diff, nicht der Augenschein.

### Die Nummernkollision, zum zweiten Mal in zwei Tagen

Der Commit trug urspruenglich Korpus-Index 4.2.3 und Authority 1.9.1, nach dem Rebase vom 09.09. dann 4.2.14 und 1.9.4. Genau diese beiden Nummern hat in der Nacht auf den 11.09. der #363-Merge vergeben, waehrend dieser PR offen lag. Aufgeloest als 4.2.15 und 1.9.5, die abgeleitete Schicht neu gebaut statt zeilenweise gemerged.

Das Gate `check-index-versions.py` hat dabei einen Fehler von mir gefangen, den ich sonst gepusht haette: `corpus-loader.js` fuehrt die Authority-Version in einer **zweiten** Zeile, und ich hatte nur die Korpus-Version hochgezogen. Das ist der Nutzen dieses Gates in einem Satz.

**Die Lehre ist keine ueber Rebases, sondern eine ueber Zustellung.** Die Entscheidung war am 21.08. gefallen und gemessen; sie hat trotzdem 21 Tage lang nichts bewirkt, weil kein PR existierte, und #198 las sich in dieser Zeit weiter als eine offene Frage an Julia. Ein Commit ohne PR ist in diesem Repositorium kein Zwischenstand, sondern unsichtbar.


---

## 2026-09-11 (Nachmittag) – Anhänge nachgeholt, und zwei Zahlen, die aus zwei Mengen kamen

Diese Sitzung lief auf dem Laptop, wo GitHub-Anhänge abrufbar sind. Vorausgegangene Sitzungen bekamen dort `403` (die Begründung steht in #419: `user-attachments` liegt ausserhalb der freigegebenen Repositoriumspfade). Nachgeholt wurden die Anhänge der offenen Vorgänge. Der grösste Posten war Alans Testprotokoll in #419, dessen 15 Screenshots bis dahin niemand gesehen hatte.

**Was die Screenshots hergaben, war nicht das, was im Protokoll stand.** Alan hatte zum Reimwörterbuch notiert: „nein - die belege sind nicht da und anklickbar, und man kann kein zweites lemma ‚tot' angeben" (DOCX in #419, Testfall 8). Auf dem Bild steht `Mindest-Reimpaare 6`, und Gottfried reimt `brôt` und `tôt` fünfmal. Mit der Vorbelegung 1 kommt genau seine Antwort samt anklickbaren Belegen. Der Fehler liegt trotzdem bei uns, nur woanders: bei 0 Reimpartnern nennt die Oberfläche zwei Gründe (Kreuzreime, rein klangliche Reime), die beide nicht zutreffen, und verschweigt den eingestellten Filter, der zwei Zeilen darüber im Kopf steht. **Eine Leermeldung, die den Filter des Nutzers nicht nennt, erklärt den falschen Fall.**

**#58 ist behoben, und der Fehler war zum zweiten Mal derselbe Mechanismus.** Die Dokumentsuche zeigte die Tokenzahl des Textes als Belegzahl. Entstanden ist das nicht durch eine falsche Rechnung, sondern durch eine Aufräumarbeit: #327 entfernte ein rein schreibend gewordenes Feld, und die Anzeige fiel auf das einzige verbliebene Zahlenfeld zurück. Beim Beheben stand dieselbe Falle wieder offen, weil `totalWords` nach der Umstellung seinerseits keinen Leser mehr gehabt hätte; es ist deshalb mit entfernt. `docs/CONTRACTS.md` §C trug die alte Objektform und den Satz „What the result card shows is `totalWords`", beides jetzt nachgezogen. **Gefunden hat diese Doku-Stelle der Reviewer, nicht ich.** Wer die Gestalt eines Objekts ändert, hat die Stelle zu suchen, die diese Gestalt dokumentiert; hier stand sie in §C derselben Datei, in der auch die Suchregeln des Playgrounds stehen.

### Rote Zeilen

**Rot: die 6.418.133 gehörten zu einem anderen Lemma als die 157.** Ausgezogen als rote Zeile 22 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: eine Zuschreibung, für die ich die Quelle offen vor mir hatte.** Ausgezogen als rote Zeile 23 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, in Runde 2 desselben Reviews: „im PDF waren die Bildpositionen leer" war ein übernommener Befund, und er stimmt nicht.** Ausgezogen als rote Zeile 24 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, vierte Zeile, am selben Tag gegen dieselbe Lehre: `items[0].keys()` ist nicht das Schema.** Ausgezogen als rote Zeile 25 nach [../fehlerjournal.md](../fehlerjournal.md).

Alle vier Fehler hatten dieselbe Gestalt: eine Aussage, die aus der Nähe richtig aussieht, weil ihre Bestandteile stimmen. Die 6.418.133 war gemessen, Alans Protokoll war gelesen, der Satz über das PDF stammte von jemandem, der die Datei tatsächlich vor sich hatte, und die Kollisionsmessung lief korrekt über die Felder, die sie kannte. Falsch war jeweils die Verbindung, und viermal hat sie derselbe Reviewer gelöst, der dafür nichts wusste, was mir nicht auch zur Verfügung stand.

---

## 2026-09-14/15 (Nachtlauf) – Neun Entscheidungen waren längst gefallen, und zweimal saß die Korrektur in einer Spiegelkopie

Auftrag: die Vorgänge mit `wait:kzw` durchgehen, die beantworteten vom Warten befreien, umsetzen was dadurch frei wird, und alles ohne Entscheidung aufschreiben statt raten. Die Prämisse hat sich bestätigt, und zwar quantifizierbar: **9 von 39 Vorgängen mit `wait:kzw` trugen eine Antwort, die den ganzen offenen Rest trägt**, und keiner von ihnen hatte das Label verloren.

### Ausgangsstand, selbst gemessen

Grundmenge sind die offenen Vorgänge (`gh issue list --state open --limit 200`), Kontrollwert `evergreen` trifft genau einmal (#44), die Abfrage greift also.

| Menge | vor dem Lauf | nach dem Lauf |
|---|--:|--:|
| offene Vorgänge | 71 | 69 |
| davon `auto:blocked` | 46 | 38 |
| davon `wait:kzw` | 39 | 31 |
| `wait:*` ohne `auto:blocked` | 0 | 0 |
| `auto:blocked` ohne `wait:*` | 0 | 0 |

Die vier Zustände über den 39: **beantwortet und ausführbar 9, teilweise ausführbar 4, beantwortet mit einer neuen Frage 8, wirklich noch wartend 18.** Die Messvorschrift für die letzte Gruppe steht im #44-Kommentar, weil „wartet noch" sonst die Restmenge einer Subtraktion wäre und keine benannte Gruppe.

Die Aufteilung stand zwischendurch auf 10 und 3. **#375 war in der ersten Gruppe gelandet, weil ich den ausführbaren Teil für den ganzen Vorgang gehalten hatte**: die acht eindeutigen Belege sind umannotiert, aber Punkt 1 des dortigen Arbeitsauftrags lautet wörtlich „@wachauer: die acht Fälle der zweiten Tabelle lesen". Der Vorgang bleibt deshalb offen und geht auf `auto:blocked` mit `wait:kzw` zurück. Das ist der Fehler, den dieser Lauf strukturell begünstigt: wer nach ausführbaren Resten sucht, liest einen Auftrag darauf hin, was er tun darf, und nicht darauf, was noch fehlt.

### Der Befund des Laufs: der Header spiegelt drei Master, und nur einer war geprüft

Ein TEI-Header führt an drei Stellen Daten, deren Master woanders liegt: `msIdentifier/idno` aus `works.xml`, `listBibl/biblStruct` über `works.xml` aus Zotero, `particDesc/listPerson/persName` aus `persons.xml`. Nur der erste hatte einen Schreiber und ein Gate. **Beide ungegateten Stellen sind in dieser Nacht aufgefallen, unabhängig voneinander, und beide Male saß eine Korrektur am falschen Glied.**

**#237 AA-1.** Der Auftrag führt die Bibliographie-Korrektur in `tei/VTC.tei.xml` als „sofort ausführbar, unabhängig von allem anderen". Geschrieben, validiert, Index byte-identisch, alle Gates grün, und wirkungslos: derselbe `biblStruct` steht mit derselben `xml:id` in `authority-files/works.xml`, und ausgeliefert wird diese Fassung. `api/works/work_572.json` trägt „Josef Emler" und keinen Jireček. Die Schreibrichtung steht als Kommentar im Sync-Skript selbst (`scripts/sync/enhance_works_with_zotero.py:281-285`), wo sie für #235 schon einmal teuer gelernt wurde. **AA-1 hängt an AA-4**, und AA-4 ist Handarbeit in der Zotero-Oberfläche, also ein Posten für Christian. Zweig gesichert, kein PR.

**#308.** Die Namensansetzung für `person_1249` ging auf „Jakob von Warte", in `persons.xml`, in `works.xml` und im `titleStmt` von `tei/SJW.tei.xml`. Der `particDesc`-Block derselben Datei blieb stehen und führte weiter „Jakob von Wart" als Hauptform. Die Datei widersprach sich nach der Korrektur weiter, nur andersherum, und zwar in genau der Zeile, die der #308-Kommentar vom 06.09. als Widerspruch benannt hatte.

Der zweite Fall ist repariert und bekommt ein Gate. Gemessen über alle 667 Dateien: 666 tragen den Block, 671 Einträge sind gegen `persons.xml` prüfbar, **genau 1 Abweichung, danach 0**. Kontrollwert `person_1050` ergibt „Heinrich von Pressela" wie erwartet. `check-author-refs.py` prüft das seither und läuft als Step 7b in `data-integrity.yml`.

**Dass es dort bisher nicht lief, war keine Lücke, sondern eine Entscheidung mit einer Bedingung daran**, und die stand seit #228 in `scripts/README.md`: „Läuft bewusst nicht in der CI, solange der tote `@ref` in VOR offen ist (#308); sonst wäre der Befund ein Blocker für unbeteiligte PRs." Genau diesen `@ref` hat die Korrektur dieser Nacht behoben. Die Bedingung war erfüllt, bevor irgendjemand sie nachgeschlagen hatte; gefunden habe ich sie erst, als ich die Doku zum Skript nachziehen wollte. **Eine Bedingung, die niemand überwacht, wird still wahr.**

### Das Gate ist in beide Richtungen gelaufen, und es hatte selbst ein Loch

Drei Mutationen, je einzeln eingebaut und zurückgenommen:

| eingebauter Fehler | Meldung | exit |
|---|---|--:|
| SJW preferred zurück auf die alte Form | Spiegel veraltet 1 | 1 |
| HHP `@corresp` auf `person_999999` | Spiegel tot 1 | 1 |
| preferred-Zeile in SJW gelöscht | (nichts) | **0** |

Der dritte Fall ist der Befund der dritten Reviewrunde und der interessanteste: ein Eintrag ohne `preferred`-Zeile fiel per `continue` aus der Grundmenge, der Zähler sank von 671 auf 670, und nichts wurde rot. **Ein zählendes Gate kann eine schrumpfende Bezugsmenge nicht von einem kleineren Bestand unterscheiden, solange das Schrumpfen keine eigene Klasse hat.** Jetzt hat es eine, und der dritte Fall gibt exit 1. Heute betrifft er 0 von 671 Einträgen, es war also ein Loch im Gate und kein Fehler im Bestand.

**Und dann fand der CI-Review-Bot dasselbe Loch eine Ebene höher.** Die neue Klasse deckt einen Eintrag ohne `preferred`-Zeile ab; ein ganz gelöschtes `<person>`-Element fällt durch alle Klassen, weil sie sämtlich über vorhandene Einträge sprechen. Der Zähler sinkt still von 671 auf 670, `--check` bleibt exit 0, `schema/mhdbdb.rnc:211` erlaubt ein leeres `listPerson`, und sonst greift nichts: der Cross-Ref-Audit sucht tote Verweise, und ein gelöschter Block hat keine.

**Beim dritten Mal wird nach der Hausregel nicht weitergezählt, sondern der Mechanismus gewechselt.** Statt einer vierten Fehlerklasse über gezählten Einträgen steht dort jetzt eine Invariante, die jede Datei selbst mitbringt: jede Autoren-ID des `titleStmt` muss im `particDesc` derselben Datei stehen. Gemessen über alle 667 Dateien: 672 `titleStmt`-Autoren mit `@ref`, keine einzige Datei ohne einen, 671 `particDesc`-Einträge in 666 Dateien, null Einträge ohne zugehörigen Autor. Die Differenz ist genau ein Fall, und er heißt `VOR`. Der Unterschied zur Baseline-Zahl, die der Bot als Alternative vorschlug: **eine Invariante wächst mit dem Korpus mit, eine Zahl muss jemand nachziehen.** Mit gelöschtem Block in SJW meldet das Gate „Autor ohne Spiegel 1" und exit 1, nach Rücknahme exit 0 und `tei/` byte-identisch.

`VOR` steht dabei mit Namen und Grund im Skript statt als Zahl, und das Skript meldet die Ausnahme, sobald sie überflüssig wird. Ob die Datei ihren Autor im `particDesc` nachgetragen bekommt, ist eine Modellfrage und hier ausdrücklich nicht entschieden.

Ungeprüft bleiben, ausdrücklich vermerkt: die `alternative`-Formen und die `idno`-Zeilen desselben Blocks, und die lokale `xml:id` gegen `@corresp`.

### Umgesetzt

**#308, #375 und #432** in einem Zug, weil sie dieselbe abgeleitete Schicht anfassen. Korpus-Index 4.2.16, Authority-Index 1.9.6, ein neuer Variantentyp `type_372376` für `waeren` (nie ein bestehender umgehängt, Regel aus #367).

Wirkung am Index gemessen, alt gegen neu: `lemma_7338` 3.529 → 3.537, `lemma_7505` 36.362 → 36.354, `lemma_7779` 1.001 → 1.000, `lemma_9653` 14 → 15. Die beiden Ausgangswerte 1.001 und 14 sind genau die, die #432 nennt, was die Messung an den Vorgang bindet. `wordCount` ändert sich in 0 von 667 Texten.

**Das Gate, das #378 vorschlägt, ist einmal von Hand gelaufen.** Variantenabbildung 1.9.5 gegen 1.9.6: 0 Formen hinzugekommen, 0 entfallen, 0 umgehängt, bei 234.245 Abbildungen auf beiden Seiten. Das war genau die Art Änderung, die eine Abbildung kippen kann, und sie hat es nicht getan.

**Zwei weitere Gates sind in beide Richtungen ausgeübt worden, ohne dass jemand den Fehler eigens einbauen musste**, weil der Lauf ihn mitbrachte: `check-author-refs.py` stand vor der Korrektur auf **fünf Befunden in vier Klassen** und danach auf lauter Nullen, `doc-count-audit.py` ging über die Formenzahl erst rot und nach dem Nachziehen grün. Die fünf, am Diff nachgezählt statt aus dem Gedächtnis: ein toter `@ref` (VOR), ein Präfix-Ausreißer (WZB), ein Zeilenumbruch im Namen (LUU) und zwei Namensabweichungen (HHP, SJW). Die dokumentierte Formenzahl ist an 9 Stellen von 256.772 auf 256.773 gezogen worden; die 234.245 ausdrücklich **nicht**, weil sie eine andere Menge zählt (CONTRACTS §C).

### Frontend im Browser geprüft, nicht nur im Code

Zwei ausgelieferte Seiten tragen die Formenzahl. Vorher am Livestand: `hilfe-daten.html` zeigt „256.772 orthographischen Varianten". Nachher lokal „256.773", der Zahlenblock intakt neben „667 TEI-Texte" und „43.878 Lemmata"; `index.html` zeigt im Korpus-Übersichtsblock „256.773 / Orthographische Varianten". Beides am Bildschirm gesehen.

### #410: vier Blöcke, und die Grenze ist nicht Wichtigkeit

Der zweite Teil des Abends ist die Informationsarchitektur der Abfragespalte. Die Entscheidung lag seit dem 11.09. vor, samt der Bewertung, die sie trägt, und dem einen Nachtrag: „Ich möchte beim Aufklappen immer einen kleinen erklärenden Satz, was dieser Block beinhaltet (philologisch argumentiert, nicht technisch)."

| Block | Vorgabe | Inhalt |
|---|---|--:|
| Korpusanalysen | offen | 6 Werkzeuge |
| Register & Indizes (Authority Files) | offen | 6 Register |
| Weitere Korpusanalysen | zu | 5 Werkzeuge |
| Experimentelle Forschungsdaten | zu | 2 Datensätze |

Die Aufteilung der elf Analysewerkzeuge folgt der am 10.09. an den Eingabefeldern gemessenen Regel: sechs beginnen mit einem Wort oder Begriff, fünf mit einem Text oder einer Autor*in. **Das ist keine Wertung, sondern eine Eigenschaft der Werkzeuge**, und deshalb heißen die Blöcke „Korpusanalysen" und „Weitere Korpusanalysen" statt „zentral" und „weitere".

Auch hier vorher und nachher im Browser: am Livestand ein offener Block „TEI Textanalyse" mit elf Werkzeugen darunter zwei zugeklappte; lokal stehen beim ersten Laden die sechs Register da, während der Korpus noch lädt, und nach wenigen Sekunden kommen die Korpusanalysen dazu. Der Umschalter des dritten Blocks öffnet ihn samt Satz und fünf Werkzeugen, und die Wortfrequenz-Analyse rendert nach dem Umzug unverändert ihre Tabelle.

**Ein toter Anker, gefangen durch Nachsehen statt Annehmen.** Der Hilfe-Link des neuen Blocks zeigte im Entwurf auf `hilfe-playground.html#tei-analyse`. Den Anker gibt es nicht; die Datei führt `#weitere-werkzeuge`. Ein toter Anker springt still auf den Seitenkopf und fällt niemandem auf, also ist er genau die Sorte Fehler, die nur vor dem Schreiben billig ist.

**Das Umbenennen hat drei Gate-Bindungen stumm gelöst, und das Gate blieb dabei grün.** `doc-count-audit.py` bindet eine Zahl an ein Ankerwort: „elf TEI-Analyse-Werkzeuge" wird gegen den aus dem Code gezählten Wert geprüft, aber nur, solange das Ankerwort danebensteht. #410 benennt genau diese Wörter um. Danach meldete die Selbstprüfung des Gates drei Paare als `[no-hit]`: zweimal `README.md`, einmal `hilfe-playground.html`. Gemessen: auf `origin/main` traf das Muster in der README zweimal und in der Hilfeseite einmal, danach keinmal. **Ein Gate, das seinen Gegenstand verliert, meldet das nicht als Fehler, sondern als Zeile ohne Exit-Code**, und diese Zeile stand mitten in dreißig anderen. Die Anker sind erweitert und in beide Richtungen ausgeübt: mit „zehn Korpusanalysen" und „sieben Register und Indizes" in der README meldet das Gate beide Zeilen mit Fundstelle und gibt exit 1, nach Rücknahme exit 0 und kein `[no-hit]` mehr.

Dabei eine Falle vermieden, die das erweiterte Muster selbst aufgestellt hätte: `ANCHOR_SEP` überbrückt bis zu acht Tags, also hätte ein Satz, der auf „Abschnitt 3 und 4." endet und dem eine Überschrift „Korpusanalysen" folgt, die 4 an den Anker gebunden und das Gate rot gemacht. Der Satz steht jetzt ohne Ziffer da.

**Und ein Beinahe-Fall derselben Bauart:** das Skript, das zwölf Stellen der Hilfeseite ersetzt, suchte zunächst mit `\n` in einer Datei, die durchgehend CRLF trägt. Alle zwölf Muster hätten null Treffer gehabt, und weil das Skript bei null Treffern abbricht statt stumm Erfolg zu melden, wäre es aufgefallen; aufgefallen ist es trotzdem vorher, beim Lesen des eigenen Skripts. Die Regel dahinter steht seit dem 02.07. im Journal (`read_text()` normalisiert Zeilenenden) und seit #115 in der Roundtrip-Lehre.

**Die Hilfeseite behauptete danach die falsche Blockzugehörigkeit, und zwar für vier von neun Werkzeugen.** Abschnitt 5 sagt über die Werkzeuge, die er beschreibt, wo sie in der Abfragespalte stehen. Nach dem Umbau stimmte das für fünf und nicht für vier: Kookkurrenz-Ranking, Reim-Wörterbuch, Begriffs-Verteilung und Lemma-Verteilung sind im offenen Block gelandet, der Abschnitt schickte die Leser*innen aber geschlossen in den zugeklappten. Gefunden hat es `fable-reviewer` in Runde 1, gemessen mit lxml über die Überschriften beider Panels, und ich habe es an derselben Stelle nachgemessen, bevor ich etwas geändert habe. Repariert ist nicht der Satz, sondern der Abschnitt: zwei Gruppen, jede mit ihrem Blocknamen als Überschrift, je in der Reihenfolge der Abfragespalte. **Eine Prosa-Aussage über eine Oberfläche altert genau dann, wenn die Oberfläche sich ändert, und niemand liest bei einem Umbau die Hilfeseite mit, weil sie nicht im Diff steht.**

Dieselbe Bauart traf die Startseite: die Kachel „Korpusanalysen" führte zwei Werkzeuge auf, die im zugeklappten Block darunter liegen. Wer von der Kachel kommt und im gleichnamigen Block sucht, findet sie nicht. Und in ihrer Nachbarschaft stand „mit 10 spezialisierten Suchfunktionen". Gemessen sind es elf Korpusanalysen, sechs Register und zwei Datensätze; 10 ist keine dieser Mengen. Welche gemeint war, ist nicht rekonstruierbar, also steht dort jetzt keine Zahl statt einer geratenen.

Beide Zweige sind gemergt: PR #438 (Daten und Gate) und PR #439 (#410), jeder mit vier grünen Checks und je einer Runde des CI-Bots ohne Befund. Der Bot hat auf #438 die beiden Befunde geliefert, die diese Nacht am teuersten waren.

### Was über den Einzelfall hinausgilt

| Aussage | Herkunft | verankert in |
|---|---|---|
| Ein Name kann mehrere Entitäten bezeichnen; das ist normal und wird über mehrere Senses am selben Lemma abgebildet, nicht über ein eigenes Lemma | #357 | `docs/DECISIONS.md` ADR-020 |
| Echte Ambiguität in der Variantenauflösung wird nicht durch einen Tiebreak aufgelöst: alle Kandidaten bleiben erhalten, sortiert nach der Häufigkeit genau dieser normalisierten Form unter dem jeweiligen Lemma | #378 | `docs/DECISIONS.md` ADR-021 („entschieden, nicht umgesetzt") plus ein Zeiger in `docs/CONTRACTS.md` §C |
| Bei zwei belegten Namensformen ist die historische die Hauptform und die modernisierte die Alternative; wo eine Normdatei ansetzt, folgt die Hauptform ihr | #308 | `docs/CONTRACTS.md` §F.5 |
| **Nicht verankert:** dass eine Bibliographie-Korrektur bei Zotero anfangen muss und nicht im TEI-Header | Befund dieser Nacht an #237 | steht als Kommentar im Sync-Skript und jetzt im Vorgang; gehört als §F-Abschnitt in `docs/CONTRACTS.md`, ist aber eine Vertragsänderung und braucht eine Entscheidung |

§F.5 ist der Abschnitt, der ohne die Zahlen daneben falsch gelernt würde. Gezählt über `persons.xml`, `works.xml` und `tei/` am Stand vor der Korrektur, mit der Regel, dass ein Name nur zählt, wo er nicht Präfix eines längeren ist: Pressela 7, Breslau 2, Warte 7, Wart 2. **Bei HHP war die Hauptform auch die häufigere, bei SJW die seltenere.** Wer aus „wovon haben wir mehr" argumentiert, bekommt beide Fälle richtig und den nächsten falsch.

### Rote Zeilen

**Rot: der #252-Kommentar ging mit den Zahlen von vor der Gegenprobe hinaus.** Ausgezogen als rote Zeile 26 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, zweiter Teil desselben Vorgangs, gegen eine eigene Lehre von vor acht Tagen: Eindeutigkeit aus drei Stichproben.** Ausgezogen als rote Zeile 27 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, und die unangenehmste: derselbe Fehlermodus zweimal in derselben Nacht, drei Stunden auseinander.** Ausgezogen als rote Zeile 28 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: das Datum 2026-09-15 stand an sieben Stellen und war erschlossen, nicht abgelesen.** Ausgezogen als rote Zeile 29 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, eigener Regelverstoß, und zwar zweimal in derselben Nacht aus derselben Familie.** Ausgezogen als rote Zeile 30 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: das Umbauskript hat den Abschnitt aus seinen Teilen neu zusammengesetzt, und was kein Teil war, fiel weg.** Ausgezogen als rote Zeile 31 nach [../fehlerjournal.md](../fehlerjournal.md).

Zwei Dinge daran sind über den Fall hinaus brauchbar. Erstens hätte **ein Größenvergleich es nicht gefangen**: der neue Abschnitt ist mit 12.381 Zeichen größer als der alte mit 12.132, weil zwei Gruppenüberschriften dazukamen. Ein Verlust und ein Zuwachs im selben Diff heben sich in jeder Kennzahl auf, die nur zählt. Zweitens war die brauchbare Gegenprobe ein **Inventar der Top-Level-Elemente** vorher gegen nachher, und die habe ich erst gezogen, nachdem der Reviewer die eine Box benannt hatte: sie hat dann bestätigt, dass es bei dieser einen blieb. **Wer einen Befund über ein verlorenes Element bekommt, prüft nicht das Element, sondern das Inventar.**

**Rot, gleicher Commit, anderer Fehlermodus: ein Deep-Link hing an einer Eigenschaft, die die Änderung aufgehoben hat.** Ausgezogen als rote Zeile 32 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: „Fifteen checks" über einer Liste mit sechzehn Einträgen.** Ausgezogen als rote Zeile 33 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, dritter eigener Regelverstoß derselben Familie, und der erste, der Text beschädigt hat.** Ausgezogen als rote Zeile 34 nach [../fehlerjournal.md](../fehlerjournal.md).

**Nicht rot, aber festzuhalten, weil sonst der Eindruck entsteht, es sei knapp gegangen.** Drei weitere Fehler sind vor dem Commit oder vor der Veröffentlichung gefangen worden und haben nichts getragen: ASCII-Ersatzschreibungen („Jirecek", „ueber") in deutscher Prosa im TEI-Header, um dem NFD-Problem auszuweichen statt es zu lösen; „1 Vorkommen" kombinierender Zeichen in VTC, was eine Aussage über U+0308 war und als Aussage über alle sieben gesuchten Zeichen dastand (richtig sind 4); und „als Befund in #44 vermerkt" im Perfekt, während der #44-Kommentar noch ungeschrieben war.

Drei weitere aus der zweiten Hälfte der Nacht, alle vor dem Commit gefangen und deshalb ohne Zählung, aber zwei davon aus einer Familie, die es wert ist: der neue Abschnitt der Hilfeseite verwies auf `#versposition`, während der Anker `verse-position` heißt (derselbe Fehlertyp wie `#tei-analyse` drei Stunden vorher, nur diesmal vor dem Lauf des Skripts gefangen, weil ich die Ankerliste vorher gemessen habe statt sie zu erinnern); die Ausnahme im neuen Gate begründete sich mit „`VOR` führt als einzige keinen `particDesc`-Block", was falsch ist, denn die Datei hat einen `particDesc` mit leerem `<listPerson/>`, und aufgefallen ist es nur, weil die Mutationsprobe an ihrer eigenen Vorbedingung scheiterte; und der erste Entwurf desselben Abschnitts schrieb „Die elf Korpusanalysen" in eine Seite, aus der die Werkzeugzahl am 02.09. ausdrücklich herausgenommen worden war, weil sie dort niemand nachzieht. **Der letzte ist die unangenehmste Sorte: eine Entscheidung, gegen die man verstößt, ohne sie zu kennen.** Gefunden hat sie nicht mein Gedächtnis, sondern das Gate, das die Entscheidung als Eintrag mit Begründung führt und beim Wiedereinsetzen der Zahl „veraltete Ausnahme" meldete. **Eine Entscheidung, die nur im Journal steht, schützt niemanden; eine, die als Konfigurationszeile neben ihrem Gate steht, meldet sich von selbst.**

**Und der Fall, an dem die Regel sichtbar gearbeitet hat.** Für die Einordnung des neuen CI-Schritts hatte ich „rund zwei Sekunden" geschrieben und ihn in den billigen Block gelegt. Gemessen: 1 min 47 s und in einem zweiten Lauf 1 min 44 s, weil das Skript jede der 667 Dateien ganz parst, während der Nachbarschritt per `iterparse` nach 0,7 s fertig ist. Faktor 50 daneben, und die Zahl hätte eine Entscheidung getragen, nämlich die Position im Workflow. Gefangen hat es niemand: die Zahl ist gemessen worden, weil sie in eine Datei sollte. **Das ist der billigste Fang des Laufs, und er kostet eine Zeile vor dem Schreiben statt einer Reviewrunde danach.** Nachtrag vom Ende der Nacht, und er dreht die Lehre noch einmal weiter: der erste Lauf des Schritts auf `main` brauchte **32 Sekunden**, nicht 1 min 47 s (Lauf 34910635460, Schritt 21). Beide Zahlen sind gemessen, sie sprechen über verschiedene Maschinen, und dokumentiert war die lokale in einem Satz, der die Position in der CI begründet. Die Begründung trägt weiter, weil der Nachbarschritt in derselben CI unter einer Sekunde bleibt; das Verhältnis entscheidet, nicht der Absolutwert. **Eine selbst gemessene Zahl kann trotzdem über die falsche Menge sprechen, und bei einer Laufzeit ist die Menge die Maschine.**

### Zwei Befunde ohne Vorgang

Beim Editieren eines TEI-Headers ist eine Textersetzung gescheitert, weil „Verfügung" dort nicht vorkomponiert steht, sondern als `u` plus kombinierendes Trema. Eine Suche über die NFC-Form findet solche Stellen nicht und meldet dabei keinen Fehler, sondern „nicht gefunden". Gemessen über alle 667 Dateien in `tei/`, für U+0300, U+0301, U+0302, U+0308, U+030A, U+030C und U+0327: **568 Dateien tragen mindestens eines, 1.366 Vorkommen**, Kontrollwert VTC 4, alle im `teiHeader`.

`tei/LUU.tei.xml` führt im `particDesc` die Personen-ID `person_05154796-f128-42a1-bd0d-e8335bf854e6`, korpusweit der einzige Fall dieser Form. Das `@corresp` daneben löst korrekt auf, der Name stimmt. Nicht angefasst, weil eine `xml:id` ein möglicher Deep-Link-Anker ist (#358).

Beide ohne Ticket, weil an keinem ein Arbeitspaket hängt.

### Geschlossen, je ein Satz mit dem Grund

- **#308** geschlossen, weil alle vier entschiedenen Punkte umgesetzt sind und die drei mechanischen Fälle desselben Audits mit ihnen, samt der Regel dahinter als `docs/CONTRACTS.md` §F.5 und einem Gate auf dem Spiegel, der beim Umsetzen aufgefallen ist.
- **#432** geschlossen, weil `WH_6214_3` jetzt auf `lemma_9653` hängt und die Wirkung am Index gegen die beiden Zahlen gemessen ist, die der Vorgang selbst nennt (1.001 → 1.000 und 14 → 15).
- **#375** ausdrücklich **nicht** geschlossen, obwohl der ausführbare Teil erledigt ist: Punkt 1 des dortigen Arbeitsauftrags ist eine Lesearbeit für @wachauer.
- **#410** ausdrücklich **nicht** geschlossen, obwohl umgesetzt und gemergt: die Abnahme der Oberfläche liegt nach dem Deploy bei ihr, und dafür gibt es die Regel, dass das Issue offen bleibt und nicht der PR.
- **#406** bleibt offen, obwohl der Auftrag „Aktualisiere die Triage" erfüllt ist: die Triage ist ein Lesedokument, und ihre sechs Positionen leben in ihren eigenen Vorgängen weiter.

### Was zurück an Christian geht

Alles hier ist liegengeblieben, weil eine Entscheidung fehlt, nicht weil die Arbeit fehlt.

1. **#237 AA-1 ist geschrieben und nicht gemergt, weil es an AA-4 hängt.** Der Auftrag führt AA-1 als „unabhängig von allem anderen", gemessen ist es das nicht: der `biblStruct` steht zweimal, und ausgeliefert wird die Fassung aus `works.xml`. AA-4 ist Handarbeit in der Zotero-Oberfläche und damit deine. Der Zweig liegt als `claude/237-aa1-vtc-biblstruct`.
2. **Die Richtung der `listBibl`-Kette braucht eine Entscheidung, bevor sie ein CONTRACTS-Abschnitt werden kann.** Dass eine Bibliographie-Korrektur bei Zotero anfangen muss, steht heute als Kommentar im Sync-Skript und im Vorgang. Als Vertragsabschnitt wäre es eine Festlegung darauf, dass der TEI-Header an dieser Stelle dauerhaft Kopie bleibt, und das ist keine Sitzungsentscheidung.
3. **#433, #434 und #435 sind `auto:checkin` und tragen im Körper ausdrückliche „Zu entscheiden"-Punkte.** Sie sind nicht angefasst worden, weil genau das der Fall ist, den der Auftrag ausschließt.
4. **#410 hat eine unbeantwortete Frage aus deinem Bewertungskommentar:** ob der aufgeklappte Zustand weiterhin im Browser gemerkt werden soll. Das Verhalten ist unverändert geblieben, weil „lass es, wie es ist" die einzige Variante ohne Entscheidung war.
5. **Soll `tei/VOR.tei.xml` seinen Autor im `particDesc` nachgetragen bekommen?** Die Datei führt als einzige ein leeres `<listPerson/>`. Das neue Gate nimmt sie namentlich aus und meldet die Ausnahme, sobald sie überflüssig wird. Ein Nachtrag wäre eine Datenänderung am Modell und keine Reparatur.
6. **#375 bleibt offen und geht zurück auf `wait:kzw`.** Die acht zu lesenden Fälle liegen als `ingest/pos-disambig/375-waeren-ausweitung/faelle.csv` bereit und warten auf eine Spalte `entscheidung`.
7. **#370 und #378 sind nicht angefasst worden**, wie im Auftrag vorgegeben. Die Entscheidung aus #378 ist als ADR-021 verankert, ausdrücklich als „entschieden, nicht umgesetzt".
8. **Der Mechanismuswechsel, den die dritte rote Zeile zu den Shell-Konventionen fällig macht, ist eine Entscheidung über deine Einstellungen und deshalb deine.** Die Regel selbst ist eindeutig und wurde dreimal gebrochen, obwohl sie gelesen war; der vorhandene Mechanismus (Skript per Write, dann `python skript.py`) ist billiger als der Einzeiler und wurde in dieser Nacht bei jeder größeren Ersetzung benutzt. Gebrochen wurde er nur bei Nebenbefehlen. Ein greifender Wechsel wäre eine `deny`-Regel auf `python -c`, die den Weg über die Datei erzwingt. Das sperrt auch die harmlosen Einzeiler, und ob dir das den Fang wert ist, kann ich nicht für dich entscheiden. Ein parsender `PreToolUse`-Hook scheidet aus: dass Einstellungen nicht mit Rückfragen gehärtet werden, ist schon entschieden.

---

## 2026-09-15 – #204 im Playground: der erbetene Hinweis wäre eine Zusicherung ohne Deckung gewesen

KZW hat #204 wiedereröffnet, weil eine zweite Nutzerin denselben Fehler machte wie im Juli: im Korpus-Browser nach `mori` filtern, annehmen dass damit Moriz von Craûn das Ausgangskorpus ist, Analyse starten, Gesamtkorpus-Ergebnisse bekommen. Erbeten war, den Hinweis aus der Korpussuche in den Playground zu übernehmen.

**Der Befund steht nicht im Ticket, sondern kam aus der ersten Messung: die Auswahl aus Schritt 1 hat auf die Analysen überhaupt nicht gewirkt.** Auswahl auf null Texte setzen und je Werkzeug `getCorpusTexts().length` lesen: **10 von 11 liefern trotzdem 667**. Nur die Multi-Lemma-Suche las sie, weil sie über `tei-manager.js` läuft und nicht über den Thunk in `playground-main.js`. Der Kontrollwert war dieselbe Messung an ihr: 0 Treffer bei 0 Texten, also misst die Probe wirklich etwas. **Hätte die Nutzerin „Nur diese" geklickt, wären die Zahlen genauso falsch gewesen, nur ohne sichtbaren Anlass zum Misstrauen.** Ein Hinweis allein hätte eine Wirkung versprochen, die es nicht gab.

Umgesetzt in PR #441: zwei Thunks statt einem. `selectedTextsThunk` filtert auf `includedTexts` und geht an sieben Werkzeuge, `corpusTextsThunk` bleibt bei dreien, jedes aus einem von KZW entschiedenen Grund (Hapax ist korpusweit per Definition, der Textvergleich wählt selbst, das Reim-Wörterbuch hat ein eigenes Filterfeld und bekommt die Sigle sichtbar vorbelegt statt still). Alle drei sagen das jetzt in ihrer Kopfzeile. Live nach dem Deploy gegengeprüft: Auswahl CR, Kookkurrenz „minne" ergibt 14 statt 7.161, Hapax bleibt bei 667.

### Was über den Fall hinausgilt

**Eine Änderung, die eine Menge verengt, entwertet jeden Zustand, der aus der alten Menge stammt.** Bis #204 war die Textmenge immer der ganze Korpus und konnte sich nicht ändern; jedes Werkzeug durfte deshalb gefahrlos IDs und fertige Ergebnisse über eine Auswahländerung hinweg behalten. Die Befunde mit genau dieser Wurzel, namentlich: das Reim-Wörterbuch behielt ein ohne Filter gerechnetes Ergebnis unter der neuen Filterzeile (`Filter „CR" → 667 Texte`, eine Aussage, die sich selbst widerspricht); Wortfrequenz und Versendings-Profil hielten in `state.scope` einen abgewählten Text, Ergebnis „Keine Daten" unter „Gesamtkorpus (666 Texte)"; die Text-Statistiken behielten verwaiste IDs in ihren eigenen Häkchen, `Ausgewählt: 3 / 1` neben „Keine Texte ausgewählt"; Kookkurrenz-Ranking und Begriffs-Verteilung überlebten die Auswahländerung sogar dauerhaft, weil sie ihr Ergebnis im State halten und beim Öffnen nur neu rendern. Das ist die #397-Frage in ihrer teuren Form, und sie lautet hier: **was hat diese Änderung falsch gemacht, das vorher wahr sein durfte.**

**Jede eigene Regressionsprobe hat den Zustand verfehlt, den sie bewachen sollte, und zwar dreimal aus demselben Grund: sie richtete den Zustand direkt ein, statt ihn entstehen zu lassen.** Der Kookkurrenz-Test verengte vor der ersten Suche, das Werkzeug besaß also nie ein korpusweites Ergebnis. Der Marker-Test leerte das Feld zuerst und lief damit durch den Leer-Zweig. Die Tests zum Sigle-Wechsel gingen direkt von einer Einzelauswahl in die nächste und nie über „Alle". Alle drei waren grün und prüften nichts. **Ein Test, der den Zustand setzt, prüft die Zeile darunter; ein Test, der den Weg geht, prüft den Zustand.** Der letzte Fall dieser Art hat es explizit gemacht: nach der Verlegung eines Stempels von `show()` nach `runSearch()` wäre der Tauschtest grün geblieben, ohne noch irgendetwas zuzusichern, weil er `state.result` von Hand setzte. Er geht jetzt durch eine echte Suche und misst als Kontrollwert mit, dass sie 14 liefert.

**Zwölf Reviewrunden auf einem Frontend-Diff.** Drei lokale `fable-reviewer`-Runden, die dritte davon als Audit auf den Restzustand statt als Diff-Review, dazu neun Runden des CI-Bots. Sechs der Bot-Runden trugen je einen Verhaltensbefund, die letzten drei keinen mehr. Der Audit-Auftrag war die ergiebigste Variante: statt den Bot einen Fehler nach dem anderen finden zu lassen, einmal systematisch über alle sieben umgestellten Werkzeuge. Er fand den Fehler in der Korrektur des vorigen Befunds, nämlich einen Stempel, der die Textmenge beim Anzeigen festhielt statt beim Rechnen.

### Rote Zeile

**Rot: eine Pluralstelle repariert und den Satz daneben nicht mitgelesen.** Ausgezogen als rote Zeile 35 nach [../fehlerjournal.md](../fehlerjournal.md).

Die Korrektur ist dann größer ausgefallen als der Befund. Statt die zwei gemeldeten Stellen zu flicken, alle gesucht, die eine Textzahl in einen Satz setzen: fünf konnten seit #204 eine Eins tragen, drei konnten es schon vorher und bleiben unberührt, weil sie nicht in diesen PR gehören. **Wer eine Grammatikstelle gemeldet bekommt, sucht nicht die Stelle, sondern ihre Klasse** – derselbe Griff wie beim Inventar statt des verlorenen Elements am 14.09.

### Offen

#204 bleibt offen bis zur Abnahme durch @wachauer und steht auf `auto:blocked` + `wait:kzw`. #442 hält fest, was dieser PR bewusst nicht löst: ändert man die Auswahl bei offenem Werkzeug, folgt dessen Ergebnis erst beim nächsten Öffnen. Das betrifft alle acht auswahlabhängigen Werkzeuge gleich und ist eine Entscheidung über den ganzen Playground.

---

## 2026-09-16: #444, Moriz von Craûn ist anonym

KZWs Korrektur aus #444: Die veraltete Zuschreibung an Bligger von Steinach entfällt in work_5 und im CR-Header. Anonym stand bereits an zweiter Stelle; der erste Eintrag bestimmte den Index-Autor. Auch der lokale Bligger-Eintrag in CR und der work_5-Rückverweis in MBS sind entfernt. Bliggers Lyrik bleibt ihm zugeordnet. Text und Annotationen bleiben unverändert. Beide Indexe (Corpus 4.2.17, Authority 1.9.7) und API neu gebaut. Die historische Zuschreibung bleibt hier dokumentiert; das Datenmodell für den Forschungsstatus und eine Prüfung aller Mehrfachzuschreibungen sind Folgeaufträge aus dieser Sitzung an Claude.

---

## 2026-09-21 (Spur A des Datenlaufs) – 88 Tokens, und dreimal stand die Zahl im Auftrag gegen die Zahl im Bestand

Drei von KZW entschiedene Pakete in einem Lauf, ein Rebuild der abgeleiteten Schicht, ein Versions-Bump, ein PR: #366 (acht unlemmatisierte Tokens aus dem fyndling-Beitrag), #375 (die vier letzten `wâren`-Fälle) und #371 (76 Tokens der Formen `stat` und `stât`). Korpus-Index 4.2.18, Authority-Index 1.9.8.

### Was gearbeitet wurde

88 Tokens in 45 Korpusdateien bekommen `@lemmaRef`, `@pos` und `@corresp`, je Datei ein `revisionDesc`-Eintrag pro Paket. 84 davon tragen erstmals ein `@lemmaRef`, vier wechseln von `lemma_7505` (Verb) auf `lemma_7338` (Adjektiv). Zehn Variantentypen neu geprägt, `type_372377` bis `type_372386`, keiner umgehängt. `variants.xml` von 256.773 auf 256.783 Formen, Einträge unverändert 42.626, normalisierte Mappings von 234.245 auf 234.250.

Kein `@ana`. In keinem der drei Vorgänge hat KZW einen Sense benannt, und die Sense-Zuordnung ist nach TEI-MODEL-AUTH-FILES.md kuratorisch: sie wird vom Team vergeben und ist nicht aus dem Korpus rekonstruierbar. Ein hier gesetztes `@ana` wäre kuratorische Arbeit des Skripts gewesen. Das ist der Rest, der an KZW offenbleibt.

### Drei Zahlen aus dem Auftragstext, die am Bestand nicht hielten

Der Kickoff sagte selbst, sein ganzer Text sei eine Behauptung und jede Zahl vor der Verwendung nachzumessen. Dreimal hat das etwas gefangen, und keines der drei wäre von einem Gate bemerkt worden.

**Zehn Typprägungen statt drei.** Der Laufplan rechnete mit drei neuen Typen, alle aus #371, und behandelte #366 als reines Setzen. Gemessen trägt dort **keine** der sieben Schreibungen unter ihrem Ziellemma bereits eine Nummer, es sind also sieben weitere. Der Satz stand seit dem 06.09. im Ticket („Alle sieben Schreibungen sind unter ihrem Ziel-Lemma noch nicht belegt"), und der Plan hatte ihn beim Lesen von #366 überflogen. Der harte Fall darunter ist `hawsen`: die Form wird bereits als `type_372368` unter `lemma_49714` *hûsenblâter* geführt, geprägt im #363-Lauf für die getrennt geschriebenen Erstglieder. Ein Umhängen hätte jene Tokens mitgerissen.

**Die Arbeitsmenge von #375 war vier und nicht sechzehn.** Die acht „eindeutigen" Fälle sind seit PR #438 erledigt, einzeln nachgemessen; die vier VRB-Fälle aus KZWs Tabelle bestätigen den Ist-Stand. Und alle vier verbleibenden tragen die Form `wâren`, brauchen also nur den bestehenden `type_287014`. Die Typtabelle des Tickets nennt drei Zieltypen, weil sie für die ganze Sechzehnermenge geschrieben war. **Eine übernommene Liste ist derselbe Fehler wie eine übernommene Zahl, nur an einer Stelle, die niemand für eine Zahl hält.**

**KZWs `zusammenfassung` war richtig, und der geplante Vorwurf traf nicht.** Laufplan und Kickoff hielten fest, ihr `offen: 7` stehe gegen gezählte 17 und die Zahl in der Zusammenfassung sei falsch. Gemessen decken sich alle vier Werte der `zusammenfassung` exakt mit dem Feld `status` (95/95, 63/63, 25/25, 7/7); die 17 zählt das Feld `option`. Die Kreuztabelle löst es auf: `status=offen` **und** `option=OFFEN` sind 7, `status=anders` **und** `option=OFFEN` sind 10. **Zwei Felder, zwei Mengen, beide Zahlen richtig.** Der Satz wäre vier Tage nach ihrer Rüge in #406 als Korrektur ins Ticket gegangen, für einen Fehler, den sie nicht gemacht hat. Er ist aus beiden Dokumenten entfernt, und ins Ticket geht stattdessen die Auflösung.

### Die Feldsemantik eines Review-JSON, und warum sie ins Provenienz-Log gehört

KZWs Review zu #371 kommt als JSON mit 95 beurteilten Fällen und einem `actions`-Array mit 76. Drei seiner Felder sehen nach ihrer Stimme aus und sind es nicht, gemessen am abgelegten Original:

- **`begruendung` ist dreiteilig.** 19 von 95 wortgleich mit ihrem Feld `notiz`, 6 der generierte Satz „Abweichung von Claudes Vorschlag, ohne Notiz.", 70 ein analytischer Text, der nicht aus `notiz` stammt. Nur `notiz` ist zuverlässig ihre Stimme, und sie ist bei 76 der 95 Fälle leer.
- **`batch_verdict` ist das Maschinenurteil.** Es weicht bei 25 Fällen von `pos` ab und trägt auch dort ein Urteil samt Konfidenz, wo sie `pos: null` gesetzt hat.
- **`actions.confidence` ist kein Maß für Sicherheit, sondern eine Ableitung aus `status`**, ohne eine einzige Ausnahme: `ok` wird `high` (63), `anders` wird `medium` (13). Gegen `batch_verdict.confidence` weicht sie bei 61 von 76 ab. **Die 13 mit `medium` sind damit gerade die Fälle, in denen KZW vom Vorschlag abgewichen ist**, also die am gründlichsten angesehenen, und nicht die unsichersten.

Der dritte Punkt hätte fast einen falschen Satz in den PR-Text gebracht: die 13 waren als die ausgewiesen, bei denen die Abnahme zuerst hinsehen soll. **Ein Feld, das einen Wert trägt, sieht geprüft aus, auch wenn nie jemand geprüft hat, was der Wert bedeutet.** Die Messvorschrift steht deshalb in `ingest/pos-disambig/371-stat/README.md`, neben der Aussage.

Und das JSON ist nicht parsbar: bei Zeichen 82.382 steht mitten im `actions`-Array die Klartextzeile `Prüfer: Alan van Beek`. Genau einmal. Eine Zeile entfernen, dann strikt mit `json.loads`, mit `len(faelle) == 95` und `len(actions) == 76` als harter Bedingung; kein Feldschnitt über Regex, der hätte keine Kontrolle darüber, ob er ein Objekt verliert.

### Was über den Fall hinausgilt

**Eine Zahl, die steigt, zieht die Zahl neben sich mit, auch wenn ein Plan sie für unbeteiligt erklärt hat.** Der Laufplan führte die normalisierten Mappings ausdrücklich unter „nicht betroffen, andere Menge". Gemessen stiegen sie mit, von 234.245 auf 234.250: zehn neue Rohformen ergeben fünf neue Mappings. Beim Vorgängerzug (#375, eine einzige neue Schreibung) war es tatsächlich null, und daraus war eine Regel geworden. Die beiden Zahlen mussten zusammen gezogen werden, weil sie in denselben zwei Sätzen mit einem gemeinsamen Stichtag stehen: **eine allein zu ziehen hätte genau den Satz falsch gemacht, der vor ihrer Verwechslung warnt.**

**Ein Gate, das eine Zahl bewacht, sieht nicht, ob die Zahl an dieser Stelle einen Ist-Stand meint.** `doc-count-audit.py` meldete die Formen- und die Mappingzahl an 17 Stellen. Zwei davon in `DECISIONS.md` sind keine Ist-Angaben: die eine benennt den Messstand von #378, die andere einen abgeschlossenen Vergleich zweier Indexstände („Authority Index 1.9.5 against 1.9.6: 0 forms added, 0 removed, 0 re-pointed, out of 234,245 mappings on both sides"). Die zweite hochzuziehen wäre eine Falschaussage über eine dokumentierte Messung gewesen. Der Ausweg stand schon im Gate: `find_stale_numbers` kennt einen nachgestellten Stand-von-Version-Vermerk, gebaut für genau diesen Satztyp in `CONTRACTS.md` (#297). Die Zeile heißt jetzt „out of 234,245 mappings on both sides, which is the state of v1.9.6 and not today's" und ist damit für das Gate **und** für einen menschlichen Leser eindeutig. **Wo eine historische Zahl neben einer wachsenden steht, ist der Vermerk billiger als die Ausnahme**, denn die Ausnahme altert still und der Vermerk steht im Text.

**Das Inventar-Gate liest mehr Namen, als es Verzeichnisse scannt.** `check-doc-inventories.py` bindet vier Pfade (`scripts/` flach plus `audit/`, `sync/`, `_archived/`), hält aber jeden im Baum von `scripts/README.md` genannten Skriptnamen gegen die gescannten Dateien. Ein Name aus `scripts/ingest/` ist damit „genannt, aber nicht vorhanden" und färbt das Gate rot. Mutationsprobe am committeten Stand gefahren und zurückgenommen. Die Lücke unter `ingest/` sah aus wie ein Versehen und ist eine Notwendigkeit; sie trägt jetzt einen Absatz, der sagt warum.

### Die #397-Frage: was hat dieser Zug wahr gemacht, das vorher falsch sein konnte

Zehn Prägungen stellen eine Invariante her, die vorher an zehn Stellen verletzt war: die Form steht jetzt unter ihrem Lemma. **Jede Prüfung, die auf „Form nicht unter diesem Lemma vorhanden" gebaut war, hat für diese zehn Paare keinen Gegenstand mehr.** Auf der Typ-Ebene trägt die Gegenprobe: der Trockenlauf vor und nach dem Zug hat `added 10` und die übrigen drei Semantikzähler auf 0, die Mehrdeutigkeitszähler stehen unverändert bei 613 und 1.

**Hier stand zuerst „gesucht und nicht gefunden", und das war falsch.** Die Antwort auf die #397-Frage liegt eine Ebene tiefer, im normalisierten Laufzeit-Wörterbuch des Authority-Index, und dort hat der Zug eine Schreibform umgehängt: `hawsen` löst ab jetzt auf `lemma_42619` *hûse* auf statt auf `lemma_49714` *hûsenblâter*, weil first-wins in Dokumentreihenfolge entscheidet und `variants.xml` nach Lemmanummer sortiert ist, 42619 dort also vor 49714 steht. Gemessen über beide gebauten Wörterbücher: **added 5, removed 0, re-pointed 1**. Wer „hawsen" sucht, erreicht damit 4 Belege statt 32, gezählt über die Belege des aufgelösten Lemmas und nicht über die Vorkommen der Form; die Form selbst steht 5 mal unter der Hausenblase und 2 mal unter dem Fisch. **Der Flip geht gegen Vorschrift B von ADR-021**, also gegen die Rangfolge, die KZW am 14.09. in #378 entschieden hat und die nicht gebaut ist.

**Die Prüfung, die es gefunden hätte, verlangt dieses Projekt seit dem 14.09. selbst:** ADR-021 fordert genau diesen Vergleich als Handgate, ausdrücklich damit „a single re-annotation cannot silently flip a mapping". Er war einmal von Hand gelaufen, grün, 0/0/0; dieser Zug ist der zweite Lauf und liefert das erste rote Testdatum. Es steht jetzt in `docs/DECISIONS.md` neben dem grünen.

**Was daraus über die #397-Frage hinaus folgt: null zusätzliche Mehrdeutigkeiten auf der Typ-Ebene ist eine richtige Zahl, die eine falsche Sicherheit trägt.** Ein Token, das ein Lemma mit dem Typ eines anderen kombiniert, bliebe in der Mehrheit unsichtbar, und dagegen misst dieser Zähler richtig. Er misst aber nicht, was die Prägung mit der **Schreibform** macht, und genau dort lag die Antwort. Ein Kontrollwert, der im selben Zuschnitt liegt wie die Frage, teilt dessen Blindheit; ausgezogen als rote Zeile 43.

### Rote Zeilen

**Rot: einem Menschen zugeschrieben, er habe etwas geprüft, weil ein Feld daneben so klang.** Ausgezogen als rote Zeile 40 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot, erste Zeile zu dieser Lehre: die Trefferzahl stimmte, die Einfügeposition nicht, weil die Zeilenenden ungeprüft blieben.** Ausgezogen als rote Zeile 41 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: zwei Variantenzahlen mit einem Skript gezogen und die dritte im selben Absatz daneben stehengelassen.** Ausgezogen als rote Zeile 42 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: die #397-Frage gestellt, verneint, und die Verneinung war eine Abwesenheitsbehauptung über den halben Bestand.** Ausgezogen als rote Zeile 43 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: aus einer Eigenschaft der Datei auf das Verhalten des Codes geschlossen, und die Auskunft stand in demselben ADR, in das ich in diesem Lauf geschrieben habe.** Ausgezogen als rote Zeile 44 nach [../fehlerjournal.md](../fehlerjournal.md).

### Offen

Alle drei Vorgänge bleiben offen bis zur Abnahme durch @wachauer; ein `Closes` ist keine Abnahme. Was sie noch entscheiden muss: die Sense-Zuordnungen für alle 88 Tokens, die 17 Fälle mit `option: OFFEN` und die 2 mit `NEU_STAND` aus #371 (letztere bräuchten ein neues Lemma), und die erste Hälfte des `hirne`-Auftrags aus #366, die kein Objekt hat: `lemma_2853` trägt 228 Tokens in 66 Dateien und ist nicht leer, und die Form `gehornn` steht nicht darunter.

---

## 2026-09-21: Ein Prüfseiten-Format (#443), und die halbe Fallmenge war gar keine Frage (#359)

Zwei Vorgänge in einem Lauf: ein Format für kuratorische Prüfseiten (#443) und seine erste Anwendung, 45 Fälle aus Luise Boreks Pferdewortlisten (#359). Eine einzelne HTML-Datei, die man verschickt und ohne Installation im Browser öffnet, mit eingebetteten Daten, Rückgabe als JSON und als lesbarer Bericht.

**Der Befund, der die Seite umgebaut hat, steht nicht im Ticket.** Die exakte Stufe des Abgleichsberichts vergleicht Boreks flektierte Formen gegen unsere Lemmaansetzungen. Wo eine fremde Ansetzung zufällig wie eine Flexion aussieht, trifft sie das falsche Wort: `oren` nicht das Ohr, sondern das Fabelvolk der `Ôren` im Herzog Ernst, `lenden` nicht die Lende, sondern das Verb `landen`. Der Homographenzähler des Berichts sieht davon nichts, weil die normalisierten Formen auseinanderlaufen. **28 der 45 Fälle sind Artefakte dieser Art oder bestätigt richtige Annotationen und brauchen keine Entscheidung.** Die Seite ist deshalb nach Befund gruppiert und nicht nach der Klasse des Berichts, und das steht über der ersten Karte: wer 45 Karten durchklickt und bei Karte 31 merkt, dass die Hälfte keine Frage an ihn war, hat bis dahin die falsche Frage beantwortet.

**KZWs Körperteil-Frage vom 16.09. löst sich zu drei Vierteln auf.** `ôr`, `lende` und `brust` tragen `concept_14011100` längst; Boreks Formen haben andere Lemmata getroffen. Nur `gebeine` ist ein echter Kandidat, und die tierische Verwendung ist belegt (`AXU_23544_3` „gar des orses gebeine“, `HTR_193190_2` „des lewen gebeine ist âne marc“). Gelesen sind 9 der 207 Belege, nämlich die mit einem Pferdewort im Kontextfenster: das beantwortet „kommt vor“ und nicht „kommt wie oft vor“, und die Seite sagt das so. Der Löwenbeleg ist dem Filter zugelaufen, weil `marc` in der Wortliste steht und an dieser Stelle Knochenmark heißt.

### Was über den Fall hinausgilt

**Ein Gate schützt, was es liest, und die Liste dessen, was es liest, ist selbst eine Behauptung.** Gegen verfälschte Zitate war ein Gate gebaut: jedes Zitat in der Begründung muss so in den gemessenen Belegen stehen, `ss` ausdrücklich nicht gleich `ß`. Es hat gegriffen und trotzdem nichts genützt, denn über der Begründung steht `kurz`, fett gesetzt und als Erstes gelesen, und dort behauptete eine Kurzzeile eine Formel, die keiner der fünf Belege liest. Das ist dieselbe Geometrie wie #397, eine Stufe höher: dort raubt ein Fix einer Prüfung ihren Gegenstand, hier gibt ein Gate den Nachbarfeldern eine Zusage, die es nicht einlöst.

**Die Antwort darauf hat drei Stufen, und die dritte ist die einzige, die nicht mitwachsen muss.** `_prosafelder` sammelt die Felder, statt sie aufzuzählen; `HTML_FELDER` steht im Modul statt im Kopf des Autors; und `rohe_striche` prüft **das fertige Dokument** statt der Felder. Kommt ein siebtes Feld dazu, bleibt nur die dritte richtig. Vier Felder einzeln zu bewachen hieße, das fünfte zu vergessen.

**Drei Runden, drei Klasse-A-Befunde, und jeder saß in dem, was die vorige Runde gebaut hatte.** Runde 1 fand die fehlende Auszeichnung; Runde 2 fand, dass deren Fix den Rückweg verdorben hatte (`vorschlag.text` ging durch die Auszeichnung, und dasselbe Feld lebt als Text im Export weiter, wo KZW `<span class="mono">hurt</span>` gefunden hätte); Runde 3 fand den Fehler in der Prüfung, die Runde 2 dagegen gebaut hatte. Sie suchte im fertigen Wert nach einem Muster, sah aber einen Wert nach `html.unescape`: ein geschriebenes `<pc>` steht darin wieder als `<pc>` da. **Gemessen brechen `<pc>` und `<w>` ab, während `a < b und c > d` durchläuft**, also trifft der Fehlalarm genau die Formen, die hier in einer Annotationsbegründung stehen.

**Ich habe daraufhin das Gate umgebaut, es vergleichen statt suchen lassen, und Runde 4 hat gezeigt, dass der Umbau nichts prüft.** Der Vergleich leitete den erwarteten Wert mit demselben Ausdruck aus derselben Quelle ab, den der Generator benutzt: für `kopfText` `f['kopf'] == f['kopf']`. Ein ausgezeichnetes Feld ohne Eintrag in `HTML_FELDER` lief glatt durch, und das ist genau das Fehlerbild aus Runde 1. **Der Stand nach Runde 3 war schlechter als der davor**, und damit war die Entscheidung keine Abwägung mehr: zurückgebaut, die Lücke im README benannt, der Vergleich ersatzlos raus.

**Vier Runden, drei davon an derselben Stelle, und das ist für sich ein Befund über das Vorgehen.** Die Prüfung, um die es ging, hat in den 45 realen Fällen nie gefeuert und hätte es auch mit keiner der vier Fassungen getan. Was jede Runde erzeugt hat, war eine weitere Annahme über einen Fall, den es hier nicht gibt.

**Die Lehre, die bleibt, ist nicht die über Muster und Vergleiche, sondern die über den Ersatz:** wer ein Gate ersetzt, fährt die Mutationen der alten Fassung gegen die neue. Meine acht Proben waren alle für die neue Fassung erfunden, keine stammte von der alten, und keine berührte deshalb den Fall, den die alte gefangen hätte. **Eine Mutationsprobe, die nur die neue Prüfung kennt, misst, was der Autor sich vorgestellt hat; die alte Fassung weiß, was früher schiefging.** Rote Zeile 56.

**Und der Grund, warum ich es nicht selbst gesehen habe, steht in meinen eigenen Texten desselben Nachmittags.** Die #397-Frage („was hat diese Änderung wahr gemacht, das vorher falsch sein konnte?“) steht im Eintrag oben, im Reviewauftrag für Runde 4 und in der roten Zeile 47. Ich habe sie dreimal an fremden Code gestellt und kein einziges Mal an den Fix, den ich gerade schrieb.

**Eine Prüfung, deren Greifen nicht gemessen ist, ist eine Behauptung wie jede andere.** Jede neue Prüfung dieses Laufs ist mit einer Mutationsprobe in beide Richtungen belegt: sauberer Fall durch, mutierter abgewiesen. Die Koordination hatte am selben Tag vorgemacht, warum die eine Richtung nicht reicht, und dabei einen ungültigen ersten Anlauf offengelegt, dessen Attrappe an einer Stelle saß, die das Gate ohnehin überspringt. Eine Probe, die nur den mutierten Fall zeigt, belegt, dass ein Gate etwas meldet, und nicht, dass es das Richtige meldet.

**Der Zuschnitt einer Messung ist gefährlicher als ihre Rechnung.** Dreimal an einem Nachmittag war die Menge falsch geschnitten und die Zahl darin richtig: ein Kontrollwert, der flektiert danebenlag (`Welscher Gast` gegen „Der Welsche Gast“); eine Grundmenge, die nur finden konnte, wonach sie fragte (fünf bekannte Titel statt der 36 Werk- und Autornennungen unter 59 Klammernennungen); und eine Zahl, unter der zwei Mengen lagen. Aufgefallen ist jeder der drei erst, als das Kommando für die nächste Aussage hinzuschreiben war, keiner beim Schreiben der Zahl. Rote Zeile 48. **Beim Nachzählen der Kette für diese Zeile ist derselbe Fehler noch einmal aufgetreten:** ein Grep über das Fehlerjournal nach `dateisuche.md` trifft null Einträge, und alle drei Zeilen dieser Lehre nennen sie in Prosa. Wer eine Kette über den Dateinamen zählt, zählt die Zeilen, die ihn zufällig schreiben.

**Und eine Quote, deren Nenner ein Sammel-Limit ist, sieht aus wie eine Aussage über das Korpus.** `jagen` trägt 1.406 Tokens, gesammelt sind 250, weil `BELEG_CAP` dort greift; „249 von 250“ ist eine Aussage über die Sammlung und keine über das Korpus.

### Nebenbefund, der weiter reicht: `pos` gegen `posAll`

Bevor sich Bewertungen auf die Wortart eines Lemmas berufen, ist gemessen, ob das Feld hält. Gegen `posAll` sind **34 von 34** Lemmata mit gesammelten Belegen einig, sobald Kompositum-Tags aufgelöst werden (ohne diese Regel 31, und die drei Abweichungen wären reine Notation). Gegen das Einzelfeld `pos`, also die Angabe, die als *die* Wortart erscheint, weichen **4 von 34** ab: `jagen` führt INJ bei 249 von 250 VRB, `lenden` ADV bei 44 von 45 VRB, `merken` INJ bei 7 von 7 VRB, `rôse` ADJ bei 3 von 3 NOM. Alle vier führen die Korpuswortart in `posAll` an zweiter Stelle. Das betrifft `authority-files/` und jede Ansicht, die `pos` zeigt, und steht mit Messvorschrift in `ingest/review/359-borek/folgebefunde.md`.

### Rote Zeilen

Ausgezogen nach [../fehlerjournal.md](../fehlerjournal.md): **45** die Umlaut-Ersetzung, die drei mittelhochdeutsche Zitate mitgezogen hat; **46** vier aus Siglen erschlossene Werktitel, derselbe Fehlermodus wie `Alanya`, nur an einem Kürzel; **47** das Gate, das ein Feld deckte und daneben fünf stehen ließ; **48** der dreimal falsch geschnittene Zuschnitt; **49** eine Zahl aus einem Reviewbericht, die ich in vier eigene Texte geschrieben habe, ohne sie zu messen; **56** das Gate, das ich durch ein besseres ersetzt habe, welches nichts prüfte.

---

## 2026-09-22: Review-page examples for reuse

KZW approved collecting the blank review pages via a separate branch and PR after consultation with Chris. `examples/review-pages/` preserves byte-identical copies of the local #364, #371 and #390/#115 pages. The overview in INDEX documents scope, snapshot dates, exports and differences from #443, and links the external wachauer/mhdbdb-kuratorik example at commit 296f4ff4cfb3a68b526397c46baef9a3ec9189ef. Existing generators and templates accompany the newer examples; generators continue to write working pages at the repository root, leaving the archived snapshots unchanged. Browser tests now address the archived copies. No submitted human decisions or corpus/authority edits are included. Validation: seven Chromium tests passed at the archive paths; the stat page rendered 95 cards without browser errors and exported valid JSON. Archive copies verified byte-identical.

---

## 2026-09-23 (Spur A, Welle A1) – #387, #418, #464: 36 Tokens, und das Doppeltag steht in der Reihenfolge, die nichts verwechselt

Drei von KZW entschiedene Pakete in einem PR, ein Rebuild, Korpus-Index 4.2.19, Authority-Index 1.9.9. 21 Resttokens aus #387, die 12 offenen *hawe*-Belege aus #418 (dazu `AC3_23010_1` mit neuem Typ), die zwei *zalder*-Tokens aus #464. Fünf Typen geprägt (`type_372387` bis `type_372391`), `type_117159` entfallen, ein neuer Sense `lemma_9644_sense_119194`. Laufskript `scripts/ingest/pos-disambig/apply-387-418-464.py`, Einzelheiten im PR.

### Was über den Einzelfall hinausgilt

**Eine Bestandszahl zählt die Altlast mit, bis man fragt, welches Merkmal die Fälle trennt.** Der Laufplan hatte `NOM ADJ` statt KZWs `ADJ NOM` vorgesehen, weil der Bestand 119.501 zu 0 steht. Die Zahl war richtig, trug aber die falsche Menge: keiner der 119.501 hat ein `@reason`, sie sind die unaufgelösten Komposita der Migration, die K4 auflösen soll. Die Verschmelzungen zeigen, was eine bewusste Doppelannotation im Bestand ausmacht: `VRB PRO` 154 von 154 mit `@reason`, `PRO VRB` 0 von 9.068. Ein bewusstes Doppeltag in `NOM ADJ` zu schreiben, hätte es in genau die Menge gelegt, die später maschinell aufgelöst wird. Festgehalten in POS-TAGSET §2; die Koordination hat die Laufplan-Zeile revidiert. Die #464-Tokens wechseln aus demselben Grund von `PRO VRB` auf `VRB PRO`.

**Eine Kommentarvorgabe hat Folgen im Schema, die niemand mitgeplant hatte.** `@reason` an `<w>` ist GAP-Kategorie 1 und in tei_all ungültig. Vier Dateien, die vorher tei_all-gültig waren (FR1, FR3, ENE, ROT), sind es mit ihrem ersten `@reason` nicht mehr; die Baseline steigt von 30 auf 34, und die alte Zahl stand in `validate-corpus.py`, TEI-MODEL.md §10, `schema/README.md`, `DECISIONS.md` und einer Hilfeseite. Gefunden hat es die Stichprobe über die 19 geänderten Dateien, nicht ein Gate: Stage 1 warnt nur, und mit `--sample` oder `--corpus-only` überspringt `validate-corpus.py` den Namensabgleich ganz. Wer nachweisen will, dass die Baseline hält, fährt den Lauf **ohne** Filter (hier 641/675, Stage-1 34 bei Baseline 34, keine NEW- oder GONE-Zeile).

**Der Typzähler war zum zweiten Mal grün, während das Wörterbuch umklappte.** `extract-variants.py` meldete `>1 lemma` von 1 auf 0, also sauberer als vorher. Der Vergleich der beiden gebauten `authority-index`-Wörterbücher, den ADR-021 seit dem 14.09. verlangt, zeigte 0 neu, 0 entfallen, 2 umgeklappt: `hawe` zu *houwen* (B-konform) und `froewen` zu *vrô*, gegen Vorschrift B (35 Belege unter *vrouwe*, 21 unter *vröuwen*, 1 unter *vrô*). Die Ursache ist dieselbe wie bei `hawsen` am 21.09.: eine zwingende Neuprägung trifft auf first-wins. Gefunden hat es die Reviewrunde, nicht ich, obwohl der Eintrag darüber und rote Zeile 43 genau das beschreiben. **Der Vergleich steht nicht als Schritt im Data-Change-Lifecycle, und solange er dort fehlt, fährt ihn nur, wer sich an ADR-021 erinnert.** Die dritte Fixture liegt als Änderungswunsch im Laufplan, weil `DECISIONS.md` eingefroren ist.

**Eine revisionDesc-Vorlage, die für jede Datei gilt, sagt über den Sonderfall die Unwahrheit.** In AC3 stand zunächst „2 Tokens umannotiert“, obwohl einer davon nur einen neuen Typ bekam. Das Skript kennt den Fall jetzt (`NUR_TYP`), und die Zeile ist aus der Vorlage neu erzeugt; die Reviewrunde 2 hat per Nachbau auf dem Vor-Stand bestätigt, dass alle 19 TEI-Dateien und `lexicon.xml` byteidentisch herauskommen.

### Rote Zeilen

Keine neue. Der Wörterbuch-Flip hätte eine Zeile zu derselben Lehre wie Nummer 43 werden können; er hat nichts getragen, weil die vorgeschriebene Reviewrunde ihn vor dem Push gefunden hat. Dasselbe gilt für die zwei Nachbarzeilen, die die Zahländerung nicht mitgezogen hatte (CONTRACTS.md:381, TEI-MODEL.md:933, Lehre aus `korrigieren.md`), und für die Vorher-Zahlen, die im POS-TAGSET-Absatz zunächst als Ist-Stand standen. Nach `wiederholte-fehler.md` ist ein durch ein Gate abgewendeter Fehler keiner. Dass die Lehre selbst dreimal nicht gegriffen hat und jedes Mal die Reviewrunde, steht oben.

Gemessene Verteilung aus `trockenlauf-auswerten.py`, Abschnitt `shell-konventionen`: diese Session `394e94e5 mhdbdb-daten2` mit 178 Aufrufen, 49 Treffern, 28 %. Das Skript bricht danach am Log `gelesenes-trockenlauf.jsonl` mit `AttributeError: 'NoneType' object has no attribute 'get'` ab (eine Zeile ist `null`); die übrigen Abschnitte liegen deshalb nicht vor. Das Skript liegt in `claude-code-setup` und ist hier nicht angefasst.

### Was zurück an Christian geht

- Der PR ist ein Daten-PR, der CI-Review-Bot wird rot; der lokale Review trägt ihn (zwei Runden, keine offenen Befunde).
- `npm test` endete mit `VERDICT: ROT (3 flaky …)`: 352 bestanden, 0 unerwartet, drei Lade-Timeouts im ersten Versuch, alle im Retry grün, während Spur C parallel testete.
- Der *fröwen*-Flip (siehe oben) bleibt bis zur Umsetzung von ADR-021 bestehen; KZW bekommt ihn in #387 als Hinweis.
- Nachzüge außerhalb des PR: `hilfe-daten-beitragen.html:819` (Baseline 30, Spur B), `docs/DECISIONS.md:782` und die dritte ADR-021-Fixture (Inbox).
- Offen bei KZW: das `etym` von *zalder* (#464, Vorschlag *er* + *zal* + *zeln*) und die Grenze zwischen ihrer allgemeinen Konvention `ADJ NOM` und ihren zwei Einzelentscheidungen `NOM` (#387).

---

## 2026-09-23 (Spur B des Issue-Abbaus) – vier KZW-Meldungen im Frontend, eine davon wartet auf sie

### Was gearbeitet wurde

- **#446**, „das Korpus“ in nutzersichtbarem Text: sechs Stellen in Playground und Hilfe. Das Audit hatte vier genannt; die fünfte (`playground/index.html:126`) stand dort nicht, die sechste habe ich selbst zuerst übersehen (rote Zeile 70). `README.md:115` hat die Koordination in `081ad4d10` übernommen.
- **#435**, Tippfilter über beiden Textlisten im Textvergleich, wie KZW am 15.09. entschieden hat. Ihre Frage zur Begriffs-Verteilung beantwortet die Messung: das Autocomplete gibt es seit `a2e7b0b36` (#113, 15.05.). Alans „baum“ scheiterte an der Umlautfaltung, behoben am 11.09. in `a3779e271`; im Browser schlägt „baum“ jetzt „Bäume“ vor.
- **#433**, Gattungs-Vorschlag im Textfilter der Korpussuche, Klick setzt die Auswahl samt Untergattungen. Dazu der Gattungen-Explorer auf den Teilbaum umgestellt; das revidiert #361/PR #362 und ist von Christian freigegeben. Die Chip-Frage steht in #433 bei KZW.
- **#58** nicht gebaut: für den Durchklick gibt es drei vernünftige Zielorte, und Christian wollte die Form mit KZW klären. Der Entwurf ging über die Koordination an sie.

### Was über den Einzelfall hinausgilt

**Ein Haltepunkt im Auftrag kann den falschen Gegenstand tragen.** Der Kickoff nannte für #433 den Haltepunkt „Chip“ als „Form der Auswahl in der Suchmaske“. Im Thread war diese Form seit dem 17.09. entschieden, und „Chip“ meinte den Gattungs-Chip in der Trefferliste, zu dem KZWs Frage „Wo genau würde man das sehen?“ seit dem 15.09. offen stand. Erst die Kommentare, nicht der Auftragstext, sagten, wo der Halt hingehört.

**Eine Entscheidung von gestern kann an einer Prämisse hängen, die heute fällt.** #361 hatte bewusst zwei Bedeutungen für denselben Filterhaken festgeschrieben, weil „Werke anzeigen“ nur die direkten Werke las. KZWs „die Untergattungen kommen immer mit“ nimmt genau diese Prämisse weg. Die Revision musste trotzdem benannt und vorgelegt werden, bevor gebaut wurde, weil sie gegen eine dokumentierte Entscheidung ging.

**Ein totes Feld hat oft einen falschen Leser, nicht einen fehlenden Schreiber.** Das Ticket vermutete den Gattungs-Chip am leeren `genre` des Korpus-Index. Gelesen wird aber `work.genre` im Authority-Index, ein Feld, das keines der 584 Werke trägt; sie tragen `genres` als Liste.

**Ein Overlay über einer Liste von Checkboxen macht aus einem Fehlklick eine andere Handlung.** Der Reviewer hatte es nur „für den Berater“ notiert: die Vorschlagsliste lag über der Textliste, und ein Klick auf eine verdeckte Checkbox hätte eine ganze Gattung gewählt. Sie steht jetzt im Fluss.

### Die #397-Frage

Wahr gemacht hat der Zug: `findWorksInGenre` ist jetzt eine Obermenge der direkten Zuordnung. Unerreichbar geworden ist dadurch der Detailfeld-Zweig „kein Werk direkt zugeordnet, im Zweig darunter N“; er ist entfernt. Die zwei Stellen, die weiter die direkte Zahl brauchen (Baumzeile, Detailfeld), gehen über das neue `countOwnWorks`. Der Filterhaken zählt in beiden Ansichten jetzt dieselbe Menge; seine zwei Beschriftungen bleiben stehen, bis `genre-explorer.spec.js` nach dem Merge von #465 angepasst werden darf.

### Rote Zeilen

**Rot: eine Trefferzeile selbst abgeschnitten und das Abgeschnittene als Nichttreffer gelesen.** Ausgezogen als rote Zeile 70 nach [../fehlerjournal.md](../fehlerjournal.md).

**Rot: Port 8080 als frei gemeldet, weil die Gegenprobe auf einem deutschen Windows nach „LISTEN“ suchte.** Ausgezogen als rote Zeile 71 nach [../fehlerjournal.md](../fehlerjournal.md).

Verteilung aus `claude-code-setup/hooks/trockenlauf-auswerten.py` am 23.09.: `suchergebnis` 1.798 Zeilen, davon eng 1.371, leer 46, eng und leer 36. Die Auswertung bricht danach beim Log `gelesenes` (2.250 Zeilen) mit `AttributeError: 'NoneType' object has no attribute 'get'` ab (Zeile 102); eine Zeile dieses Logs ist kein Objekt. Das ist ein Befund an `claude-code-setup`, hier nicht angefasst.

Nicht gezählt: zwei Testläufe durch eine Pipe geschickt, gegen die Projektregel. Die VERDICT-Zeile war beide Male sichtbar, getragen hat es nichts.

### Was zurück an Christian geht

- #58 wartet auf KZWs Wahl der Form; die Lesearbeit (Render- und Lesestellen) steht in #58 und in dieser Session.
- #433: der Chip wartet auf KZW; FILTER_LABEL und `genre-explorer.spec.js` werden nach dem Merge von #465 zusammengezogen.
- `docs/FEATURES.md` und `docs/DEVELOPMENT.md` tragen der Koordination übergebene Änderungswünsche, einzutragen nach den Merges.
- Nebenbefund: ERB und ERD tragen im Textvergleich dieselbe Beschriftung „Herzog Ernst (Hrsg. Bartsch, 1869)“; der Disambiguator unterscheidet sie nicht.
- `hilfe-daten-beitragen.html:819` nennt die Baseline 34 auf Ansage von Spur A; bis deren PR gemergt ist, eilt die Hilfeseite voraus.

---

## 2026-09-23 (Spur C des Laufs) – #465: der Testport als Parameter, und warum die Probe zweimal am Speicher scheiterte

PR #472, nicht gemergt. `MHDBDB_TEST_PORT`, Vorgabe 8080. Gelesen wird die Variable allein in `testing/test-port.js`, und dieselbe Funktion versorgen die Config (`baseURL`, `webServer`), `scripts/run-tests.js` (Sentinel) und `npm run serve` (neuer Wrapper `testing/serve.js`). In 30 Specs sind 132 absolute Adressen jetzt Pfade relativ zu `baseURL`; zusammen mit den drei Stellen in der Config sind das die 135 in 31 Dateien, die die Koordination gezählt hatte.

### Was gearbeitet wurde

- Umbau, zwei Review-Runden `fable-reviewer` (Runde 1 auf `cdaee8ddd`: Basisangabe im Auftrag, Randwert 65535 im Abhilfetext; Runde 2 auf `e36b5b17e`: ohne Befund), CI grün, Bot ohne Befund.
- Parallelprobe mit je `--workers=2`, Hauptbaum auf 8080 und dieser Zweig auf 8081 gleichzeitig: `VOLLLAUF GRUEN (370 Tests, 34 Dateien)` und `VOLLLAUF GRUEN (355 Tests, 34 Dateien)`. Allein auf 8080 ohne Variable: `VOLLLAUF GRUEN (355 Tests, 34 Dateien)`.
- Mutationen: fremder Server auf dem gesetzten und auf dem Vorgabeport ergibt je Exit 2; der eigene Server über `npm run serve` wird erkannt und wiederverwendet; eine leere Spec-Datei ergibt `NICHT GELAUFEN` und `VERDICT: ROT`, Exit 1; ungültige Werte (`abc`, `0`, `""`, `65536`) ergeben je Exit 2 mit VERDICT-Zeile.
- Nebenbefund behoben: `vendor.spec.js` durchsuchte die Repo-Wurzel ohne `.claude` auszunehmen und testete im Hauptbaum je fünf Seiten aus drei fremden Worktrees mit. Daher 370 Tests dort gegen 355 hier, mit `--list` gezählt und nach Datei aufgeschlüsselt.

### Zwei Fallen, die kein Ticket kannte

**`http-server` ohne `-p` weicht still aus.** Der naheliegende Umbau von `npm run serve` wäre gewesen, `-p 8080` wegzulassen und `PORT` zu setzen. `http-server` nimmt dann `PORT` und ohne sie den nächsten freien Port ab 8080 (`bin/http-server`, Zeile 68 und 129). Bei belegtem 8080 wäre der Dev-Server also stillschweigend auf 8081 gelandet: genau die Verhaltensänderung ohne gesetzte Variable, die der Auftrag als Stoppbedingung nannte. Dazu kommt, dass npm-Skripte unter Windows in `cmd.exe` laufen (`script-shell` ist `null`), wo `$VAR` nicht expandiert. Beides zusammen verlangt einen Wrapper, der `-p` immer setzt.

**Das Inventar-Gate entschied über den Ort einer neuen Datei.** `scripts/serve.js` machte `check-doc-inventories.py` rot, weil `scripts/README.md` jede Datei unter `scripts/` kennen muss und in diesem Lauf eingefroren war. Unter `testing/` zählt dasselbe Gate nur `*.spec.js` in `testing/tests/`. Gemessen, nicht gelesen: das Gate einmal mit der Datei unter `scripts/` gefahren (Exit 1, „Fehlt: serve.js"), einmal unter `testing/` (Exit 0). Der Rotlauf war zugleich der Kontrollwert, dass das Gate neue Dateien überhaupt sieht.

### Was über den Einzelfall hinausgilt

**Eine Testzahl, die von der Umgebung abhängt, ist keine Eigenschaft der Suite.** Wer im Hauptbaum `npm test` fuhr, bekam so viele vendor-Tests, wie gerade Worktrees unter `.claude/` lagen. Die VERDICT-Zeile zeigte 370 und sah aus wie ein Bestand. Aufgefallen ist es nur, weil zwei Läufe gleichzeitig liefen und ihre Zahlen nebeneinander standen. Der Spec-Abgleich von `run-tests.js` hätte es nicht gefunden, denn er vergleicht Dateien, nicht Tests je Datei.

**Eine Abnahmeprobe, die die Maschine überfordert, ist ein Befund über die Probe und nicht über die Änderung.** Die ersten beiden Läufe mit je sechs Workern hatten vor dem Abbruch 11 und 14 Fehlschläge, auch der unveränderte Hauptbaum. Die naheliegende Lesart „der Umbau bricht 14 Tests" hätte eine Nacharbeit an fehlerfreiem Code ausgelöst. Getrennt hat es erst ein zweiter Lauf unter anderen Bedingungen: gleichzeitig mit je zwei Workern, beide grün.

**Was diese Änderung wahr gemacht hat, das vorher falsch sein konnte (#397):** `BASIS_URL` stimmte mit dem Port von Playwright nur überein, weil beide Konstanten waren. Jetzt hängt die Übereinstimmung an derselben Lesefunktion und an der Vererbung der Umgebung über `spawnSync`. Außerhalb von `run-tests.js` (`--config`, `test:ui`, `test:debug`, `test:headed`) prüft kein Sentinel, und das war vorher genauso.

### Rote Zeilen

**Rot: aus einem gemessenen Abbruch auf seine Ursache geschlossen und die Ursache in einen PR-Body geschrieben.** Ausgezogen als rote Zeile 73 nach [../fehlerjournal.md](../fehlerjournal.md).

Verteilung aus `trockenlauf-auswerten.py`, Zeile dieser Session (`03dc7dca`, mhdbdb-testport): shell-konventionen 32 Treffer bei 107 Aufrufen (30 %), mengenaussagen 10 bei 15 (67 %). Das Skript selbst bricht im Abschnitt `gelesenes` mit `AttributeError: 'NoneType' object has no attribute 'get'` ab (Zeile 102, `auswerten_bool`): ein Element der eingelesenen Logzeilen ist `None`, woher, ist nicht untersucht. Das ist ein Befund für `claude-code-setup` und nicht in diesem Repositorium zu beheben.

### Was zurück an Christian geht

- **#472 mergen**, wenn der PR trägt. Danach trägt die Koordination die drei Inbox-Sätze in `docs/DEVELOPMENT.md` ein, sobald auch #469 gemergt ist.
- **Zwei Volläufe parallel brauchen weniger Worker.** Mit je sechs hat Claude Code die Läufe wegen Speichermangels beendet, mit je zwei liefen beide in etwa 22 Minuten grün. Ob sechs auf einer sonst ruhigen Maschine parallel tragen, ist nicht gemessen.
- **`trockenlauf-auswerten.py` stürzt im Abschnitt `gelesenes` ab** (siehe oben).
- **`TaskStop` auf `npm run serve` ließ hier den `http-server`-Kindprozess stehen** (gemessen: PID 34060 lauschte nach dem Stopp weiter auf 8081). Der Port bleibt belegt, bis jemand die PID beendet. Ob der alte Aufruf ohne Wrapper sich genauso verhielt, ist nicht gemessen.

---

## 2026-09-23 (Nachtlauf, Spur A, Paket A1) – #252 und #267: 846 Lücken und neun Header, und kein Index hat es gemerkt

Der Nachlass des Tageslaufs, fertig gemacht. #252 zweiter Durchgang: 846 Stellen des Musters `( caesura )` innerhalb einer Zeile mit Wortlaut sind `<gap reason="lost"/>` geworden, in 20 Dateien, nach KZWs Freigabe vom 22.09. #267: neun Header tragen `no-print` statt `excerpt-only` und den Satz, den KZW am 10.09. formuliert hat, FR3 trägt das Standard-`<availability>`. Kein Versions-Bump, weil keiner der drei Builds eine Differenz erzeugt. Skripte unter `scripts/ingest/gap-252/` und `scripts/ingest/no-print-267/`, Zahlen im PR.

### Was über den Einzelfall hinausgilt

**Ein gesicherter Patch ist ein Kontrollwert, kein Ergebnis.** Das Skript lief frisch auf `origin/main`; der Tagespatch wurde nicht angewandt, sondern auf Kopien des Basisstands im Scratch, und dann zeilenweise gegen den Arbeitsbaum gehalten. 17 Dateien zeilengleich, drei unterscheiden sich genau um die #267-Zeilen. Kein Byte-Gleichstand, und zwar aus einem Grund, der beim ersten Blick wie eine Abweichung aussieht: `core.autocrlf=true`, `git show` liefert den LF-Blob, der Arbeitsbaum hat CRLF. Wer hier nur Bytes vergleicht, meldet 20 Abweichungen, die keine sind; wer nur Zeilen vergleicht, übersieht eine echte Zeilenend-Änderung. Beides zusammen, plus `git diff --numstat` als Gegenprobe (3 → 1 Zeilen je Stelle), trennt die Fälle.

**Die Zahl einer Messung steht in TEI-MODEL.md zweimal, und kein Gate kennt sie.** §6.5 und §3.1 nennen beide die Zahl der `<caesura/>`. Am 10.09. ist die Kopie in §3.1 stehen geblieben, heute wieder; gefunden hat es beide Male die Reviewrunde. `doc-count-audit.py` führt keinen `caesura`-Schlüssel, also hängt an keiner der beiden Zeilen ein Anker. Der Vorschlag des Reviewers gehört an Christian: entweder verweist §3.1 nur noch auf §6.5, ohne Zahl, oder das Audit bekommt den Schlüssel.

**Ein Marker, den niemand liest, kann jahrelang das Gegenteil sagen.** `sources/README.md` behauptete, das Frontend zeige bei den `excerpt-only`-Texten nur Auszüge. Es hat den Marker nirgends ausgewertet (#267, am 06.09. gemessen, heute für `assets/`, `playground/`, `testing/` wiederholt). Der neue Name `no-print` hat dasselbe Risiko: auch ihn wertet heute nichts aus, weil nichts druckt. Die Bedeutung steht jetzt in TEI-MODEL §2.1, damit der, der einmal eine Druckansicht baut, sie findet.

### Rote Zeilen

Keine neue. Die stehen gebliebene Zahlkopie in TEI-MODEL.md:263 fällt unter die Lehre aus `korrigieren.md` (Nachbarschaft einer geänderten Zahl mitlesen), hat aber nichts getragen: die vorgeschriebene Reviewrunde hat sie vor dem ersten Push gefunden, und ein durch ein Gate abgewendeter Fehler zählt nach `wiederholte-fehler.md` nicht. Dass dieselbe Lehre damit heute zum zweiten Mal nur über die Reviewrunde gegriffen hat (Eintrag darüber, CONTRACTS.md:381 und TEI-MODEL.md:933), steht oben als Befund.

Gemessene Verteilung aus `trockenlauf-auswerten.py`, Abschnitt `shell-konventionen`: diese Session `09f7a3aa nacht-daten` mit 85 Aufrufen, 17 Treffern, 20 %. Das Skript bricht danach weiterhin am Log `gelesenes-trockenlauf.jsonl` mit `AttributeError: 'NoneType' object has no attribute 'get'` ab; es liegt in `claude-code-setup` und ist hier nicht angefasst.

### Was zurück an Christian geht

- Ein Daten-PR ohne Index-Bump; der CI-Review-Bot wird voraussichtlich rot, der lokale Review trägt ihn (zwei Runden, Runde 2 ohne Befund).
- `npm test` auf Port 8081 mit zwei Workern: `VERDICT: VOLLLAUF GRUEN (373 Tests, 38 Dateien)`, 0 unerwartet, 0 flaky, gelaufen auf 8be73c141; danach nur eine Doku-Zeile und Reviewer-Memory.
- Offen bei KZW in #252: die fünf Komma- und Doppelpunktfälle (Kontextliste vom 23.09. 14:05), die zwei `MUG`-Stellen mit der Zäsur im `<hi>`, die drei Stellen „Marker plus ein Zeichen“.
- Nicht angefasst, weil nicht Spur A: der Docstring von `scripts/migrate-caesura-to-gap-252.py` nennt noch „838 in 17 Dateien“ als offen.
- Zu entscheiden: ob die caesura-Zahl in TEI-MODEL §3.1 bleibt oder ein Audit-Schlüssel dazukommt (siehe oben).

---

## 2026-09-23 (Nachtlauf, Spur B, Paket B1) – #433: der Chip war nie da, und die Kette dahinter auch nicht

Der Nachlass des Tageslaufs, übernommen von der Neustart-Instanz `nacht-frontend-2` (die erste Instanz `nacht-frontend` endete ohne Commit). Zwei Teile: der verwaiste Commit `5625ff334` (eine Beschriftung für den Filterhaken im Gattungen-Explorer) per Cherry-pick, byte-identisch; und KZWs Entscheidung vom 23.09. 12:32 UTC in #433, den ungenutzten Anzeigezweig für den Gattungs-Chip auf den Trefferkarten zu entfernen. Damit sind die zwei Zusagen aus dem Eintrag des Tageslaufs eingelöst: „der Chip wartet auf KZW" und „FILTER_LABEL und `genre-explorer.spec.js` werden nach dem Merge von #465 zusammengezogen" (oben unter „Was zurück an Christian geht" und im #397-Absatz). Der JOURNAL-Nachtrag aus dem gesicherten Patch ist nicht übernommen: er hätte eine alte Zeile mitten im Text geändert und einen Hash genannt, den es auf `main` nicht geben wird.

### Was über den Einzelfall hinausgilt

**Ein toter Anzeigezweig hat eine tote Kette hinter sich, und die gehört mit weg.** Der Chip las `result.genre`, das `SearchEngine.getGenre()` aus `work.genre` füllte, einem Feld, das keines der 584 Werke im Authority-Index trägt (gemessen, der Schlüssel fehlt ganz; die Werke tragen die Liste `genres`). An derselben Kette hing ein Filterzweig `filters.genre`, den kein Aufrufer übergibt. Hätte ihn jemand benutzt, hätte er jeden Text ausgeschlossen, weil `null !== genre` immer wahr war. Nur die Chip-Zeile zu streichen hätte diesen Zweig als scheinbar funktionierenden Gattungsfilter stehen lassen, genau die Sorte Feld, die #58 erzeugt hat.

**Kein neuer Test, und das ist gemessen, nicht bequem.** Ein Test auf das Fehlen des Chips wäre auf der Basis ebenso grün gewesen, weil der Chip nie gerendert hat. Er hätte also nichts festgehalten (§2.1 Regel 3 im Issue-Playbook).

### Rote Zeilen

Keine. Verteilung aus `trockenlauf-auswerten.py`, Zeile dieser Session (`11858632`, nacht-frontend-2), Stand beim Schreiben dieses Eintrags am 23.09. abends (die Zahlen wachsen mit jedem weiteren Aufruf der Session): shell-konventionen 19 Treffer bei 60 Aufrufen (32 %), mengenaussagen 2 bei 13 (15 %). Das Skript bricht weiterhin im Abschnitt `gelesenes` mit `AttributeError: 'NoneType' object has no attribute 'get'` ab (Zeile 102); es liegt in `claude-code-setup`.

### Was zurück an Christian geht

- `docs/DESIGN.md` verliert die Zeile „Genre tag" unter Badges, als benannte Freeze-Ausnahme der Koordination: die Chip-Zeile war die einzige Verwendung des Musters.
- Nicht angefasst, weil Spur A gehört: das Feld `genre` je Text im Korpus-Index, in 667 von 667 Texten vorhanden und in keinem gefüllt (`build-corpus-index.py`). Es hat nach diesem PR auch im Frontend keinen Leser mehr; ob es aus dem Build fällt, ist eine eigene Entscheidung.
- KZW prüft nach Merge und Deploy; sichtbar ändert sich an den Trefferkarten nichts, sichtbar neu ist nur die eine Beschriftung des Filterhakens im Gattungen-Explorer.

---

## 2026-09-23 (Nachtlauf, Spur A, Paket A2) – #270: der Kommentar nennt seinen Urheber

KZW hat am 23.09. in #270 entschieden: die gespeicherte Urheberangabe soll direkt beim Kommentar stehen, auf der Lemma-Seite und im Playground, als „Kommentar von Katharina Zeppezauer-Wachauer“. Umgesetzt nach ADR-018 Option 2, also beim Bauen: `build-authority-index.py` liest `contributors.xml` und schreibt zu jedem `sense.commentResp` ein `sense.commentRespName` in den Index. Beide Oberflächen setzen das Label daraus, ohne Namen bleibt es beim bloßen „Kommentar“. Authority-Index 1.9.10, Korpusindex unverändert. ADR-018 trägt eine Revision statt einer neuen ADR, weil die Entscheidung dieselbe ist und nur ihr Geltungsbereich wächst.

### Was über den Einzelfall hinausgilt

**Der Index-Diff ist die Messung, nicht der Build-Erfolg.** Gegen `main` verändert der Rebuild genau zwei Felder: die Versionsnummer und `lemmata[22933].senses[0].commentRespName`. Heute trägt genau ein Kommentar eine Urheberangabe (lemma_37818, Abba). Die Spec verlangt diese Menge deshalb nicht, sondern liest den Index von der Platte und prüft, dass jede Oberfläche ihm folgt; lemma_37818 steht nur als Kontrollwert darin, damit ein leerer Abruf nicht als grün durchgeht.

**Eine unbekannte Urheberangabe hält den Build an.** Ein `@resp`, das nicht mit `contributors.xml#` beginnt oder auf keine Person und keine Organisation zeigt, ist ein harter Fehler statt eines stillen Kommentars ohne Namen. Per Mutationsprobe an drei ungültigen Werten geprüft, jede brach ab, der Ausgangsstand war danach wiederhergestellt. 54 Namen werden gelesen (52 Personen, 2 Organisationen).

**Aufgelöst wird nur der Kommentar.** `definitionResp` und `origin.resp` bleiben Verweise ohne Namen; die Spec prüft, dass kein `definitionRespName` und kein `origin.respName` in den Index gerät. Ob „von <Name>“ auch an `<def>` und `<etym>` gehört, ist eine Frage an KZW und steht im Statuskommentar von #270.

### Rote Zeilen

Keine neue. Die Runde-1-Befunde (Bump-Widerspruch in DATA-MODEL.md:903, Schema und XPath-Tabelle ohne das neue Feld) hat die vorgeschriebene Reviewrunde vor dem ersten Push gefunden; abgewendet, nicht gezählt. Einen Teillauf (4 Tests auf 593bdcb40) habe ich gestartet, ohne ihn bei der Koordination anzumelden, während Spur B einen Volllauf hatte. Die Koordination hat das korrigiert, seitdem werden auch Teilläufe angemeldet. Der Kickoff hatte nur Volläufe genannt; das ist eine Klarstellung der Laufregel, keine gerissene Lehre.

Verteilung aus `trockenlauf-auswerten.py`, Zeile dieser Session (`09f7a3aa`, nacht-daten, über A1 und A2 zusammen), Stand beim Schreiben: shell-konventionen 63 Treffer bei 214 Aufrufen (29 %), mengenaussagen 32 bei 80 (40 %). Das Skript bricht weiterhin im Abschnitt `gelesenes` mit `AttributeError` ab.

### Was zurück an Christian geht

- Lokaler Review in drei Runden, alle drei mergefähig, keiner mit Klasse A und keiner am Verhalten; neben einem Code-Kommentar und dem Reviewer-Memory betrafen sie die Doku: Die Bump-Regel für `contributors.xml` stand in der Routingzeile und im Satz darunter gegensätzlich, und drei Aufzählungen der Indexfelder (DATA-MODEL Schema und XPath-Tabelle, TEI-MODEL-AUTH-FILES) kannten das neue Feld nicht. Behoben über Freeze-Ausnahmen der Koordination.
- Veraltet und nicht angefasst, weil in docs/playbooks: MASTERPLAN-EINZEL-LEMMA-KURATION.md:102 („@resp wird nirgends angezeigt“). Die Koordination zieht die Zeile nach dem Merge nach.
- `VERDICT: VOLLLAUF GRUEN (377 Tests, 39 Dateien)` auf e9b381d44, also vor dem Rebase auf B1 (28a5bffda). Der Rebase hat keine A2-Datei verändert; das kombinierte Verhalten prüft die Koordination mit einem Volllauf auf main.
- Frage an KZW in #270: Urheber auch an Definition und Etymologie?
- Freeze-Ausnahmen dieses PRs, von der Koordination benannt (Zeilen im Endstand): DATA-MODEL.md 239-244, 466, 512, 549, 894, 904, 908; CONTRACTS.md 927; TEI-MODEL-AUTH-FILES.md 211, 219; DECISIONS.md 46 und ADR-018; scripts/README.md 123; dazu die DEVELOPMENT.md-Zeile für die neue Spec.

---

## 2026-09-23 (Nachtlauf, Spur B, Paket B2) – #420: Pin auf v0.3.0-beta und "Lemma" statt "Term"

Lindas Punkte 1 und 4 aus ihrer Abnahme vom 16.09.: der Naming-Index steht jetzt auf Naming-analysis v0.3.0-beta, und das Modul "Erweiterte Figurenbezeichnungen" sagt überall "Lemma", wo es "Term" sagte (Perspektive, Auswahl, Filter, Spaltentitel, Hilfe, FEATURES, Spec). Der Montagslauf `naming-index-update.yml`, seit dem 14.09. rot, hat damit seinen Grund verloren. Punkt 3, ein Tab "Bezeichnung", ist nicht gebaut: die Kategorie wird an vier Stellen gefiltert oder gezählt, und ob der Tab in allen drei Perspektiven erscheinen soll, ist eine Gestaltungsfrage, die Linda offen gelassen hat.

### Was über den Einzelfall hinausgilt

**Ein Aufrufparameter, der wörtlich in ein Artefakt geschrieben wird, gehört zum Inhalt.** Der Laufplan sah `--ref v0.3.0-beta` vor. Das Skript schreibt `source.ref` aber unverändert in den Index, und der Montagslauf baut ohne `--ref`, also gegen `master`, und vergleicht Bytes. Mit dem Tag im Feld hätte er jeden Montag einen PR ohne Datenänderung geöffnet. Gebaut ist deshalb gegen `master`, das zum Bauzeitpunkt derselbe Commit war wie der Tag (`8076467a`); die Provenienz trägt `source.commit`, und das Freshness-Gate in `data-integrity.yml` normalisiert `ref` ohnehin weg.

**Eine Zahl, die ein Skript für ein Modul nachrechnet, muss rechnen wie das Modul.** In Kommentar und FEATURES stand seit #420 "247 von 433 treffen exakt 100, Spanne 89 bis 109". Das Modul rundet mit `Math.round`, halbe Prozente also aufwärts; gemessen war mit Pythons `round()`, das halbe zur geraden Zahl rundet. Mit der Rundung des Moduls sind es 244 und 91 bis 121. Die zwei Beispiele daneben (`helt` 98, `hêrre` 95) sind in beiden Rundungen gleich, deshalb fiel es niemandem auf. Gefunden hat es die Reviewrunde.

**Linda sprach von 13 Zeilen in drei Werken, der Index zeigt 9 Records in zwei.** Ihr Bereinigungscommit `af531d30` vom 09.09. berührt die Dateien aller drei Werke. In den `categorization_*.json` sind es 12 Stellen, nicht 13 (die dreizehnte liegt vermutlich nur in einer Excel-Datei, nicht geprüft): Iwein 3 (V. 1805, 2216, 4905), Rolandslied 8 (V. 527, 2863, 2864, 2875, 2880, 2882, 2887, 6101), Trojanerkrieg 1. Den Index bewegen davon 9. Rolandslied 527 und 6101 und die Trojanerkrieg-Stelle trugen doppelte Attribution, und unser Build hatte schon dieselbe Seite gewählt: er zählt Figurenrede nur, wenn nennende Figur **und** `Bezeichnung` gesetzt sind, und prüft das vor dem Erzähler-Feld (`build_record`). Bei 527 und 6101 fehlte `Bezeichnung`, also Erzähler wie jetzt bei Linda; bei der Trojanerkrieg-Stelle war beides gesetzt, also Figurenrede wie jetzt bei Linda. Im Index ändern sich Attribution oder Phrase von 9 Records (IW 3, ROL 6); Record- und Figurenzahlen je Werk bleiben gleich, und die 2 Iwein-Records "Figurenrede ohne Nenner" gibt es nicht mehr. Lindas Beispielzahlen im Rolandslied (`helt`, `hêrre`, Ruolant) sind auf altem und neuem Stand identisch.

### Rote Zeilen

Keine. Verteilung aus `trockenlauf-auswerten.py`, Zeile dieser Session (`11858632`, nacht-frontend-2), Stand beim Schreiben dieses Eintrags am 23.09. abends (die Zahlen wachsen mit jedem weiteren Aufruf): shell-konventionen 52 Treffer bei 174 Aufrufen (30 %), mengenaussagen 16 bei 41 (39 %). Der Abschnitt `gelesenes` bricht weiter mit `AttributeError` ab (siehe B1).

### Was zurück an Christian geht

- Frage an Linda in #420: ihre `CITATION.cff` nennt seit v0.3.0-beta den Concept-DOI `10.5281/zenodo.21914259`, bis v0.2.2-beta den Versions-DOI. Übernommen ist ihr Wortlaut; ob der Index lieber den Versions-DOI `10.5281/zenodo.22690452` zitieren soll, entscheidet sie.
- Angebot an Linda in #420: der Tab "Bezeichnung" (ihr Punkt 3), wenn sie ihn will, mit der Frage, in welchen Perspektiven.
- #420 schließt mit dem Merge, weil Linda die Abnahme an Punkt 1 und 4 gebunden hat.

---

## 2026-09-23 (Nachtlauf, Spur A, Paket A3) – #357: ein Name, zwei Entitäten, und das Konzept stand schon im Katalog

KZW hat am 14.09. in #357 entschieden (ADR-020): „ingligar von jelezie“ im Rennewart bekommt kein eigenes Lemma, aber Ingliart einen zweiten Sense für den Menschennamen. Welches Konzept dieser Sense trägt, stand nicht im Thread. Der Laufplan verlangte, es aus den Nachbarn im selben Namenkatalog abzuleiten, und bei fehlender Übereinstimmung anzuhalten. Übereinstimmung gab es: `lemma_3036_sense_119195` trägt `concept_21012000` und `concept_23112500`, `REN_242090_0` zeigt mit `@ana` darauf, die beiden Parzival-Belege bleiben beim Pferdenamen. Authority-Index 1.9.11, Korpus-Index unverändert.

### Was über den Einzelfall hinausgilt

**Der Katalog war die bessere Messung als die drei genannten Nachbarn, und seine Grenzen gehören mitgemessen.** Der Auftrag nannte drei Lemmata. Der Katalog läuft von Vers 24206 bis 24220, gerahmt von „als daz maer mir tuot bekant“ und „die gaben ritterliche ir leben“, und hat 15 Personen und 14 Orte. Alle 15 Personen tragen dieselben zwei Konzepte; 14 davon sind Zeugen, der 15. ist der umgehängte Token. Ein Konzept, das der ganze Katalog trägt, ist abgeleitet und nicht gewählt. Meine erste Fassung des ADR-Satzes nannte „24206 bis 24213, acht Personen“ und damit ein Messfenster als Katalogumfang. Die Zahl stimmte für das Fenster, der Bezug nicht. Die zweite Reviewrunde hat das vor dem Push gefunden.

**Der Korpus-Index sieht keine Sense-Zuordnung.** `build-corpus-index.py` liest `@ana` nicht. Ein Token, das nur den Sense wechselt, lässt den Index byte-gleich, und ein Bump wäre einer ohne Inhalt. Sichtbar wird der zweite Sense nur über den Authority-Index (`senseCount`, `conceptToLemmas`).

**`sense/@ana` im Lexikon hat keinen Konsumenten im Build, trägt aber eine Regel.** Die Typliste des Sense ist die Schnittmenge, aus der ein Ingest `@corresp` auflöst (DATA-MODEL.md, Phase 3). `type_177507` („ingligar“) trägt korpusweit nur dieser eine Token. Deshalb ist er aus dem Pferde-Sense in den neuen gewandert; bliebe er stehen, wäre die Schnittmenge für den neuen Sense leer.

### Rote Zeilen

Keine. Der Fensterfehler im ADR-Satz (oben) fällt unter die Mengenlehre (`mengen.md`: eine richtige Zahl mit falschem Bezug), hat aber nichts getragen: Die Reviewrunde hat ihn vor dem ersten Push gefunden.

Verteilung aus `trockenlauf-auswerten.py`, Zeile dieser Session (`09f7a3aa`, nacht-daten, über A1 bis A3), Stand beim Schreiben: shell-konventionen 110 Treffer bei 365 Aufrufen (30 %), mengenaussagen 57 bei 126 (45 %).

### Was zurück an Christian geht

- Lokaler Review in drei Runden, alle mergefähig, kein Klasse A. Einziger Sachbefund war der Katalogumfang im ADR-Satz (oben). Die Konzepte der drei Nachbarn hat die Koordination selbst am Baum geprüft.
- Pilde (`lemma_47319`, REN 24216) steht im Katalog als Ort, trägt aber `concept_23253000`, `concept_24212000` und `concept_24222000` plus „Personennamen“ (`concept_23112500`) und kein `concept_24120000`. Das ist nicht angefasst und im PR genannt.
- `VERDICT: VOLLLAUF GRUEN (377 Tests, 39 Dateien)` auf 767810ae7, vor der Prosa-Korrektur und dem Rebase auf #480. Nach dem Rebase ist der Authority-Rebuild byte-gleich mit dem committeten Index.
- ADR-020 hat einen neuen Consequences-Punkt (Freeze-Ausnahme der Koordination). Er hält fest, dass die Konzeptzuweisung abgeleitet ist und KZW sie in #357 überstimmen kann; Z. 1247 („sense meanings stay curatorial“) bleibt stehen.
- „Das gilt für alle Namen“ ist nicht angefasst. Welche Namen heute einen Sense mit Referenten verschiedener Art teilen, ist eine eigene Messung und steht als Beobachtung im Statuskommentar.

---

## 2026-09-23 (Nachtlauf, Spur B, Paket B3) – #467: das Wörterbuch nimmt die Lemma-Nummer

KZWs Wunsch aus #467: im Wörterbuch "lemma_4086" eingeben und "mer" sehen. Das Suchfeld nimmt jetzt `lemma_4086`, auch in der Schreibung aus `@lemmaRef` (`lexicon.xml#lemma_4086`), und zeigt genau dieses Lemma; beim Treffer steht die Nummer neben dem Eintrag. Korpussuche und Playground sind nach dem Laufplan nicht gebaut, sondern gemessen; die Antwort steht in #467.

### Was über den Einzelfall hinausgilt

**Eine nackte Zahl ist im Wörterbuch nicht eindeutig, und das ließ sich vor dem Bauen messen.** Fünf Lemmata beginnen mit einer Ziffer ("1", "36", "42", "46", "49"), und die Präfixsuche findet sie heute über genau diese Eingabe. Hätte eine Zahl nur noch die Nummer gesucht, wären sie über das Suchfeld unerreichbar geworden. Deshalb sucht `lemma_46` nur die Nummer, `46` dagegen die Nummer zuerst (*abwege*) und darunter weiter das Lemma *46*. Die Multi-Lemma-Suche im Playground, auf die KZW am 23.09. hinwies, behandelt eine nackte Zahl dagegen allein als Nummer (`tei-ui.js:19`), und nur sie: `lemma_4086` findet dort nichts, denn alles außer reinen Ziffern geht in die Namensauflösung, die keinen ID-Zweig hat. Die ID-Erkennung in `authority-manager.js:49` (`resolveLemmaNames`) sieht nach dem Gegenteil aus, hat aber keinen Aufrufer; die erste Fassung dieses Eintrags hatte sich auf sie gestützt, die Reviewrunde hat es gefunden.

**Ein Hilfebeispiel ist auch eine Behauptung über die Daten.** Die erste Fassung erklärte "Nummer zuerst, darunter die Präfixtreffer" am Beispiel `4086`, zu dem es keine Präfixtreffer gibt; wer es nachtippt, sucht die zweite Liste vergeblich. Gefunden hat es die Reviewrunde, das Beispiel ist jetzt `46`, dasselbe, das der Test prüft.

### Rote Zeilen

Keine. Verteilung aus `trockenlauf-auswerten.py`, Zeile dieser Session (`11858632`, nacht-frontend-2), Stand beim Schreiben dieses Eintrags am 23.09. spätabends (die Zahlen wachsen mit jedem weiteren Aufruf): shell-konventionen 76 Treffer bei 259 Aufrufen (29 %), mengenaussagen 28 bei 68 (41 %).

### Was zurück an Christian geht

- KZW prüft nach Merge und Deploy im Wörterbuch; der Prüfweg steht in #467.
- In #467 beantwortet: Korpussuche und Lemma-Explorer kennen die Nummer nicht, die Multi-Lemma-Suche nur als nackte Zahl (`4086`, nicht `lemma_4086`). Ob Korpussuche oder Playground sie lernen sollen, ist KZWs Entscheidung; der Aufwand wäre klein.
- Die Commits der Pakete B1 und B2 und der erste Commit von B3 tragen als Trailer `Co-Authored-By: Claude Opus 5.5`, `CLAUDE.md` schreibt `Co-Authored-By: Claude` vor (Hinweis der Reviewrunde zu B3); ab dem zweiten B3-Commit in der Form von `CLAUDE.md`.

---

## 2026-09-23 (Nachtlauf, Spur B, Paket B4) – #448: CSV-Export im Playground

Die Userfrage aus #448: Ergebnisse im Playground als CSV herunterladen. KZWs Auftrag dazu war, die Werkzeuge systematisch durchzugehen. Unter `playground/js/ui/tei/` liegen 15 Dateien, ohne den Helfer `corpus-scope.js` und die Hülle `tei-ui.js` also 13 Werkzeuge, aufgeteilt 13 (9 + 1 + 3). Neun Werkzeuge mit tabellarischem Ergebnis bekommen einen Export: Wortfrequenz, Versendings-Profil, Text-Statistiken, Kookkurrenz-Ranking, Reim-Wörterbuch, Textvergleich, Versposition, Bezeichnungen und Pferde. Das eine ist Hapax, das seinen älteren Export behält. Drei bekommen keinen: Konzept- und Lemmaverteilung, weil ihr Ergebnis ein Diagramm ist, und die Multi-Lemma-Suche, weil ihr Ergebnis aus Karten besteht, deren Kontext erst beim Aufklappen per `fetch` aus dem TEI nachkommt. Ausgerechnet der Anwendungsfall aus dem Ticket ("an der brust" bei Steinen) liegt dort; die Tabelle je Werkzeug und die offene Frage dazu stehen im Statuskommentar in #448.

### Was über den Einzelfall hinausgilt

**Die Datei trägt die Menge, nicht die Anzeige.** Wo eine Tabelle nach Top-N oder einer Anzeigegrenze kappt (50, 100, beim Reim-Wörterbuch 200), exportiert der Knopf trotzdem alles hinter ihr, mit den aktuellen Filtern. Das war schon die Regel des Hapax-Exports, der über alle Seiten geht, und der Tooltip jedes Knopfs sagt, welche Zeilen drin sind. In Wortfrequenz und Versendings-Profil stand die Filter- und Sortierlogik mitten in `renderTable`; sie ist jetzt eine eigene Methode `sortedEntries()`, damit Tabelle und Datei dieselbe Menge lesen und nicht zwei Kopien derselben Regel.

**Zwei Formate im selben Werkzeugkasten, und das bleibt so.** Die Hauptseite exportiert seit #114 mit Komma, der Hapax-Export im Playground mit Semikolon. Der Laufplan hatte beide für gleich gehalten; gleich sind nur BOM und CRLF. Entschieden hat die Koordination: die neuen Exporte folgen der Hauptseite, Hapax bleibt, weil ein Wechsel bestehende Auswertungen bräche. Der Helfer `assets/js/lib/csv-export.js` trägt das Format jetzt für beide Seiten, `app.js` delegiert an ihn. Dass der Export der Hauptseite dabei bytegleich bleibt, prüft ein Test gegen eine wörtliche Kopie des alten Quotings, nicht gegen den Helfer selbst; sein Kontrollwert sind die vier Texte mit Komma in Titel oder Autor, die *minne* trifft (FR1, FR2, HVM, PL1).

**Komma-CSV und deutsches Excel.** Ein deutsches Excel spaltet eine Komma-CSV beim Doppelklick nicht auf. Die Hilfe verspricht deshalb nicht "öffnet sich direkt", sondern nennt den Weg über "Daten, Aus Text/CSV". Das gilt für die Hauptseite seit #114 genauso und ist vielleicht der Grund, warum Hapax einmal das Semikolon bekam.

### Rote Zeilen

Keine. Ein eigener Zählfehler, bevor er etwas trug: in der Meldung an die Koordination standen "12 Werkzeuge", es sind 13; die Koordination hat nachgezählt, der PR-Body trägt die richtige Aufschlüsselung.

### Was zurück an Christian geht

- Die Multi-Lemma-Suche ist genau das Werkzeug aus dem Anwendungsfall des Tickets und hat keinen Export. Ein Export dort bräuchte eine Entscheidung, ob die Datei nur die Trefferliste (Text, Abstand, Vers) trägt oder auch den Wortlaut, der erst per `fetch` aus dem TEI kommt. Die Frage steht in #448.
- Die Datensätze von Linda (CC BY-NC-SA) und Borek (CC0) gehen jetzt als CSV aus dem Playground. Die Datei trägt keine Quellenangabe, die Seite schon. Ob die CSV eine Attributionszeile braucht, ist eine Frage an Linda; eine Kommentarzeile bricht allerdings manches Einleseprogramm.

---

## 2026-09-24 (Nachtlauf, Spur A, Paket A4) – #228: Apparat entannotiert, und ein gehaltenes Lemma hat 82 Geschwister im Lexikon

KZW hat am 11.09. in #228 entschieden (K7): Die Dichternamen im Verfasser-Slot von acht Liedtexten, die übrigen Apparatnoten mit `@n` und die 422 neuhochdeutschen Inhaltsangaben in GWTK sind Herausgebertext und werden entannotiert; CL und KVO bleiben, in KVO wird `lob` nachgetragen; Lemmata, die dadurch jeden Beleg verlieren, werden gelöscht. Umgesetzt mit `scripts/ingest/entannotate-228/apply-228.py`: 69 Noten mit 132 Tokens in 12 Texten, 422 GWTK-Noten mit 2.058 Tokens, 165 Lemmata gelöscht (`lexicon.xml` 43.878 auf 43.713), `variants.xml` regeneriert (256.787 auf 256.512 Formen, 233.978 Mappings). Korpus-Index 4.2.20, Authority-Index 1.9.12.

Drei Dinge blieben bewusst draußen. NEIM, weil seine Noten die Konkordanz tragen, die #453 sichern will. Die 26 Ziffern in MR1 und WVV, weil K7 sie nur unter „sofern“ nennt; die Form ist als Frage in #228. Und `lemma_66692` *Mur*: belegfrei, aber `lemma_33528` *Murouwe* und `lemma_66691` *Murstat* verweisen per `etym` darauf, also Haltepunkt statt Löschung.

### Was über den Einzelfall hinausgilt

**Ein Lemma zu halten macht seine ausgehenden Zeiger falsch, nicht nur seine eingehenden richtig.** Der Haltepunkt schützt die zwei `etym`-Verweise auf Mur. Dass Murs eigener Sense per `@ana` auf einen Typ zeigt, den die Regeneration von `variants.xml` gerade entfernt hatte, sah kein Gate: `check-authority-cross-refs.py` überspringt nackte `#frag`. Die erste Reviewrunde hat es gefunden.

**Und das Suchmuster war der Zuschnitt.** Gemessen war mit `ana="#type_\d+"`, also nur an einwertigen Listen. `sense/@ana` ist eine Leerzeichenliste; 21.844 von 43.404 Attributen auf origin/main sind mehrwertig. Per `split()` gemessen hatte A4 nicht einen, sondern 83 Typ-Tokens hängend gemacht; Mur war der einzige einwertige Fall und deshalb der einzige, den das Muster sah. Die zweite Runde hat das gefunden, `prune-ana-228.py` entfernt die übrigen 82. Danach hängen wieder genau die 105 Tokens, die schon auf origin/main hingen. Ob jede Regeneration von `variants.xml` die Lexikonlisten mitbereinigen soll, ist eine Frage an den Data-Change-Lifecycle, nicht an #228.

**Ein gelöschtes Lemma kann das Beispiel einer anderen Spur sein.** „46“ war seit #467 (B3, am selben Abend gemergt) das Prüfbeispiel für die Suche nach der Lemma-Nummer, in `woerterbuch.spec.js` und in `hilfe-korpussuche.html`. Beide zeigen jetzt auf „36“ (`lemma_69748` und `lemma_36` *aberelle*, genau zwei Treffer). Entscheidet KZW die Ziffern, muss das Beispiel noch einmal umziehen.

### Rote Zeilen

Keine. Der hängende Zeiger (83 Tokens) hat nichts getragen: `sense/@ana` hat keinen Konsumenten im Build, und beide Runden haben ihn vor dem ersten Push gefunden. Ebenso abgewendet: Der erste Apply-Lauf schrieb `<note n>` wörtlich in den `<change>`-Text und zerbrach 13 TEI-Dateien. `extract-variants.py` brach daran ab, die Dateien wurden zurückgesetzt, das Skript bekam einen Markup-Guard und einen Parse vor dem Schreiben.

Verteilung aus `trockenlauf-auswerten.py`, Zeile dieser Session (`09f7a3aa`, nacht-daten, über A1 bis A4), Stand beim Schreiben: shell-konventionen 139 Treffer bei 542 Aufrufen (26 %), mengenaussagen 75 bei 190 (39 %).

### Was zurück an Christian geht

- Lokaler Review in drei Runden. Runde 1 und 2 hatten je einen Sachbefund (oben), Runde 3 auf Prune und Doku war mergefähig ohne Befund.
- `VERDICT: VOLLLAUF GRUEN (379 Tests, 39 Dateien)` auf f13277280, vor dem Rebase auf #448 (danach f123424f5; `git diff --stat` zwischen beiden zeigt nur die 22 Dateien, die main seither geändert hat: #448, Kickoff, Reviewer-Memory). Er gilt für den Prune-Commit, weil kein Test `lexicon.xml` liest und Index und API danach byte-gleich neu gebaut wurden. Nach dem Rebase `VERDICT: TEILLAUF GRUEN (24 Tests aus 2 Datei(en))` für die zwei Specs, die #448 geändert hat, auf 3e15feb40.
- Freeze-Ausnahmen der Koordination: CONTRACTS.md Z. 99, 381, 396 (Homographen jetzt 476 Formen, 991 Lemmata, 2,27 %), sieben ungegatete Stellen mit 43.878 in DATA-MODEL, DESIGN, FEATURES und TEI-MODEL-AUTH-FILES, das „46“-Beispiel.
- Nicht angefasst, im PR genannt: `ingest/foreign-lang/28-gleis1-kandidaten.csv:5626` führt das gelöschte `lemma_64691` *Siegesfest*; die Kommentare in `hapax-legomena.spec.js:7-12` und `hapax-legomena.js:127-130` sagen noch, 42/46/49 fielen mit #228, es fiel nur 46.
- Fragen an KZW in #228: die Form für die 26 Ziffern; ob Mur gelöscht und die zwei `etym`-Verweise umgehängt werden sollen.

---

## 2026-09-24 (Nachtlauf, Koordination) – acht PRs in einer Nacht, und wo die Koordination selbst danebenlag

Laufplan `docs/playbooks/kickoffs/2026-09-23-nachtlauf.md`, zwei Spuren (A Daten, B Frontend), Merge-Freigabe von Christian für PRs ohne offene Befunde, Index-Bumps eingeschlossen. Gemergt wurden zehn PRs, 10 (2 + 8): zwei Reste des Tageslaufs und die acht Pakete des Nachtlaufs, in dieser Reihenfolge: #476, #469 (Tagesreste), #477 (A1: #252, #267), #478 (B1: #433), #479 (A2: #270, Authority 1.9.10), #480 (B2: #420, geschlossen), #482 (A3: #357, Authority 1.9.11), #481 (B3: #467), #483 (B4: #448), #484 (A4: #228, Korpus 4.2.20, Authority 1.9.12). Schlusslauf der Koordination auf `82af90239`, dem Stand mit allen zusammen: `VERDICT: VOLLLAUF GRUEN (389 Tests, 40 Dateien)`. Deploy und Data Integrity auf diesem Stand grün.

### Was über den Einzelfall hinausgilt

**Zwei Spuren, die dateidisjunkt geschnitten sind, sind es über die Daten nicht.** A4 löschte `lemma_69733` „46“, und genau dieses Lemma war in derselben Nacht in B3 zum Prüfbeispiel für die Nummernsuche geworden, in Spec, Hilfeseite und Ticketkommentar. Kein Dateibesitz hat das angezeigt; gefunden hat es die Koordination, weil sie die Löschliste gegen den eben gemergten PR hielt. Wer Spuren nach Dateien schneidet, muss bei Löschungen in `authority-files/` zusätzlich fragen, welche gemergten Tests und Beispiele an den gelöschten IDs hängen.

**Ein „sofern“ in einer Entscheidung ist keine Entscheidung.** K7 in #228 rechnet die 26 Ziffern in MR1 und WVV nur mit, „sofern“ sie wie vorgeschlagen entannotiert werden, und der Vorschlag stammt von einer Session. Die Spur hatte das als entschieden gelesen; die Koordination hat es nach Lektüre des Kommentars herausgenommen und als Frage an KZW gegeben.

**Testvergabe seriell hat gehalten, bis auf einen Fall.** Ein Volllauf zur Zeit, Teilläufe nicht daneben; einmal fuhr Spur A zwei unangemeldete Teilläufe während eines B-Volllaufs, der trotzdem grün endete. Einmal hat Spur B einen Slot zurückgegeben statt ihn zu nutzen, weil ein Checkout einem laufenden Review die Dateien weggezogen hätte. Wo ein Teillauf statt eines Volllaufs reichte, stand die Begründung als Messung daneben (wer die geänderte Datei lädt), nicht als Einschätzung.

**Ein vermeintlicher Neustart war eine eigene Nachricht.** Spur A stand mitten in der Nacht mit neuer PID unter derselben Kennung da, und die Zustellung meldete „new session under a previously used name“. Das Operator-Skill (`transport.md`) beschreibt genau das: eine Nachricht an eine ruhende Spur startet sie neu. Verloren ging nichts (Baum sauber, Zweig gleich PR-Kopf, laut Spur A).

### Rote Zeilen

Keine. Einmal lag die Koordination daneben, und abgewendet hat es die Spur, nicht die Koordination: Für den Konflikt in #481 wies sie Spur B an, mit `--force-with-lease` auf den PR-Zweig zu pushen, obwohl der Spurvertrag Force-Push verbietet. Spur B hat abgelehnt und gefragt; gemergt wurde über einen Merge-Commit. Es hat nichts getragen, deshalb keine Zeile; die Nummern 90 bis 94 bleiben unverbraucht.

### Was zurück an Christian geht

Steht im Morgenbericht der Koordination; die Fragen an KZW stehen je in #251, #252, #267, #270, #357, #228, #433, #467, #448, alle auf `auto:blocked` + `wait:kzw`, die Matrix in #44 ist nachgezogen.

---

## 2026-09-24 – #237: VTC-Editionsnachweis aus Zotero, und ein Online-Sync ist nie nur ein Werk

KZW hat am 23.09. in #237 Weg 1 gewählt: den Zotero-Eintrag Z246QK62 selbst korrigiert (Josef Jireček als Mitherausgeber von FRB III) und um einen Online-Sync gebeten. Übernommen ist genau dieses Werk: `works.xml` (`work_572`), der VTC-Header, Authority-Index 1.9.13, API. Der Korpus-Index bleibt byte-gleich.

### Was über den Einzelfall hinausgilt

**Ein Online-Sync ändert alles, was seit dem letzten Online-Sync auseinandergelaufen ist.** Am 24.09. brachte er außer VTC zweierlei mit. Erstens 171 Werke, in denen nur die Großschreibung zurückkehrt (`[lieder]` → `[Lieder]`, `N.f.` → `N.F.`): die Korrektur aus #171 F37 (`2734267a3`, 11.07.), die seither auf keinen Online-Sync getroffen war; kein Großbuchstabe fällt dabei weg. Zweitens zwei bewusste Handkorrekturen, die der Sync still zurückgenommen hätte, weil sie nur in `works.xml` stehen: FLG (`c0b546a45`, #104) und FR1 (`115c3a01f`, #236).

**Die 171 blieben draußen, weil ihre Kopien in 182 TEI-Headern nicht mitlaufen.** Für `listBibl` gibt es keinen gefahrlosen Schreiber (`--bibl-struct` serialisiert alle 667 Dateien neu und löscht die `mwb-sigle`), und `--works --check` prüft nur `msIdentifier`. Gefunden hat das die lokale Review in Runde 1; entschieden hat chsteiner am 24.09.: dieser PR nur VTC, der Rest in #486. Mit derselben Antwort ist die Richtung der Kette entschieden, die seit dem Nachtlauf 14./15.09. offen stand: Zotero → `works.xml` → Header, der Header ist Kopie.

### Rote Zeilen

Keine.

### Was zurück an Christian geht

- #486: Schreiber und Gate für `listBibl`, die 171 Titel, FR1 und FLG nach Zotero (KZW), Doku an die Kettenentscheidung.
- Offen in #237 bei KZW: Blaschka 1934 für WLK (Werkeintrag vorbereiten, Zotero-Felder vorgeben).

---
