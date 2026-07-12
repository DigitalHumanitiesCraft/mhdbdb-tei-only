# MHDBDB Development Journal

Chronological log of development decisions, dead ends, and savepoints. Not a changelog – captures the *reasoning* behind changes.

---

## Verdichtete Historie

Hochrangiger Trace der Einträge 2025-02 bis 2026-06-12. Volltext aller 52 verdichteten Einträge in `journal-archive.md`.

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

> Full older entries preserved in journal-archive.md

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