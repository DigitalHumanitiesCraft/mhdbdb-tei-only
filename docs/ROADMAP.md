# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Updated 2026-09-07.

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: the constraint is decisions, not capacity

**Measured 2026-09-07 over all open issues: 62 open, of them 48 `auto:blocked`, 7
`auto:pair`, 6 `auto:checkin` and the evergreen #44.** Fifty-five of sixty-two
cannot be moved by a session at all, they need an answer from KZW, from Julia,
from Linda or from Chris. That is the single most important fact for planning
this project right now, and it is not a capacity problem: **the backlog is a
decision backlog.** The number moves with every ticket opened or closed, so
re-measure it rather than quoting this line.

**The annotation series have arrived at their target values, and what is left of
them are decisions.** `stat` (#369) applied 7,760 of 7,855 cases; the remaining
95 are held back on purpose, and 51 of those wait on a lemma decision in #371
that has shrunk to three sense choices at lemmata that already exist. `minne`
(#216) is at 78 percent with 1,547 tokens left. The next content-word targets in
line are `sere` (7,915), `not` (7,269), `nam` (6,709) and `leit` (6,550), and
none of them should start while two series wait on editorial feedback.

**Six tickets carry no work at all any more, only an acceptance:** #58, #169,
#193, #239, #250 and #251 are built, merged and live, most of them since the end
of July. #251 holds a shared four-step check path that covers #239 and #169 as
well. They sit in the ping list of #44 as if they were work, and they are not.

**Redundancy in the TEI headers is generated rather than maintained since
#399.** For `handschriftencensus`, `GND` and `wikidata` `works.xml` is the master
and `sync_tei_headers.py --works --check` gates the mirror in `data-integrity.yml`;
drift is zero at 667 of 667, so the generator is a no-op today and the point of
it is that it stays one. The contract is [CONTRACTS §F.4](CONTRACTS.md#f4-work-identity-worksxml-leads-the-tei-header-mirrors).
`mwb-sigle` stayed header-owned against the original intention, because the MWB
assigns its sigles per manuscript redaction while `works.xml` knows identifiers
per work only; the model question behind that is #404.

**What sorts the rest is #406**, a triage of KZW's share by how much a single
decision releases. Its top entry is the sharpest illustration of the paragraph
above: fifteen minutes of reading in #28 decide 77.2 percent of the non-name
tokens of that workstream, and no machine can take it over, because the
annotation confirms the questionable assignment instead of correcting it.

## Before that: search semantics decided and implemented

**Autonomous issue session on 2026-07-29** ([MASTERPLAN-AUTONOME-ISSUE-SESSION](playbooks/MASTERPLAN-AUTONOME-ISSUE-SESSION.md)), triggered by KZW's four decisions of 2026-07-28. Two code PRs plus a meta PR, both code PRs frontend-only: no data PR, the indexes stay at 4.1.8 / 1.6.4.

| PR | Issue | Content |
|----|-------|--------|
| #245 | #169 | the proximity search measures the span instead of the distance to the anchor, dedup keeps the hit with the shortest distance, the fast-path dictionary is gone |
| #246 | #239 | word-component search as a second mode in the lemma explorer |

**Merge order:** #245, then #246, then the meta PR (stacked on #245, because both touch `JOURNAL.md` and `ROADMAP.md`). Cancel running review jobs before merging.

**The break in the numbers that KZW wanted on record:** hit counts from proximity searches with **three or more lemmata** dated before 2026-07-29 are systematically too high. Until then `maxDistance` limited only the distance of each lemma to the anchor, not the span, which could therefore reach twice that. Measured on „minne + herze + leit" at distance 20: the largest old hit had a real span of **38**. With two lemmata the window fix changes nothing, the dedup fix does (243 to 244 for „minne + herze"). Details in the JOURNAL entry of 2026-07-29.

**The fast path was no longer a future risk but an active bug:** five of the eleven hardcoded entries resolved wrongly, because the lemma ids had been reassigned since they were written down. Searching for „bier" (beer) in the playground got you the pear. The lesson for the codebase: a fast path in front of a central resolution never passes, by construction, the place that would notice its error.

**Written on 2026-07-29, and overtaken since:** at that point #216 stood here as ready to start, with about 7,000 unannotated tokens in 262 texts. The series has run since; the current state is in the „Now" section above (78 percent done, 1,547 tokens left, waiting on editorial feedback). The line stays as a dated retrospective instead of being deleted, because the prioritization it points at (series 2 onwards, PR #210) is still the one in force. Same error type as the two entries corrected on 2026-07-31 below: a status sentence in the present tense outlives its state, and `pruefe_roadmap()` cannot see it, because it checks table rows for **closed** issues and #216 is neither.

**Newly attested, and equally interesting for #109 and for data curation:** 27,166 of the 43,879 lemmata (61.9 percent) carry their morphological components in the lexicon (`<etym type="morphological">`), and those statements already ship in the authority index. The word-component search now uses them as a filter. That refutes the widespread assumption that decomposing compounds in the frontend necessarily needs stemming; for the remaining 38 percent without recorded word formation it still holds.

**Done on 2026-07-29:** the playground cleanup round. Eight functions without callers removed (among them two that additionally cut context windows with index positions into the unfiltered `<w>` list, and two that were orphaned by the deletion itself), `resolveLemmaIds` deduplicated, and both co-occurrence modes now refuse to work instead of reporting every occurrence of a single lemma as a hit at distance 0. The deviating counting of the upload fallback is documented with measurements in CONTRACTS §B.

**Open from the same corner:** #251, implemented meanwhile as PR #256, see above.

## Ongoing: post-merge care plus unblocked workstreams

**Health check done (2026-07-09):** a drift check against main after the merge week. Finding: the core docs (TEI-MODEL §11, INDEX.md, the data counts via `doc-count-audit.py`, algorithm spot checks on §B.1/§D.2/posAll) were drift-free; 5 peripheral drifts fixed (the version pointer in CLAUDE.md, the tool count in the README, the #23 status in LINECODE, the DATA-MODEL changelog for v4.1.4/v4.1.5, a version placeholder in DECISIONS). Scorecard in the JOURNAL.

The autonomous merge session (2026-07-08, [MASTERPLAN-AUTONOME-MERGE-SESSION](playbooks/MASTERPLAN-AUTONOME-MERGE-SESSION.md)) brought all 13 PRs of the issue session onto main (#174 to #186); 13 issues were closed automatically (#163 #164 #159 #168 #158 #162 #160 #161 #134 #145 #27 #167 #170), while #68/#86/#28/#171 stay open as planned (partial work). Authority index v1.6.0 (posAll[]) is live, live smoke checks for both stack chains and the independent PRs passed. Details: the JOURNAL entry of 2026-07-08 (merge session) plus the closing report in #44.

Became ready to start:
- **#92 ARITHMETIC stage 1** – the escaping blocker was merged in #185; the metadata questions to Carina are still open
- **#18 multi-lemma plus PoS search** – the POS policy (#27) is merged; it needs POS data in the corpus index

**Correction of 2026-07-31:** two entries stood here as ready to start, but both have been done since 2026-07-10 and are therefore taken off the list.

- **#187 posAll display migration** (commit `edb16dd3f`, issue closed as completed; JOURNAL, morning of 2026-07-10). All display sites listed in the issue now read `posAll[]` with a first-value fallback for older caches, plus `verse-position-search.js`, which the issue list had missed.
- **The WVV stanza run**: the clause „the run itself is still pending" dated from 2026-07-08 and was overtaken on 2026-07-10 (JOURNAL: „#110/WVV complete"). Measured against `tei/WVV.tei.xml`: 489 continuous `<lg>`.

Both are the same type of error: the ROADMAP describes the state of a document instead of the state of the project, as soon as an entry is not carried along after it is done.

**#124 is closed** (2026-07-10, by KZW) and is listed here only because the paragraph that stood in its place presented it as an open priority for a month. Cookieless Matomo has been live since 2026-06-17 (`includes/_matomo.html`, opt-out plus a data protection section in the legal notice, commit `7abbf7672`), the site runs as **site-ID 15** in the central Salzburg Matomo at `webstatistics.sbg.ac.at`. Dashboard access is not a project task but a request to IT Services (read access for a PLUS account); the legal-basis details for the data protection text were suggested to be asked in the same message, and nothing in this repository records an answer. The Matomo dependency named in the side task of #255 is that request, not a blocked ticket.

This paragraph is the blind spot the roadmap gate names in its own docstring: `pruefe_roadmap()` in `scripts/audit/build-issue-matrix.py` only sees a closed issue in the first column of a **table row**, deliberately, because checking every `#N` in the file would have reported 45 lines on its first run. An entry written as prose falls through, and this was one.

## Next: pings to people (after the merges)

**Who is waiting on whom is generated daily into the body of
[#44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44)**, from the
`wait:*` labels, by `scripts/audit/build-issue-matrix.py`. Read it there.

Until 2026-09-02 the same list stood here a second time, hand-maintained, 15 rows.
It had drifted, as an ungenerated copy of a generated list does: two of its rows named
issues that had been closed for weeks, #129 since 2026-07-10 and #224 since 2026-08-06,
both of them already closed when the file was last edited on 2026-08-07. Four further
dead rows stood elsewhere in the file (#140, #172 and #106 closed before that edit,
#111 two days after it), and they were cleaned up in the same pass. This is the failure
mode #316 removed on 2026-08-02 for the table „Recently Completed", and the ping table
was simply left behind in that cleanup.

One row does not fit into #44 and therefore stays here, because it has no issue to
carry a label:

- **Putting Brom and Nieser in touch** (chsteiner, to Vlastimil Brom and Florian
  Nieser). Brom asked about own or fine-tuned language models on MHDBDB data;
  ParzivAI is the nearest answer and interesting for both sides. State of play in
  [RESEARCH.md → Downstream Reuse and Related Projects](RESEARCH.md#downstream-reuse-and-related-projects)

## Needs clarification: the decision cluster (chsteiner)

| # | What | Key question |
|---|------|-------------|
| #169 | search semantics (audit 3/6) | all four points implemented (the point numbers are audit findings, not issue numbers): point 45, the 3-stage drift, in PR #227 (ADR-016), points 15/48/51 on 2026-07-29 after KZW's approval of 2026-07-28. What remains open is acceptance. The break in the numbers for proximity searches with 3+ lemmata is in the JOURNAL of 2026-07-29 |
| #18 | multi-lemma plus PoS search | the POS policy (#27/#181) is merged and it can be specified; it needs POS data in the corpus index |

Two rows left this table on 2026-09-02 because their issues are closed: **#140**
(human-readable documentation) and **#172** (test suite policy). Both were already
closed when the file was last edited.

## Future: needs design, or waiting for a trigger

| # | What | Key question |
|---|------|-------------|
| #141 | Borte ingest: task 0 (the borte.md metadata template) is delivered in the issue | KZW's prioritization (after #139) |
| #28 | foreign language annotation: the data phase plan is merged (`docs/features/FREMDSPRACHEN-PHASENPLAN-28.md`, the lemma level leads) | implement phases 0 to 4 in the next data slot |
| #139 | ingest the CoReMA corpus | trigger and capacity |
| #118 | language stages from authority data | policy plus an architecture decision |
| #123 | „König vom Odenwald" | scope and time window (KZW) |
| #63 | update of the concept system | scope and policy (KZW) |
| #93 | moving the text series typology (from marketext.at to a MHDBDB subpage): SKOS data from the `textseries` repository, tree visualization; dysfunctional `dhplus` URIs to clean up | visualization plus a comparison against the authority files |
| #109 | FWF single project (deep corpus analysis, NER pipeline, phonetic rhyme analysis, visualizations): proposal by KZW, small budget, max. 50 % external funds | a scope note for the proposal text |

**Index size and a splitting strategy** stands here without an issue number, and
that is deliberate: the budget question of #111 is **decided and gated**, and the
issue is closed. [ADR-019](DECISIONS.md) sets 50 MB gz / 200 MB raw for the corpus
index, `scripts/audit/check-index-budget.py` measures it in `data-integrity.yml`.
Measured 2026-09-02: 42.23 MB gz, **84 percent** of the budget, 7.77 MB of
headroom. No field is pre-selected. ADR-019 fixes only the rule for choosing: the
breached axis names the field (gz → `texts[].lemmata`, raw → `texts[].words`). The
next trigger is a feature, not a date: #27 and #109 breach the budget in every
combination of their estimates.

It sits outside the table for the same reason as the paragraph above: a row in a
table whose first column is `#` has to carry a number, and this point no longer
does. Writing prose into that column instead would leave `pruefe_roadmap()`
structurally blind to the row, and a gate that a text edit can switch off is worse
than a formatting inconsistency.

#106 (verse boundary features) left this table on 2026-09-02, closed.

## What is finished lives in the JOURNAL

This file looks forward. What is completed stands chronologically and with
reasoning in [JOURNAL.md](JOURNAL.md), older entries in
[journal-archive.md](journal-archive.md). Until 2026-08-02 a table „Recently
Completed" stood here as well: it reached back to April but ended on 2026-07-08,
while 80 PRs had been merged since. Keeping a second chronicle next to the
JOURNAL did not work and was therefore given up (#316).

## Strategic Direction

1. **TEI model consolidation done** – the target model (#32) is fully implemented, the #32 follow-up is complete at 17/17 (P1-5 with 3 context-specific enum patterns for `idno/@type`, plus the WZB shelfmark, the stage 1 PI cleanup, the CI push trigger). Both schemas written (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), all 667 corpus + 8 authority files validated. Target models: [TEI-MODEL.md](TEI-MODEL.md) + [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md). Architecture Decision Record: [ADR-013 "Data Consolidation Before Schema Relaxation"](DECISIONS.md#adr-013-data-consolidation-before-schema-relaxation).

2. **TEI data quality** – structural fixes (#23, #26, #30, #85), schema hardening (#32 ✅), the Wenzelsbibel (#34, phase 3 at 92.5%) and the WVV follow-up (#110) are the active workstreams. Most of the remaining structural fixes are blocked on KZW's review.

3. **Playground TEI text analysis, release 1 done** – UX cleanup (#87), word frequency (#88), text statistics (#89) and lemma distribution (#90) were all closed on 2026-05-11. Release 2 (concept distribution) and release 3 (POS shares, depending on #27) are still unplanned.

4. **FAIR data and citability** – the static JSON API (#45) and the Zenodo DOI (#91, stub delivered) make MHDBDB data externally citable and programmatically accessible. This enables external collaborations (MWB, Wörterbuchnetz, a ZfdG submission).

5. **Frontend refinements** – reader (#17 ✅), UI polish (#20 ✅), the reading view render policy (#101 ✅ 2026-05-12, Julia) and lemma linking to MWB and Lexer (#73 ✅ 2026-05-12) are complete. The dead-code cleanup of the upload UI is done (#314, 2026-07-31): about 2,200 lines across 19 files, three of them entirely.

6. **Advanced search** – PoS-based search (#18) and foreign language search (#28) depend on corpus index extensions.
