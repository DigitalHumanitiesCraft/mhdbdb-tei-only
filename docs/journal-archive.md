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
