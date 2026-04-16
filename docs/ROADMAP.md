# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Updated 2026-04-16.

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: Quick Wins + prio-1

| # | What | Domain | Effort |
|---|------|--------|--------|
| #17 | Reader View: TEI structural elements — **prio-1**, in progress | frontend | L |
| #87 | Playground TEI Textanalyse: UX-Cleanup (broken buttons + reorder) | frontend | S |
| #20 | Readability fixes (font sizes, contrast) — done, awaiting approval | frontend | S |
| #52 | Playground "Authority Files" card clickable — implemented, awaiting Katharina review | minor-UX/UI | S |

## Next: Playground TEI Textanalyse + FAIR Data

| # | What | Domain | Effort |
|---|------|--------|--------|
| #88 | Playground TEI Textanalyse: Wortfrequenz-Analyse | frontend | S |
| #89 | Playground TEI Textanalyse: Text-Statistiken | frontend | S |
| #90 | Playground TEI Textanalyse: Lemma-Verteilung | frontend | S |
| #45 | Static JSON API (FAIR data) — [planning doc](features/045-static-api.md) ready | pipeline + frontend | L |
| #79 | /hilfe/ — user-facing help page (part of #80 umbrella) | documentation | L |
| #78 | Frontend-Dokumentation: MHDBDB-Schema & Daten-Tutorial | documentation | M |
| #86 | Barrierefreiheitserklärung (WZG) — needs Uni Salzburg input | documentation | M |

## Blocked: Needs Human Input

| # | What | Who's needed |
|---|------|-------------|
| #30 | TEI structural fixes — auto-fixes ready, draft-fixes prepared | KZW (review) |
| #26 | Missing `<pb>` elements (17 texts) | KZW manual check |
| #85 | Fehlende `<div>`-Wrapper (26 Texte, 4 Kategorien) | KZW + Julia |
| #81 | Sprachstufen-Differenzierung: pauschales `gmh` stimmt nicht | KZW |
| #34 | Ingest Wenzelsbibel + CoReMA — WZB branch (`feature/wenzelsbibel-ingest`) needs rebase | Julia + Helmut |
| #68 | Guide: How to add data to MHDBDB | KZW (depends on #34 lessons learned) |

## Needs Clarification

| # | What | Key question |
|---|------|-------------|
| #47 | TEI Textanalyse im Playground (umbrella) | Release 1 sub-issues created (#87-90). Further features (#47 Release 2+3) need scoping |
| #27 | POS Workflow expansion | Linguistic decisions answered — implementation scope? |
| #28 | Foreign language search | Index needs `xml:lang`; UI design needed |
| #18 | Multi-lemma + PoS tag search | Depends on POS corpus migration (#27) |
| #73 | Lemma-Linking zu MWB/Wörterbuchnetz | MWB API HTTP-only (blocked by mixed content); linking strategy needed |
| #23 | Missing stanza markup (104 texts) | Complex cases need Linecode docs (#31, done) + Julia input |

## Future: Needs Design

| # | What | Key question |
|---|------|-------------|
| #58 | Begriff→Lemma→Beleg Workflow | Playground UX redesign |
| #59 | Antonomasien/Epitheta Modul | Standalone analysis module design |
| #63 | Begriffssystem Update | Julia's future plans |
| #80 | Umbrella: User-facing Dokumentation & Hilfe | Sub-issues #79, #78, #68 |

## Recently Completed

| # | What |
|---|------|
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

1. **TEI model consolidation done** — Soll-Modell (#32) fully implemented, #32-followup 16/17 items done (only P1-5 `idno/@type` context-specific enum remains). Both schemas written (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), all 666 corpus + 8 authority files validated. Target models: [TEI-MODEL.md](TEI-MODEL.md) + [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md). Architecture Decision Record: [ADR-013 "Data Consolidation Before Schema Relaxation"](DECISIONS.MD#adr-013).

2. **Playground TEI Textanalyse** — #47 umbrella broken into concrete sub-issues: UX-Cleanup (#87), Wortfrequenz (#88), Text-Statistiken (#89), Lemma-Verteilung (#90). All claude-ready, all use existing corpus index data.

3. **FAIR data** — Make all MHDBDB data citable and programmatically accessible (#45). Enables external collaborations (MWB, Wörterbuchnetz).

4. **TEI data quality** — Remaining structural fixes (#23, #26, #85). Mostly blocked on human review.

5. **Frontend refinements** — TEI rendering (#17, prio-1), UI polish (#20), and advanced playground features.

6. **Advanced search** — PoS-based search (#18) and foreign language search (#28) depend on corpus index extensions.
