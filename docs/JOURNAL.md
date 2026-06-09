# MHDBDB Development Journal

Chronological log of development decisions, dead ends, and savepoints. Not a changelog — captures the *reasoning* behind changes.

---

## 2026-06-05 — Health-Check (/promptotyping check)

**Scorecard:** Multi-Agent-Check (Workflow `wam0cgdyr`, 103 Agenten, ~62 min; 19 Probes = 15 Doc-Finder + 4 Canary für Algorithmen/XPath/Versionen/Konsistenz; jeder Befund adversarial gegen Code/Daten verifiziert): **83 Befunde geprüft, 55 bestätigt, 28 adversarial gefiltert** (kein Fehlbefund durchgerutscht). Nach Konsolidierung ~24 distinkte Drifts, **alle gefixt** (15 Dateien: CLAUDE.md + 13 Stable-Docs + Corpus-Index-Rebuild). **Hauptbefund:** Doku hinkt dem Playground-Feature-Wachstum (#47.3, #87-90, #47 R2, #107, #108) hinterher – Entry-Points 10→14, Module 18→21, „Sieben"→„Neun Werkzeuge" über INDEX/FEATURES/ARCHITECTURE/DECISIONS/DESIGN nachgezogen. **Drei fabrizierte Worked-Examples** in TEI-MODEL-AUTH-FILES korrigiert (alle gegen Quelldaten verifiziert): `lemma_879` = brôt (nicht „vriunt"; vriunt = lemma_7246), sense `_1449` (nicht `_1177`), variants type_2783/2784/2785; `work_350`/ASG ohne die transplantierten work_177-Normdaten (GND/Wikidata/HSC); `person_anonym` (Anonym, Wikidata Q4233718) entkoppelt von `person_1772` (Schweizer Anonymus, GND 103130276). **Wörterbuchnetz-API** (ARCHITECTURE/CONTRACTS): „BMZ, Lexer, LexerN, FindeB" + `Promise.allSettled` → real MWB+Lexer + `Promise.all`; statischer MWB-Trier-Link entfernt (ist API-Deep-Link). **TEI-File-Caching** (FEATURES, ARCHITECTURE) invertiert: „>5MB"→jede Datei, „No expiration"→30d (Main-Site); Playground-`indexed-db-manager.js`-Stores korrigiert (4 reale statt 2 erfundene). **§4-Migration** (`@meaningRef`→`@ana`, `@wordRef`→`@corresp`) korpusweit abgeschlossen inkl. WZB (667/667 `@ana`, 0 Alt-Attribute, 0 JS-Leser) – war als „ausstehend/Validierungsblocker" geframt, jetzt als erledigt (Phase B1/B2). **Weitere:** `validate-corpus.py` „8 strukturelle Checks"→zweistufige RelaxNG; stanza „wird migriert"→erledigt (#23/v4.1.1); „25 skipped tests #43"→0 (resolved 259bc505a); variants ~234k→~257k (256.759); works.xml 583→584; LINECODE #84/#85 closed, div/@type 7→7+24 arithmetic; diverse Zeilennummern-Pointer + Quellen-Refs (526-571→643-644 u.a.). **Rebuild:** Corpus-Index neu gebaut (clear Freshness-Gate nach #115 @corresp-Cleanup; Inhalt identisch außer `generatedAt`, **kein Versions-Bump** – v4.1.3 bleibt; Gate ist commit-history-basiert, wird mit dem Index-Commit grün; CI-Wiring + Determinismus deckt #125). **Blind-Spots (8, 1 blocking):** Ingest-Pipeline-Rebuild-Test scheitert → #132 (Phasenmuster aus README/BLOG in Stable-Doc heben); Encoding-Exemptions-Liste → #133; #92-Status-Drift (Stage 0 gebaut + PD-001 offen) kommentiert; site-chrome-„nicht-direkt-editieren"-Constraint in CLAUDE.md-Gotchas ergänzt. **Offen-notiert (kein Issue):** variants-Terminologie (entries 42.627 vs forms 256.759 vs Index-Keys 234k nirgends sauber definiert); `docs/features/`-Lifecycle (#034-Pentateuch-Scope, #114). Methodik: adversariale Verifikation + Blind-Spot-Kritik. Grade: solide – keine falsche Kerninvariante (Position-Counting §A/§B, MHG-Normalisierung, lemma-match alle korrekt verifiziert).

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

## 2026-06-02 — Health-Check (/promptotyping check)

**Scorecard:** Multi-Agent-Check (Workflow `wpq1w301u`, 6 Dimensionen, jeder Befund adversarial gegen Code/Daten verifiziert): **26 Drift-Befunde bestätigt, 1 Fehlbefund gefiltert** (fabrizierter works-Count, der im Doc gar nicht vorkam — adversarialer Schritt hat funktioniert). Alle 26 in diesem Pass gefixt (13 Dateien). **Hauptbefund:** Der Site-Chrome-Refactor (Vorsession) hinterließ Doku-Schuld — `build-pages.py`, `includes/`, `site-chrome.js` standen in KEINER Stable-Doc (nur JOURNAL); der damalige Eintrag (2026-06-01 15:29, „kein Architektur-Change, der Doku-Update bräuchte") hatte den nötigen Update wegargumentiert. Nachgezogen: ARCHITECTURE (neues Pattern „Build-Injected Site Chrome" + Key Files), DEVELOPMENT (Frontend-Build-Commands inkl. `build-pages.py`/`build:css`/`build:vendor`, Directory um `includes/`+`site-chrome.js`+`hilfe-schema.html`), DESIGN (Nav/Footer/Mobile-Menü → `site-chrome.js`, falsche „No active-page highlighting"-Aussage korrigiert), scripts/README (Baum + Spalte-E-Fix). **Zahlen-Sync:** Corpus-Index 34→40 MB (5 Docs), variants 39.282/192.472 → 42.627/256.759 (TEI-MODEL), ~670→667 TEI (CLAUDE), Authority-Index 2.90→3.1 MB (DECISIONS). **Algorithmen:** §B um `iterwalk` + Empty-Text-Skip-Parity ergänzt (latent, 0 Korpus-Fälle, → in #131 aufgenommen); §C.2.1 falsche Zeile/Funktionsname, §C Off-by-one, `@ana`-Phantom (DATA-MODEL), `indexed-db-base.js`-Phantom (lib/README). **#130-Nachzügler:** `lemma-match.js` in CLAUDE Key-Patterns + ARCHITECTURE Pattern + lib/README + DEVELOPMENT lib-Zeile. **Korrektur-Aktion:** #131 (§B-Paritätstest) um den Empty-Text-Skip-Fall erweitert. **Doc-Schuld-Lehre:** Build-Pipeline-Erweiterungen (neue Skripte/Partials/geteilte Module) gehören in DEVELOPMENT + ARCHITECTURE, auch ohne Schema-Change. Methodik: 33 Agenten, ~6 min. Grade: solide; Stable-Docs jetzt konsistent mit verifizierten Code/Daten-Werten.

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

## 2026-06-01 — Health-Check (/promptotyping check)

**Scorecard:** Authority-Source-Docs (ADR-015, CONTRACTS §F, DATA-MODEL Lifecycle, INDEX, TEI-MODEL-AUTH-FILES) konsistent; 3 Algorithmen + 3 XPaths code-konform. Fixes diesem Pass: TEI-MODEL §11 Authority-Index-Version war stale (1.3.0 → 1.4.0); CONTRACTS bekam neuen §B.1 „Lemma Highlight Matching" (token-exakt, #126) + Z.77-Korrektur (Highlighting ist `@lemmaRef`-, nicht positions-basiert); Lemma-Zahl 43.750 → 43.754 vereinheitlicht (DATA-MODEL/FEATURES/TEI-MODEL-AUTH-FILES); CLAUDE.md Varianten-Dict 176k → ~234k und Index-Versionen v1.2.0/v4.0.0 → v1.4.0/v4.1.3; ARCHITECTURE + CLAUDE Key-Patterns um das Matching ergänzt; DATA-MODEL ptr-XPath Doppel- → Einfach-Slash. **Lücke → #130:** keine Testabdeckung für Lemma-Matching-Exaktheit (#126 shippte ungetestet). **Bekannt:** Corpus-Index stale seit 2026-05-15 (gutartig, #125). **Fehlbefund gefiltert:** ADR-015 ist sehr wohl in DECISIONS.md (Blindspot-Agent irrte). Grade: solide. Methodik: 5-Agenten-Check-Workflow + manuelle Verifikation der Blocking-Claims.

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

> **Komprimierung 2026-05-28:** Die Handoff-Einträge zwischen 2026-04-10 und 2026-05-08 wurden auf ihre Kern-Decisions und permanent gültigen Lessons verdichtet (Originale in `git log`, ROADMAP „Recently Completed" enthält die Issue-Refs). Ab 2026-05-11 alles verbatim.

## 2026-04-10 17:00 — handoff (#32 feature-complete)

#32 TEI Model Consolidation gemergt (PR #69 Corpus + PR #71 Authority). Deep Schema Audit: 11 Gaps, **`div` ist RNC-Keyword (root cause RNC→RNG-Failure → `tei.div`)**. 666/666 valid. Authority Migration F-K parallel: works.xml 3,422 genre-`<ref>` → 870 `<ptr/>`, persons listBibl removed (derived from works.xml). Code-Review fand 3 Pre-Merge-Bugs (`@ana` in `resolveConceptReferences`, `<pc>`-Wrapper im zweiten Renderpfad, `etree` round-trip). Branch protection auf `main`. 121/121 Tests. **Carryover:** #20 Lesbarkeit, #52 Authority Card.

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
