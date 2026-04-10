# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Updated Apr 2026.

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: Claude-Ready

Work that can be picked up immediately.

| # | What | Domain | Effort |
|---|------|--------|--------|
| #14 | License update → CC BY-NC-SA 4.0 (TEI headers + UI footer) | data+frontend | M |
| #20 | Readability fixes (font sizes, contrast) — done, awaiting approval | frontend | S |
| #22 | TEI Encoding Guidelines (convert SharePoint docs) | documentation | M |
| #52 | Playground "Authority Files" card clickable | minor-UX/UI | S |
| #53 | "Korpus durchsuchen" UX improvement | minor-UX/UI | S |

## Next: Clear but Larger

Well-specified, ready to build, but require more effort.

| # | What | Domain | Effort |
|---|------|--------|--------|
| #45 | Static JSON API (FAIR data) — [planning doc](features/045-static-api.md) ready | pipeline + frontend | L |
| #17 | TEI structural rendering in reader view | frontend | L |
| #48 | Playground URL routing (shareable views) | frontend | M |
| #47 | TEI Textanalyse im Playground (6 features) — needs scoping | frontend | L |

## Blocked: Needs Human Input

| # | What | Who's needed |
|---|------|-------------|
| #29 | Stricker/Kaufringer `<supplied>` → `<div type="parallel">` — structural mismatch, [awaiting clarification](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/29#issuecomment-3973088014) | KZW |
| #26 | Missing `<pb>` elements (17 texts) | KZW manual check |
| #23 | Missing stanza markup (104 texts) — partially actionable | Linecode docs (#31) |
| #31 | Doku: Linecode2TEI — do #23 + #29 first | KZW |
| #30 | Manual review of TEI structural elements (~20 texts) — Alan review done, triage ready | KZW (draft-fix reviews) |
| #34 | Ingest Wenzelsbibel + CoReMA | Julia + Helmut coordination |
| #42 | Persistent lemma pages — feature done, scope expanded (Lemmata-Explorer rename, semantic explorer) | Decision: close + new issues? |

## In Progress

| # | What | Status |
|---|------|--------|
| #27 | POS Workflow expansion | Active — linguistic decisions answered, batch list provided |
| #30 | TEI structural fixes | Auto-fixes ready (71 edits, 4 files), draft-fixes prepared, aligned to TEI-MODEL.md |
| #32 | TEI model consolidation | **Corpus + Authority migration complete** — Corpus: Phases A-E (675 files, PR #69 merged). Authority: Phases F-K (7 files, 14/14 validations, authority PR pending) |

## Future: Needs Design

| # | What | Key question |
|---|------|-------------|
| #18 | Multi-lemma + PoS tag search | Corpus index needs PoS data; depends on #27 |
| #28 | Foreign language search in playground | Index needs `xml:lang`; new UI section design |

## Recently Completed

| # | What |
|---|------|
| ~~#50~~ | Fix 43 test failures → 121/121 passing ✅ |
| ~~#54~~ | Document multi-lemma dedup in CONTRACTS.MD ✅ |
| ~~#55~~ | Document lemma pages for rebuild feasibility ✅ |
| ~~#42~~ | Persistent lemma pages (base feature) ✅ |
| ~~#43~~ | Playwright test coverage ✅ |
| ~~#46~~ | Merge Lemma-Suche into Multi-Lemma-Suche ✅ |
| ~~#21~~ | Rename "Konzepte" → "Begriffe" ✅ |
| ~~#35–40~~ | Provenance metadata (5 batches + model) ✅ |

## Strategic Direction

1. **TEI model consolidation done** — Soll-Modell (#32) fully implemented. Corpus: Phases A-E (675 files, 15M+ transformations). Authority: Phases F-K (7 files, genre normalization, ID cleanup, Zotero refresh, Frauendienst/Frauenbuch split). Both schemas written (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), all 682 files validated. Target models: [TEI-MODEL.md](TEI-MODEL.md) + [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md).

2. **FAIR data** — Make all MHDBDB data citable and programmatically accessible (#45, #42). Enables external collaborations (MWB, Worterbuchnetz).

3. **TEI data quality** — Remaining structural fixes (#23, #26, #29). Most blocked on human review.

4. **Frontend refinements** — UI polish (#20), TEI rendering (#17), URL routing (#48), and advanced playground features (#47).

5. **Advanced search** — PoS-based search (#18) and foreign language search (#28) depend on corpus index extensions.
