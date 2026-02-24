# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Updated Feb 2026.

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: Quick Wins (claude-ready, effort:small)

Work that can be done immediately, no decisions needed.

| # | What | Domain |
|---|------|--------|
| #35, #37, #38, #39, #40 | Add provenance metadata to TEI headers (5 provider groups) | data:provenance |
| ~~#21~~ | ~~Rename "Konzepte" → "Begriffe" in UI~~ ✅ | frontend |
| #20 | Readability fixes (font sizes, contrast) | frontend |
| #31 | Format Linecode2TEI documentation as markdown | documentation |

## Next: Clear but Larger

Well-specified, ready to build, but require more effort.

| # | What | Domain |
|---|------|--------|
| #42 | Persistent lemma pages for MWB linking | frontend |
| #45 | Static JSON API (FAIR data) | pipeline + frontend |
| #17 | TEI structural rendering in reader view | frontend |
| #43 | Playwright test coverage (un-skip main site, add reading view tests) | testing |

**#42 and #45 are related:** #45 provides the data API, #42 provides the HTML pages. Can be built together or sequentially (API first, pages second).

## Blocked: Needs Human Input

Cannot proceed without decisions, external feedback, or manual review.

| # | What | Who's needed |
|---|------|-------------|
| #36 | Provenance model design (TEI `<sourceDesc>` pattern) | KZW + team |
| #14 | License restrictions for 10 texts (display rules) | KZW |
| #22 | TEI Encoding Guidelines README section | @juliahin |
| #26 | Missing `<pb>` elements (17 texts) | JH manual check |
| #29 | Stricker-Texte structural errors | KZW on "Abschnitte" |
| #23 | Missing stanza markup (104 texts) | Linecode explanation needed |
| #30 | Manual review of TEI structural elements (~20 texts) | Human review |
| #34 | Ingest Wenzelsbibel + CoReMA | Julia + Helmut coordination |
| #32 | TEI schema / ODD — is a formal schema wanted? | Team decision |

## Future: Needs Design

Interesting features that need scoping and architectural decisions before implementation.

| # | What | Key question |
|---|------|-------------|
| #18 | Multi-lemma + PoS tag search | Corpus index needs PoS data; how to extend? |
| #28 | Foreign language search in playground | Index needs `xml:lang`; new UI section design |
| #27 | POS workflow expansion | Gemini vs Claude, kontrahierte Verben rules |
| #42 | MWB API integration (beyond lemma pages) | MWB ID mapping, API format |

## Strategic Direction

1. **FAIR data first** — Make all MHDBDB data citable and programmatically accessible (#45, #42). This enables external collaborations (MWB, Worterbuchnetz) and increases project visibility.

2. **TEI data quality** — The provenance issues (#35-40), structural fixes (#23, #26, #29, #30), and schema work (#32) strengthen the corpus as a reliable research resource. Most of this is blocked on human review.

3. **Frontend refinements** — UI polish (#20, #21), TEI rendering (#17), and test coverage (#43) improve the user experience but are lower priority than data quality and API.

4. **Advanced search** — PoS-based search (#18), foreign language search (#28), and POS workflow (#27) are future enhancements that depend on corpus index extensions.
