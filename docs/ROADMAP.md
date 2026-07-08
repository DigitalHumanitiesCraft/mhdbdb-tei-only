# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Updated 2026-07-08.

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: PR-Review der autonomen Issue-Session (07.–08.07.)

**12 offene PRs #174–#185**; Review + Merge durch chsteiner schließt 13 Issues automatisch (#163 #164 #159 #168 #158 #162 #160 #161 #134 #145 #27 #167 #170). Merge-Reihenfolge der zwei Stack-Ketten beachten:

- **Kette A:** #174 → #175 → #178 → #184 (Lemma-Auflösung/Races → lb-Nummern → AK-Excerpt → Paritäts-Drifts)
- **Kette B:** #174 → #177 → #183 (→ posAll Multi-POS → Frontend-Kleinbugs)
- **Unabhängig:** #176 (Spaltenmodell), #179 (Hilfe/Barrierefreiheit), #180 (Rektoratsbericht), #181 (POS-Policy), #182 (Fremdsprachen-Phasenplan), #185 (Python-Ingest-Fixes)

Alle PRs tragen einen „Review-Triage"-Abschnitt (Bot-Review-Findings triagiert, Berechtigtes als Folge-Commits gefixt). Daneben bleibt **#124 (prio-1)** aktiv: Uni-Matomo entschieden, wartet auf Bärthlein-Snippet + Datenschutz-Eckdaten.

## Next: Menschen-Pings (nach den Merges)

| # | What | Who's needed |
|---|------|-------------|
| #110 | WVV-Strophen — Entscheidungsvorlage liegt im Issue (Korpus-Survey + Empfehlung b); Skript-Blocker F35/F36 in PR #185 gefixt | KZW (Entscheid) |
| #115 | Cross-Ref Phase 2 — 196 Lemmata kuratorisch (A 125 / B 36 / C 35) | KZW |
| #129, #138 | KWIC-Belege + div-/lg-Hüllen: gebaut und live, warten auf Prüfung | KZW |
| #59, #114 | Naming-Fachklärung + Tabellenansicht-Freigabe | Linda |
| #92 | ARITHMETIC — Metadatenfragen seit 16.05.; Escaping-Blocker in PR #185 gefixt, Stage 1 danach in ~1–2h | Carina (via KZW) |
| #147 | Weingrüße — Lizenz/Sigle/Genre/Zuschreibungen, Stage 0 | Silvan (via KZW) |
| #86 | Barrierefreiheit — Ansprechpersonen-Block in PR #179; schließen nach Text-Freigabe | Alan van Beek |

## Needs Clarification / Entscheidungs-Cluster (chsteiner)

| # | What | Key question |
|---|------|-------------|
| #140 | Doku menschenlesbar | Doku-Strategie-Gespräch (TEI-MODEL-Rolle, LLM-Artefakte) |
| #58 | Begriff→Lemma→Beleg Workflow | Option A/B/C entscheiden |
| #169 | Suchsemantik (Audit 3/6) | Nähesuche-Distanz, commonLemmas, Dedup — deterministische Teile bereits in PR #174 |
| #172 | Test-Suite-Policy (Audit 6/6) | 45%-passRate-Floor + korpusabhängige Magic-Numbers |
| #18 | Multi-Lemma + PoS-Suche | Nach Merge von PR #181 (POS-Policy) spezifizierbar; braucht POS-Daten im Corpus-Index |

## Future: Needs Design / Trigger-Wait

| # | What | Key question |
|---|------|-------------|
| #141 | Borte-Ingest — Aufgabe 0 (borte.md-Metadaten-Template) im Issue geliefert | KZW-Priorisierung (nach #139) |
| #106 | Vers-Boundary-Features — Minimalvariante shipped 02.07., Rolling-Backlog | Original-Token/Phonetik → #109 |
| #139 | CoReMA-Korpus ingesten | Trigger/Kapazität |
| #118 | Sprachstufen aus Normdaten | Policy + Architekturentscheid |
| #123 | „König vom Odenwald" | Scope + Zeitfenster (KZW) |
| #63 | Begriffssystem Update | Scope/Policy (KZW) |
| #93 | Textreihentypologie-Umzug (von marketext.at auf MHDBDB-Unterseite) — SKOS-Daten aus `textseries`-Repo, Baum-Visualisierung; dysfunktionale `dhplus`-URIs zu bereinigen | Visualisierung + Authority-File-Abgleich |
| #109 | FWF-Einzelprojekt (Korpus-Tiefenanalyse, NER-Pipeline, phonetische Reimanalyse, Visualisierungen) — Antrag durch KZW, kleines Budget, max. 50% externe Mittel | Scope-Notiz für Antragstext |
| #111 | Index-Größen-Soft-Cap und modulare Splitting-Strategie | Trigger >50 MB gz (heute ~40); Optionen A modular / B brotli / C binär; keine Entscheidung bis Schwellwert erreicht |

## Recently Completed

| # | What |
|---|------|
| ~~#106~~ | Reim-Wörterbuch Minimalvariante (2026-07-02): Zehntes TEI-Analyse-Werkzeug `#rhyme-dictionary` — Reimpartner-Lemmata an benachbarten Versenden (`lineEnds[]`-Scan, Suffix-3-Heuristik auf normalisierten Formen, 2-Letter bei Kurzwörtern), optionaler Text/Autor-Filter, „→ Belege"-Link in Multi-Lemma-Nähe-Suche. Kein neuer Build-Schritt. Punkte 2-7 bleiben in #109 (FWF), Punkt 8 im Multi-Lemma-Backlog. |
| ~~#114-Followups~~ | Integrationswünsche Tabellenansicht (2026-07-02): Gesamtzeile mit Gesamttrefferzahl (sticky tfoot + „M Treffer gesamt" im Header), Types/Schreibformen + MWB/Lexer-Links im Lemma-Panel (Wörterbuchnetz-API), Keyness-Spalte (signierte Log-Likelihood Text vs. Gesamtkorpus, fett ab 10,83) inkl. Export-Spalte. |
| ~~#45~~ | Static JSON API (2026-06-12): FAIR-orientierte JSON-API unter `/api/` (2.742 Dateien, ~14 MB), deterministischer Build (`scripts/build-api.py`) + CI-Freshness-Gate, Doku-Seite `api/index.html`; PR #150 gemerged (Closes #45). |
| ~~#113-Followup~~ | KZW-Synonym-Match in Begriffs-Verteilung + Begriffe-Explorer (2026-05-28, commit `f7c8592c2`): Last-Wins-Bug in `parse_concepts()` gefixt (Primär-Term wurde von Alternative überschrieben, z.B. concept_13023100 zeigte „Früchte" statt „Obst"). Authority-Index v1.2.2 → v1.3.0 mit additiven Feldern `altDE[]`/`altEN[]`/`altNormalized[]` (263/567 Concepts mit deutschem Synonym). Beide UI-Module matchen Synonyme zusätzlich und zeigen „auch: …"-Hint im Autocomplete. Chrome-verifiziert mit „obs"/„frü"/„Wahnsinn-Tobsucht". |
| ~~#113~~ | Autocomplete im Begriffs-Verteilung-Input (2026-05-15, commit `a2e7b0b36`): klassisches Dropdown unter dem Input mit max. 8 Concept-Suggestions, Pfeil-Navigation (ArrowDown/Up), Enter wählt + sucht, Escape schließt, Klick (mousedown vor blur) wählt + sucht. Reuse `resolveQuery()` als Suggestions-Quelle. ARIA: combobox/listbox/aria-selected/aria-expanded. Live-verifiziert: „ster" → Sterben + Bruderschaft. |
| ~~#107~~ | Kookkurrenz-Ranking (2026-05-15, commit `70d0bf280`): DWDS-Style „Welche Lemmata stehen am häufigsten bei X?". Window-Scan über `text.words[pos±w]` für jede Position in `text.lemmata[X]`. POS-Filter (Inhaltswörter / NOM / VRB / ADJ / alle) essentiell weil ohne Filter Stopwords dominieren. `êre` (9.930 Vorkommen, 6.361 Partner): 1.002ms inkl. UI-Render dank MessageChannel-Yield-Chunking. POS-Filter-Switch ohne Re-Compute: ~15ms (rawCounts gecacht). Belege-Klick → Multi-Lemma-Suche mit beiden Lemmata vorbefüllt. |
| ~~#108~~ | Textvergleich (2026-05-15, commit `c53a8ac0d`): Zwei Texte auswählen → drei Lemma-Mengen (Nur A / Beide / Nur B) mit Frequenz pro Text und absoluter Differenz. Reine Set-Ops auf `Object.keys(text.lemmata)`, keine neuen Index-Felder. Lokale `_lemmaMap` (einmal pro `show()` gebaut) reduziert 6s Click-Latenz auf 53ms (112× schneller) — `AuthorityFilesManager.findLemmaById()` ist O(N) linear. Verifiziert PZ vs JT: „triuwe" 447× nur in JT (Lemmatisierungs-Unterschied Wolfram/Albrecht). |
| ~~#112~~ | Versposition-Klick-Highlight-Bug (2026-05-15, commit `131fed17b`): `verse-position-search.js` + `lemma-distribution.js` bauten Reader-URLs mit `lemmaIds=5567` (cleanId), Highlighter sucht jedoch `#${id}` in `lemmaRef="lexicon.xml#lemma_5567"` — `#5567` matcht nicht. Fix: URL-Param erhält volle Form `lemma_5567`. Live-verifiziert (76 + 140 URLs jeweils mit korrektem Prefix; 4 Highlights für `lemma_5567` in AXW). |
| ~~#104~~ | Sigle-Titel-Differenzierung (2026-05-15, commit `c0b546a45`): PL1-3, FLG/FLG1, FR1-3 bekommen sprechende Anzeigetitel mit Edition + Datum. FLG-`<biblStruct>` umgestellt auf Neumann/Vollmann-Profe 1990 (Edition) + Harsch 2009 (digitalIntermediary). Index-Bump corpus 4.1.2 / authority 1.2.2. KZW-Wording wortgleich; 130/131 Tests grün, Chrome-UI verifiziert |
| ~~#81~~ | Sprachstufen-Differenzierung (closed 2026-05-15): SAL/SAT/BAR/TUN waren Wikidata-Fehler (`gmh` bleibt). AC1-3 (Ackermann aus Böhmen) bleiben ebenfalls `gmh` — KZW-Entscheidung 2026-05-08: solange kein ISO-Code für Frühneuhochdeutsch existiert, ist `gmh` die TEI-konformste Lösung. 537 unerforschte Texte als eigener Task ausgelagert (nicht angelegt — nicht in Plan) |
| ~~#47~~ | TEI Textanalyse Umbrella geschlossen (2026-05-12): R1 (#87-90) und R2-Hauptpunkt Begriffs-Verteilung shipped; Folgepunkte ausgelagert in #107 (Kookkurrenz-Ranking), #108 (Textvergleich), #106 (Vers-Boundary-Features, Punkt 1 als Rolling-Backlog), #109 (FWF-Projekt für NER + tiefere Analysen) |
| ~~#47 R2~~ | Begriffs-Verteilung (2026-05-12): Neuer Playground-Eintrag analog Lemma-Verteilung (#90), aber concept-basiert. Datenpfad concept → senses → lemmata → texts. Verifiziert mit „Sterben" (682 Lemmata, 659 Texte, 103.657 Vorkommen) und „love" (Intimität mit Candidates) |
| ~~#47.3~~ | Lemmasuche nach Versposition (2026-05-12): Neuer Playground-Eintrag unter Multi-Lemma-Suche, findet Lemmata am Versanfang/Versende. Corpus-Index v4.1.0 mit `lineStarts[]`/`lineEnds[]` (1,359,789 `<l>` über 603 Versdichtungs-Texte, +6 MB gz). KZW-Wording wortgleich; Chrome-verifiziert (Reimpaare gân/begân, bant/bekant am Versende von AGS) |
| ~~#105~~ | Authority-Files-Counter (2026-05-12): Stats-Block auf Startseite von 7 → 8 angeglichen; Playground-Loader-Status bleibt bei 7 (technisch korrekt, `contributors.xml` nicht im authority-index) |
| #73 (shipped, Issue offen) | Lemma-Linking MWB + Lexer (2026-05-12): MWB-Block über Wörterbuchnetz-API (`/dictionaries/MWB/lemmata/{form}`) statt POST-only-Suchformular; Dictionary-Loop für beide Wörterbücher, Section nur sichtbar wenn min. 1 Treffer. Julias initialer Suchlink (`05c8676a4`) war defekt. **Issue bleibt OPEN** (needs-clarification: MWB-API noch unvollständig, KZW-Rückfrage bei Recker-Hamm offen) |
| ~~#101~~ | Reading-View-Render-Policy (2026-05-12, Julia): `milestone[@unit="verse"]` → `<span class="verse-marker">` (superscript), `div[@type="chapter"]` → `<h3 class="section-head">`, `.hi-initial` Sonderformatierung entfernt; Marginalia/Glossen/Rubrum bleiben unstylisiert |
| ~~#85~~ | Umbrella div-Wrapper (closed 2026-05-12): Kat. 2 (7 Lieder) bereits in `ef939f530`; Kat. 3 (DJEM `e7b99b990`, DES2 `f51a74468`, DUB `d92e398ec`); 13 MBS-Serie-Texte aus Kat. 1 strukturell als implizit-OK eingestuft |
| ~~WZB Pentateuch~~ | (2026-05-12, Julia): WZB-Titel + works.xml + projectDesc auf „Wenzelsbibel (Pentateuch: Gen–Dtn, Cod. 2759–2764)" präzisiert; Authority-Index-Rebuild |
| ~~Blog-Post WZB-Pipeline~~ | (2026-05-12, Julia + C. Pollin): Draft v3 in `publications/BLOG-POST-WZB-PIPELINE.md` (30J. MHDBDB-Kontext, LOD, dreiphasige LLM-Pipeline, böhmische Schreibkonventionen); unpublished |
| ~~#20~~ | Readability fixes (2026-05-11): Counter „667/667 Texte ausgewählt" auf text-2xl/font-semibold, dedizierte blue-50-Hinweisbox mit Info-Icon zum Deselect-Workflow |
| ~~#96~~ | Metadatenanzeige (2026-05-11): TEI-XML-Download-Link am Ende des Reader-Metadaten-Panels, Anonym-Wikidata-Link bei `authorId === 'person_anonym'` unterdrückt |
| ~~#87~~ | Playground TEI Textanalyse UX-Cleanup (2026-05-11): 3 broken Buttons raus, Reorder |
| ~~#88~~ | Playground Wortfrequenz-Analyse (2026-05-11): Top-N Lemmata mit Frequenz-Bars |
| ~~#89~~ | Playground Text-Statistiken (2026-05-11): Token-Anzahl, Lemma-Diversität, Hapax-Rate |
| ~~#90~~ | Playground Lemma-Verteilung (2026-05-11): Bar-Chart Lemma × Text |
| ~~#100~~ | Pre-flight Working-Tree-Check für Index-Builder (2026-05-11): `git status --porcelain`-Check verhindert dirty Builds |
| ~~#97-99~~ | Playground Follow-up-Cleanups (2026-05-11): Corpus-Index-Property-Drift gefixt, ~700 Zeilen Dead Code aus tei-ui.js entfernt |
| ~~#79~~ | /hilfe/ User-facing Help Pages (2026-05-08): 5 Hilfe-Seiten live (Korpussuche, Playground, Daten, Daten beitragen, Index) |
| ~~#94~~ | Authority-Cache invalidiert nicht bei Versions-Bump (2026-05-08): selbstreferenzieller Vergleich gefixt |
| ~~#17~~ | Reader View TEI-Strukturelemente (2026-04-16): Token-basierte `<hi rend>` Klassen (43k Compound-Werte gefixt), `<div>/<lg>/<l>/<lb>` Margin-Numbers, Note-Badges für `@type="year\|date"`, 128/128 Tests grün |
| ~~#52~~ | Authority Files Card (2026-04-16): collapse-by-default, weniger visuelle Dominanz im Playground-Sidebar |
| ~~#32-followup~~ | vollständig 17/17 (2026-05-07): P1-5 `idno/@type` 3 kontextspezifische Enum-Patterns (`msIdentifier` / `monogr` / `person`), WZB-shelfmark-Fix (Daten vor Schema), Stage-1 PI-Cleanup auf 667 Files, CI Push-Trigger |
| ~~#68 Teil 1~~ | `hilfe-daten-beitragen.html` (2026-05-07): user-facing Schema-Konversions-Leitfaden für TEI-Beitragende |
| ~~WZB-Reorg~~ | (2026-05-07): 20 Pipeline-Skripte in `scripts/ingest/wzb/`, 4 Sackgassen in `scripts/_archived/wzb/` |
| ~~#62~~ | Impressum (2026-04-16): `impressum.html` mit Datenschutz, Footer-Links auf allen Seiten |
| ~~#48~~ | Playground URL-Routing (2026-04-15): Hash-basierte shareable URLs für alle Playground-Views |
| ~~#56~~ | Lemmata-Explorer (2026-04-15): Titel-Links zu Lemma-Seiten, URL-Bug-Fix, concept-based Similar Lemmata |
| ~~#31~~ | Linecode2TEI-Dokumentation (2026-04-15): `docs/LINECODE.md` |
| ~~#22~~ | TEI Encoding Guidelines (2026-04-16): superseded by TEI-MODEL.md + schema README |
| ~~#43~~ | Playwright test coverage (2026-04-16): 121/121 passing, 25 skipped intentional |
| ~~#83~~ | Editor-Attribution & Credits-Modell (2026-04-15) |
| ~~#84~~ | HZU/HZU2 Datum-Notes — already migrated in #32 Phase A |
| ~~#32-followup~~ | Schema hardening: 16/17 items done (P1-5 `idno/@type` enum remains) |
| ~~#32~~ | TEI Model Consolidation (675→666 files, 15M+ transformations, 2 schemas) |
| ~~#29~~ | Stricker-Texte |
| ~~#60~~ | Parzival Struktur-Bug |
| ~~#61~~ | Textauswahl Whitespace-Bug |
| ~~#53~~ | Korpus durchsuchen UX |
| ~~#67~~ | Abbreviaturen Header (124 Texte) |
| ~~#70~~ | pc join spacing |
| ~~#14~~ | Sonderfall Lizenzen |
| ~~#50~~ | Fix 43 test failures → 121/121 passing |
| ~~#42~~ | Persistent lemma pages |
| ~~#46~~ | Merge Lemma-Suche |
| ~~#21~~ | Rename Konzepte→Begriffe |
| ~~#35–40~~ | Provenance metadata (5 batches) |

## Strategic Direction

1. **TEI model consolidation done** — Soll-Modell (#32) fully implemented, #32-followup 17/17 abgeschlossen (P1-5 mit 3 kontextspezifischen Enum-Patterns für `idno/@type`, plus WZB shelfmark, Stage-1 PI cleanup, CI push trigger). Both schemas written (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), all 667 corpus + 8 authority files validated. Target models: [TEI-MODEL.md](TEI-MODEL.md) + [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md). Architecture Decision Record: [ADR-013 "Data Consolidation Before Schema Relaxation"](DECISIONS.md#adr-013-data-consolidation-before-schema-relaxation).

2. **TEI data quality** — Structural fixes (#23, #26, #30, #85), schema hardening (#32 ✅), Wenzelsbibel (#34, Phase 3 at 92.5%) und WVV-Followup (#110) sind die aktiven Workstreams. Die meisten verbleibenden Structural Fixes sind auf KZW-Review geblockt.

3. **Playground TEI Textanalyse Release 1 done** — UX-Cleanup (#87), Wortfrequenz (#88), Text-Statistiken (#89), Lemma-Verteilung (#90) alle 2026-05-11 closed. Release 2 (Begriffs-Verteilung) und Release 3 (POS-Anteile, abhängig von #27) noch ungeplant.

4. **FAIR data + Citability** — Static JSON API (#45) und Zenodo-DOI (#91, Stub geliefert) machen MHDBDB-Daten extern zitier- und programmierbar zugänglich. Enables external collaborations (MWB, Wörterbuchnetz, ZfdG-Einreichung).

5. **Frontend refinements** — Reader (#17 ✅), UI-Polish (#20 ✅), Reading-View-Render-Policy (#101 ✅ 2026-05-12, Julia) und Lemma-Linking MWB+Lexer (#73 ✅ 2026-05-12) abgeschlossen. Upload-UI-Dead-Code-Cleanup pendent (kein Issue).

6. **Advanced search** — PoS-based search (#18) and foreign language search (#28) depend on corpus index extensions.
