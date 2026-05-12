# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Updated 2026-05-12 (Abend).

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: Quick Wins + prio-1

| # | What | Domain | Effort |
|---|------|--------|--------|
| #91 | Zenodo-Integration — CITATION.cff von KZW finalisiert (`type=dataset`, Lead-Autorin); Zenodo-Webhook + Tag noch User-Steps | docs/release | S |
| #81 | Sprachstufen-Differenzierung — 4/7 Texte abgehakt (SAL/SAT/BAR/TUN no-op); AC1-3 pending KZW-Code-Wahl | data | S |

## Next: FAIR Data + Daten-Qualität

| # | What | Domain | Effort |
|---|------|--------|--------|
| #45 | Static JSON API (FAIR data) — [planning doc](features/045-static-api.md) ready | pipeline + frontend | L |
| #78 | Frontend-Dokumentation: MHDBDB-Schema & Daten-Tutorial | documentation | M |
| #86 | Barrierefreiheitserklärung (WZG) — needs Uni Salzburg input | documentation | M |
| #107 | Kookkurrenz-Ranking („Welche Lemmata stehen am häufigsten bei X?") — sofort umsetzbar, alle Daten im Index | frontend | M |
| #108 | Textvergleich (gemeinsame vs. exklusive Lemmata zweier Texte) — sofort umsetzbar | frontend | M |

## Blocked: Needs Human Input

| # | What | Who's needed |
|---|------|-------------|
| #92 | ARITHMETIC ingest — 6 fnhd. Rechenbuch-HS von Carina (Graz); wartet auf Carinas Antwort zu Sigle/Lizenz/Edition/Genre + Schlüsselfrage Domänen-Klassifikation erhalten? | Carina (via Katharina) |
| #30 | TEI structural fixes — auto-fixes ready, draft-fixes prepared | KZW (review) |
| #81 | Sprachstufen-Differenzierung: pauschales `gmh` stimmt nicht | KZW |
| #34 | Ingest Wenzelsbibel — Phase 3 at 92.5% @meaningRef, 4,013 rows pending; branch rebased 2026-05-06; evaluation script (`wzb-sense-evaluate.py`) ready | Julia + Helmut |
| #68 | Guide: How to add data to MHDBDB — Teil 1 (`hilfe-daten-beitragen.html`) shipped 2026-05-07, Contributing-Guide-Update 2026-05-12 (Two-Wege-Block + 9-Punkte-Checkliste); weitere Onboarding-Artefakte hängen an #34-Lessons | KZW |

## Needs Clarification

| # | What | Key question |
|---|------|-------------|
| #27 | POS Workflow expansion | Linguistic decisions answered — implementation scope? |
| #28 | Foreign language search | Index needs `xml:lang`; UI design needed |
| #18 | Multi-lemma + PoS tag search | Depends on POS corpus migration (#27) |
| #23 | Missing stanza markup (104 texts) | Complex cases need Linecode docs (#31, done) + Julia input |
| #104 | Siglen, die zu einem Werk zusammengehören (FLG/FLG1, PL1-3, FR1-3) — KZW-Issue 2026-05-11 | KZW + Julia |
| #106 | Vers-Boundary-Folgefeatures — Punkt 1 (Reim-Wörterbuch) bleibt Rolling-Backlog; Punkte 2-7 wandern in #109 FWF-Projekt; Punkt 8 in Multi-Lemma-Backlog | KZW priorisiert weiter |

## Future: Needs Design

| # | What | Key question |
|---|------|-------------|
| #58 | Begriff→Lemma→Beleg Workflow | Playground UX redesign |
| #59 | Antonomasien/Epitheta Modul | Standalone analysis module design |
| #63 | Begriffssystem Update | Julia's future plans |
| #80 | Umbrella: User-facing Dokumentation & Hilfe | Sub-issues #79, #78, #68 |
| #109 | FWF-Einzelprojekt (Korpus-Tiefenanalyse, NER-Pipeline, phonetische Reimanalyse, Visualisierungen) — Antrag durch KZW, kleines Budget, max. 50% externe Mittel | Scope-Notiz für Antragstext |
| #111 | Index-Größen-Soft-Cap und modulare Splitting-Strategie | Trigger >50 MB gz (heute 42); Optionen A modular / B brotli / C binär; keine Entscheidung bis Schwellwert erreicht |

## Recently Completed

| # | What |
|---|------|
| ~~#47~~ | TEI Textanalyse Umbrella geschlossen (2026-05-12): R1 (#87-90) und R2-Hauptpunkt Begriffs-Verteilung shipped; Folgepunkte ausgelagert in #107 (Kookkurrenz-Ranking), #108 (Textvergleich), #106 (Vers-Boundary-Features, Punkt 1 als Rolling-Backlog), #109 (FWF-Projekt für NER + tiefere Analysen) |
| ~~#47 R2~~ | Begriffs-Verteilung (2026-05-12): Neuer Playground-Eintrag analog Lemma-Verteilung (#90), aber concept-basiert. Datenpfad concept → senses → lemmata → texts. Verifiziert mit „Sterben" (682 Lemmata, 659 Texte, 103.657 Vorkommen) und „love" (Intimität mit Candidates) |
| ~~#47.3~~ | Lemmasuche nach Versposition (2026-05-12): Neuer Playground-Eintrag unter Multi-Lemma-Suche, findet Lemmata am Versanfang/Versende. Corpus-Index v4.1.0 mit `lineStarts[]`/`lineEnds[]` (1,359,789 `<l>` über 603 Versdichtungs-Texte, +6 MB gz). KZW-Wording wortgleich; Chrome-verifiziert (Reimpaare gân/begân, bant/bekant am Versende von AGS) |
| ~~#105~~ | Authority-Files-Counter (2026-05-12): Stats-Block auf Startseite von 7 → 8 angeglichen; Playground-Loader-Status bleibt bei 7 (technisch korrekt, `contributors.xml` nicht im authority-index) |
| ~~#73~~ | Lemma-Linking MWB + Lexer (2026-05-12): MWB-Block über Wörterbuchnetz-API (`/dictionaries/MWB/lemmata/{form}`) statt POST-only-Suchformular; Dictionary-Loop für beide Wörterbücher, Section nur sichtbar wenn min. 1 Treffer. Julias initialer Suchlink (`05c8676a4`) war defekt |
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

1. **TEI model consolidation done** — Soll-Modell (#32) fully implemented, #32-followup 17/17 abgeschlossen (P1-5 mit 3 kontextspezifischen Enum-Patterns für `idno/@type`, plus WZB shelfmark, Stage-1 PI cleanup, CI push trigger). Both schemas written (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), all 667 corpus + 8 authority files validated. Target models: [TEI-MODEL.md](TEI-MODEL.md) + [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md). Architecture Decision Record: [ADR-013 "Data Consolidation Before Schema Relaxation"](DECISIONS.MD#adr-013).

2. **TEI data quality** — Structural fixes (#26, #30, #85), schema hardening (#32 ✅), and Wenzelsbibel (#34, Phase 3 at 92.5%) are the active workstreams. Most structural fixes are blocked on KZW review.

2. **Playground TEI Textanalyse Release 1 done** — UX-Cleanup (#87), Wortfrequenz (#88), Text-Statistiken (#89), Lemma-Verteilung (#90) alle 2026-05-11 closed. Release 2 (Begriffs-Verteilung) und Release 3 (POS-Anteile, abhängig von #27) noch ungeplant.

3. **FAIR data + Citability** — Static JSON API (#45) und Zenodo-DOI (#91, Stub geliefert) machen MHDBDB-Daten extern zitier- und programmierbar zugänglich. Enables external collaborations (MWB, Wörterbuchnetz, ZfdG-Einreichung).

4. **TEI data quality** — Remaining structural fixes (#23, #26, #85). Mostly blocked on human review.

5. **Frontend refinements** — Reader (#17 ✅), UI-Polish (#20 ✅), Reading-View-Render-Policy (#101 ✅ 2026-05-12, Julia) und Lemma-Linking MWB+Lexer (#73 ✅ 2026-05-12) abgeschlossen. Upload-UI-Dead-Code-Cleanup pendent (kein Issue).

6. **Advanced search** — PoS-based search (#18) and foreign language search (#28) depend on corpus index extensions.
