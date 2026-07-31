# MHDBDB Development Journal

Chronological log of development decisions, dead ends, and savepoints. Not a changelog – captures the *reasoning* behind changes.

---

## Verdichtete Historie

Hochrangiger Trace der Einträge 2025-02 bis 2026-07-10. Volltext aller 68 verdichteten Einträge in `journal-archive.md`.

**2025-02 (Phase 0 + #42):** Stabilisierung vor #42 – Wenzelsbibel (652k Zeilen) auf `feature/wenzelsbibel-ingest`, `assets/{css,js,images}` konsolidiert, Playwright 2→36 grün / 25 skipped (#43). #42 Persistent Lemma Pages: Wörterbuchnetz-IDs schon deckungsgleich (`lid=879` = `lemma_879`), Clean URLs `/lemma/879` + 404.html-Redirect-Trick für GitHub Pages. Savepoints `4562c08`, `6849758`, `e16306d`, `5154d04`.

**2026-02 (Triage + Provenienz):** #44-Triage (23 Issues, 11 Labels; 13/23 Daten/TEI). #21 „Konzepte"→„Begriffe", #46 Lemma-Suche in Multi-Lemma gemerged, #45-API Hybrid-File-Strategie beschlossen, #36-40 Provenienz-Modell ADR-012 (flaches `<listBibl>` + `<bibl type="digitalIntermediary">`). #49-Konvention: Health-Check-Reports als Issue-Comments, keine `.md`.

**2026-04 (#32 TEI Model Consolidation – die große Migration):** 0/100 Files gegen tei_all.rng valide (nur `@meaningRef`+`@wordRef` non-standard; `@lemmaRef` IST Standard). 15M+ Transformationen über 675 Files: `@meaningRef`→`@ana` (5.9M), `@wordRef`→`@corresp` (7.5M), `seg`→`pc` (1.4M), `l`→`lb` in 18 Prosa-Files. Merge PR #69 (Korpus) + #71 (Authority); Deep-Schema-Audit fixte 11 Gaps – Root Cause: `div` ist RNC-Keyword → `tei.div` (brach RNC→RNG). 666/666 valid; Performance-Fix `tree.xpath()` O(n²) → `iter()` Clark-Notation; Branch-Protection auf `main`. WZB-Pipeline (#34/#66): Phase 1b Lemma 91,6 %, Phase 2 POS 95,5 % (Tagset ART→DET, CNJ→CCNJ/SCNJ/ADV), Phase 3 Paratext.

**2026-04-14–16 (Schema-Hardening + Frontend-Sprint):** #83 Editor-Attribution (`contributors.xml`, 51 Personen + 2 Orgs); #32-followup 16/17 + Konvention „Daten vor Schema". **PL1-Validierungs-Pathologie war ein `<p>` mit 404k Direktkindern, nicht die Größe**; nested `<hi>` über 143 Files geflattet; Validierung 830s→493s. **Mishap `8b5d0e6ac`: `git add -A` zog Kollegen-Files mit → CLAUDE.md-Git-Regel + Memory.** Frontend: #31 LINECODE.md, #56 Similar Lemmata, #48 Hash-Router, #17 Reader View (43k unstyled Compound-`@rend` gefixt, 128/128).

**2026-05-07/08 (#32-followup fertig + ARITHMETIC + PD-001):** #32-followup 17/17. #68-Guide-Architektur (user-facing HTML deutsch ≠ LLM-Docs englisch). WZB-Reorg → `scripts/ingest/wzb/`. **PD-001 „Mittelweg" (KZW+Christian): TEI-P5-Standardelemente + 24 `<div>/@type` optional ins Hauptschema; ADR-013-Ausnahme nested `<hi>` wieder erlaubt; `ingest/<sigle>/`-Konvention.** WZB live in beiden Indexen; **#94 Authority-Cache-Bug gefixt (selbstreferenzieller Versionsvergleich).**

**2026-05-11 (sechs Parallel-Sessions):** Playground Release 1 (#87-90 Wortfrequenz/Text-Statistiken/Lemma-Verteilung), #20 Lesbarkeit, #96 Reader-Download, #26 pb-Insertion (1293 `<pb>` über 14 Files, `795670240`), #78 `hilfe-schema.html` + Prism gevendort, #79 closed (5 Hilfe-Seiten), #47.1/.2 + #86-Barrierefreiheit-Draft, KZW-Loop #102/#103/#85. **`docs/data/linecode-templates.csv` (665 Templates) als kanonische Quelle – Lehre: Templates nie aus Daten ableiten.** JOURNAL 937→458 komprimiert.

**2026-05-12 (Julia + Playground-Wave):** #73 Lemma-Linking MWB+Lexer via Wörterbuchnetz-API (`dcbee3479`; Julias statischer Link war POST-only/defekt), #101 Reading-View-Render-Policy (Julia), #105 Authority-Counter 7→8, **#47.3 Versposition-Suche – Corpus-Index v4.0.1→v4.1.0 mit `lineStarts[]`/`lineEnds[]` (1,36M `<l>`)**, #47 R2 Begriffs-Verteilung, #47-Umbrella closed (#107/#108/#109 ausgelagert). Index-Versions-Drift strukturell gelöst (`check-index-versions.py` + CI + Memory, drei Stellen). #23 Stanza-Bulk (93 Texte, 11.090 `<lg>`, v4.1.1). Concept-Distribution-Perf-Patch 2747ms→60-200ms (MessageChannel-Chunking, nicht `setTimeout(0)`).

**2026-05-14/15/16 (Playground-Abschluss + Audits):** #112/#108/#107/#113 live (Verse-Click-Highlight, Textvergleich, Kookkurrenz-Ranking, Autocomplete), #110 WVV-Stanza, #104 Sigle-Gruppierung (Empfehlung: Titel statt Merge), #81 closed. **Lehre `Closes`-Trailer nur bei vollständig fertig** (#110-Reopen). Audit-driven Preparation als Pattern; Autocomplete-Helper zentralisiert.

**2026-05-28 (Großtag):** #113-Followup (`concepts.xml` Alternative-Terms vom Primär getrennt, Last-Wins-Bug; Authority-Index v1.3.0, `f7c8592c2`), #114 Tabellenansicht (Spec+Plan → Subagent-driven 11 Tasks/13 Commits), **CI `index-version-check` Timeout 2→10 min (war seit 05-12 still disabled)**, `.md`-Vereinheitlichung (9 Renames + 226 Cross-Refs), Single-Source Index-Versionen (TEI-MODEL §11). **Authority-Cross-Ref-Audit: 226.863 unresolved Refs (225.886 auf variants.xml) → #115; pb-Backlog 606 Texte → #116.**

**2026-05-29 (Authority-Drift Root Cause):** Repo ist alleiniger Master (transformation→active). Cross-Ref unresolved 226.863→977. **`variants.xml` ist korpus-abgeleitet und war stale (64.287 Formen fehlten); neuer Generator `extract-variants.py` → 192.472→256.759 Formen, Authority-Index v1.3.0→v1.4.0.** Negative type-IDs = Interpunktion, totes `@corresp` gedroppt (14.895 über 296 Files). Cross-Ref-Audit als CI-Gate, Data-Change-Lifecycle in Docs. Savepoints `0867a370f`, `e21d84bd6`.

**2026-06-01/02/03 (Site-Chrome + Paritätstests):** Site-Chrome-Refactor gemerged (`2e8d48d95`) – build-injizierte Nav/Footer (`includes/` + `build-pages.py`), #8 Mobile-Menü zentralisiert, `clearSiteData` delete-by-name. #130 Lemma-Match zentralisiert (`lemma-match.js`, §B.1 token-exakt), #131 Position-Counting-Paritätstest (§B; Leer-`<w>` JS→Python angeglichen, `7491e97b3`). Zwei Health-Checks; Doc-Schuld-Lehre (Build-Pipeline-Erweiterungen gehören in DEVELOPMENT+ARCHITECTURE).

**2026-06-05/09 (Health-Check + Re-Triage):** Multi-Agent-Check (103 Agenten): Doku hing Playground-Wachstum hinterher, ~24 Drifts gefixt, fabrizierte Worked-Examples korrigiert; **8 Blind-Spots, 1 blocking → #132 (Ingest-Verfahren in Stable-Doc), #133.** #44-Re-Triage (37 Issues): kein Bewertungs-, sondern Umsetzungs-Rückstand; #30/#34/#73 closed, #138/#139 angelegt. #53/#137/#135 geshippt.

**2026-06-10/11/12 (Zenodo + #59 + #117 + #125 + #138):** #91 Zenodo-DOI live (Concept `10.5281/zenodo.20627656`, v1.0.0 `…657`); Git-Tag als SSoT für Version (`41a71188a`). #59 Naming-Explorer (`naming-index.json.gz`, 10.506 Records) + ROL/TRO-Deep-Links, #117 Wörterbuch A–Z, #132 Ingest-Verfahren nach DATA-MODEL, #129 KWIC, #128/#23 closed. **#125 deterministische Index-Builds + CI-Freshness-Gate** (`data-integrity.yml`, byte-identische Rebuilds, `requirements.txt`-Pins; Corpus v4.1.4 / Authority v1.4.1, Merge `789708322`). #138 div-/lg-Wrapper (HUG/MBS), #121 Dropdown-Disambig, #136 Text-Statistiken-Auswahl.

**2026-06-17 (vier Sessions + Scorecard):** #45 Statische JSON-API gemerged (PR #150); tei_all.rng ins Repo committet statt CI-Download von tei-c.org (Ausfall-Blocker), xml-model-PIs repo-weit aufs lokale Schema (`559fd3163`). #44-Matrix-Drift korrigiert (7 geschlossene standen als aktiv); #138 HUG-Strophen geshippt (`9c9b78e83`, 814 `<lg>`, Index byte-identisch); dabei #151 entdeckt: TEI-Reader-Cache mit 30-Tage-TTL ohne Inhalts-Invalidierung. README-Drift-Audit 65 Findings (`e7f6d58f6`); **POS-TAGSET.md als SSoT herausgezogen** (`7e8ae95a2`, INDEX-Count 14→15). 47-Agent-Health-Check: 0 blocking, Algorithmus-/XPath-Checks konform, ~24 Count-Drifts gefixt (`54e6d64d0`) → Action-Item #152. **#124 cookieloses Matomo deployed** (`7abbf7672`): build-injizierte MATOMO-Region (`includes/_matomo.html`) + localStorage-Opt-out, weil das Uni-Opt-out-iframe extern HTTP 403 liefert.

**2026-07-02 (Fünf-PR-Welle):** #151 gefixt: Conditional-GET-Revalidierung (ETag/304) statt Deploy-Invalidierung (`4e0208f`); #143 `l`→`lb` für APO/HMT/HH (3.049) + HH-Genre-Fix + APO-Gattung nach Terrahe (Corpus v4.1.5, Authority v1.4.3); **pako/dexie vendored** (`ce34c81`, null Runtime-CDN-Abhängigkeiten). #106 Reim-Wörterbuch (10. Werkzeug, `lineEnds[]`-Scan, Suffix-Heuristik) + #114-Followups (Gesamtzeile, Types + MWB/Lexer-Links, Keyness-Log-Likelihood; Referenzkorpus = alle 667 Texte, auswahlunabhängig); Review härtete `escapeHtml` (Quote-Breakout) und zentralisierte den Wörterbuchnetz-Client (`assets/js/lib/woerterbuchnetz.js`). #152/#154 Daten-Drift-Gates in data-integrity.yml: lexicon-ID-Set-Ratsche (`lexicon-baseline.json`, nach Review statt Zahlenpaar), naming-Gates inkl. TOCTOU-Fix (Fetch unter resolviertem SHA), Versions-Bump-Gate. **#115 Kategorie-A-Backfill: 125 Stubs, 43.754→43.879 Lemmata** (dangling 977→396, 349→109 IDs), Authority v1.4.4. Lehren: Roundtrip-Skripte brauchen `newline=''` (CRLF hätte die 31-MB-lexicon.xml still umgeschrieben); doc-count-audit-50er-Kappung entfernt (war für Bulk-Sprünge blind).

**2026-07-08/09 (autonome Doppel-Session + Health-Check):** Issue-Session: 12 PRs #174–#185 (u. a. posAll[] v1.6.0 für 10.171 Multi-POS-Lemmata, AK-Excerpt-Banner via `biblScope unit="verse"`, drei latente §B-Paritäts-Drifts geschlossen) mit neuem Review-Triage-Pattern (Bot-Findings erst prüfen, dann fixen; 2 False Positives). Merge-Session: alle 13 PRs auf main, 13 Issues geschlossen, Live-Smoke grün. **GitHub-Mechanik-Lehren (je 2× reproduziert):** `gh pr merge --delete-branch` schließt gestackte PRs statt sie zu retargeten (Recovery: Head-SHA re-pushen → reopen → Base edit); `gh run rerun` nach Base-Retarget recycelt stale Event-Payload → Close/Reopen triggert frisch; GitHub schließt Issues auch über Development-Verknüpfung ohne Closes-Trailer (#171/#28 reopened). Health-Check 09.07.: Kernbestand drift-frei, 5 Rand-Drifts gefixt.

**2026-07-10 (Vormittag):** Reading-Nav-Kontrast-Fix nach KZW-Feedback (`6df766522`): `.reading-nav`-Komponenten in korpus.css statt Tailwind-Utilities, weil das vorkompilierte tailwind-output.css neue Klassen still verschluckt; Commit über temporäres Worktree (geteiltes Working-Dir). KZW-Rückstau-Session (5 Commits, 205/205): #110/WVV komplett (489 `<lg>` fortlaufend), #28 reopened mit 26 KWIC-Grenzfällen, #203 KWIC-CSV-Export, #204 Filter-vs-Auswahl-UX (noResults-Box konnte seit jeher nie erscheinen), #187 posAll-Anzeige-Migration. **Direktive chsteiner: Frontend vor Ingest** (CoReMA #139 später als gemeinsame Session); juliahin wieder regulär im Projekt; brevitas-Wiki ohne Lizenz = Blocker für #147.

> Full older entries preserved in journal-archive.md

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
