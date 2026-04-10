# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Updated 2026-04-10.

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: Quick Wins + prio-1

| # | What | Domain | Effort |
|---|------|--------|--------|
| #17 | Reader View: TEI structural elements — **prio-1**, unblocked by #32 audit | frontend | L |
| #20 | Readability fixes (font sizes, contrast) — done, awaiting approval | frontend | S |
| #52 | Playground "Authority Files" card clickable | minor-UX/UI | S |
| #62 | Impressum | documentation | S |
| #31 | Doku: Linecode2TEI | documentation | S |

## Next: FAIR Data + Playground

| # | What | Domain | Effort |
|---|------|--------|--------|
| #48 | Playground URL routing (shareable views) | frontend | M |
| #45 | Static JSON API (FAIR data) — [planning doc](features/045-static-api.md) ready | pipeline + frontend | L |
| #56 | Lemmata-Explorer rename + semantic explorer | frontend | L |

## Blocked: Needs Human Input

| # | What | Who's needed |
|---|------|-------------|
| #30 | TEI structural fixes — auto-fixes ready, draft-fixes prepared | KZW (review) |
| #26 | Missing `<pb>` elements (17 texts) | KZW manual check |
| #34 | Ingest Wenzelsbibel + CoReMA — WZB branch deleted (content on main) | Julia + Helmut |
| #68 | Guide: How to add data to MHDBDB | KZW (depends on #34 lessons learned) |

## Needs Clarification

| # | What | Key question |
|---|------|-------------|
| #23 | Missing stanza markup (104 texts) | Complex cases need Linecode docs (#31) |
| #27 | POS Workflow expansion | Linguistic decisions answered — implementation scope? |
| #22 | TEI Encoding Guidelines | **Recommend close:** TEI-MODEL.md + schema README cover this |
| #28 | Foreign language search | Index needs `xml:lang`; UI design needed |
| #18 | Multi-lemma + PoS tag search | Depends on POS corpus migration (#27) |
| #47 | TEI Textanalyse Playground | Feature scoping needed (6 features proposed) |

## Future: Needs Design

| # | What | Key question |
|---|------|-------------|
| #58 | Begriff→Lemma→Beleg Workflow | Playground UX redesign |
| #59 | Antonomasien/Epitheta Modul | Standalone analysis module design |
| #63 | Begriffssystem Update | Julia's future plans |

## Recently Completed

| # | What |
|---|------|
| ~~#32~~ | TEI Model Consolidation (682 files, 15M+ transformations, 2 schemas) ✅ |
| ~~#29~~ | Stricker-Texte ✅ |
| ~~#60~~ | Parzival Struktur-Bug ✅ |
| ~~#61~~ | Textauswahl Whitespace-Bug ✅ |
| ~~#53~~ | Korpus durchsuchen UX ✅ |
| ~~#67~~ | Abbreviaturen Header (124 Texte) ✅ |
| ~~#70~~ | pc join spacing ✅ |
| ~~#14~~ | Sonderfall Lizenzen ✅ |
| ~~#50~~ | Fix 43 test failures → 121/121 passing ✅ |
| ~~#42~~ | Persistent lemma pages ✅ |
| ~~#43~~ | Playwright test coverage ✅ |
| ~~#46~~ | Merge Lemma-Suche ✅ |
| ~~#21~~ | Rename Konzepte→Begriffe ✅ |
| ~~#35–40~~ | Provenance metadata (5 batches) ✅ |

## Strategic Direction

1. **TEI model consolidation done** — Soll-Modell (#32) fully implemented. Both schemas written (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), all 682 files validated. Target models: [TEI-MODEL.md](TEI-MODEL.md) + [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md).

2. **FAIR data** — Make all MHDBDB data citable and programmatically accessible (#45). Enables external collaborations (MWB, Wörterbuchnetz).

3. **TEI data quality** — Remaining structural fixes (#23, #26). Mostly blocked on human review.

4. **Frontend refinements** — TEI rendering (#17, prio-1), UI polish (#20), URL routing (#48), and advanced playground features (#47).

5. **Advanced search** — PoS-based search (#18) and foreign language search (#28) depend on corpus index extensions.
