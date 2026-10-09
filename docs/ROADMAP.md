# Roadmap

Strategic priorities for the MHDBDB TEI Repository. Last full pass 2026-10-05; the #28 and #216 lines updated 2026-10-09.

See [Issue #44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44) for the full triage matrix with per-issue status.

## Now: decisions still dominate, but a session has work again

**Measured 2026-10-05 over all open issues: 90 open, the evergreen #44 and 89
others. Of those 89: 51 `auto:blocked`, 11 `auto:pair`, 3 `auto:frozen`, 23
`auto:checkin` and 1 `auto:full`.** Sixty-five of the eighty-nine wait for a
person or a date, so the backlog is still mainly a decision backlog. But it is
no longer only that: on 2026-09-07 there were 6 `auto:checkin` tickets out of 62
open, today a session can move 24. The numbers change with every ticket, so
re-measure them (`gh issue list --state open --limit 300 --json labels`) rather
than quoting this paragraph.

**The annotation series have reached their target values, and what is left of
them are decisions plus a few named repairs.**

- `stat` (#369) applied 7,760 of 7,855 cases and held back 95. KZW's review of
  those 95 (#371, 2026-09-15) was applied with PR #456 on 2026-09-21: 76 tokens
  annotated. Measured on 2026-10-05, 19 tokens of the forms `stat`, `stât`,
  `stät`, `stát` still carry no `@lemmaRef`, in 13 files. They are the 17 cases
  KZW left open and the 2 that would need a new lemma, and both groups sit with
  her. #371 stays open for her acceptance.
- `minne` (#216) applied 5,435 tokens and held back 1,547. What is still ours
  is listed in the thread, among it the NAM lemma "Minne", the repair case
  `MR2_27022210102100_5` (`SAX_24200_4` was fixed on 2026-10-09), the WVV address cases, the
  `GWTK` suspects and a rule for POS-TAGSET.md.
- Series 3 (`sere`, `not`, `nam`, `leit` and the rest of the list from PR #210)
  does not start while two series wait on editorial feedback.

**#28 (foreign language) has its pre-check done and owes one step of its
own.** On 2026-09-23 the 26 lemmata with more than 500 attestations were checked
against corpus context, existing annotation and a dictionary each: 16 borrowed,
1 Latin quotation word, 7 not foreign at all, 2 uncertain. One question went to
KZW: does "UR no" from 2026-07-29 also hold for the origin layer in the lexicon?
Two steps were announced in the same comment as not waiting for that answer.
One is done: the unattested sense copies at `engebrechen` and `gebrechenhaft`
(KZW's decision of 2026-09-10) were removed on 2026-10-09, authority index
1.9.21. The other is still ours: the list of Latin attestations for layer A.

**Some tickets carry no work of ours any more, only an acceptance or one
answer:** #251 has a released check path since 2026-09-23 and one design
question. #58 has its count fixed (#436) and waits on KZW's choice of form for
clicking through to the attestations (a, b or c, asked 2026-09-23). #193 was
closed on 2026-10-05 with release v1.1.0.

**Redundancy in the TEI headers is generated rather than maintained since
#399.** For `handschriftencensus`, `GND` and `wikidata` `works.xml` is the master
and `scripts/sync/sync_tei_headers.py --works --check` gates the mirror in
`data-integrity.yml`; on 2026-10-05 it reported 667 of 667 files in agreement.
The contract is [CONTRACTS §F.4](CONTRACTS.md#f4-work-identity-worksxml-leads-the-tei-header-mirrors).
`mwb-sigle` stayed header-owned, because the MWB assigns its sigles per
manuscript redaction while `works.xml` knows identifiers per work only; the
model question behind that is #404.

**What sorts KZW's share is #406**, a triage by how much a single decision
releases. It was rebuilt on 2026-09-21 after KZW rejected the previous version
for listing answered questions as her backlog, and refreshed on 2026-10-05 with
an addendum after all threads involved had been read in full.

## Next: pings to people

**Who is waiting on whom is generated daily into the body of
[#44](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/44)**, from the
`wait:*` labels, by `scripts/audit/build-issue-matrix.py`. Read it there. A
hand-maintained copy stood here until 2026-09-02 and drifted, as an ungenerated
copy of a generated list does.

One row does not fit into #44 and therefore stays here, because it has no issue to
carry a label:

- **Putting Brom and Nieser in touch** (chsteiner, to Vlastimil Brom and Florian
  Nieser). Brom asked about own or fine-tuned language models on MHDBDB data;
  ParzivAI is the nearest answer and interesting for both sides. State of play in
  [RESEARCH.md → Downstream Reuse and Related Projects](RESEARCH.md#downstream-reuse-and-related-projects)

## Frozen until December 2026

**#27** (POS workflow) and **#18** (multi-lemma plus PoS search) are
`auto:frozen`. KZW set the next pass over the undifferentiated CNJ tokens for
December 2026 (#27, 2026-07-10), and #18 depends on #27: measured on
2026-08-10, 28.4 percent of the 7,532,982 position-counted tokens carried a
compound tag. Nobody owes anything on either until
then. Until 2026-10-05 #18 stood here as a decision cluster, which it has not
been since its relabelling on 2026-09-23.

## Future: needs design, or waiting for a trigger

| # | What | Key question |
|---|------|-------------|
| #92 | ARITHMETIC ingest: stage 0 is built and the six manuscripts are converted in `ingest/ari/`, the schema extension (PD-001) is on `main` | Carina's metadata per manuscript, open since 2026-05-16 |
| #139 | ingest the CoReMA corpus: pilot of five cookbooks (Bs1, GR1, H2, M11, W1) as proposed by Helmut Klug; H2 has no published recipe objects | a joint session with Chris |
| #141 | Borte ingest: task 0 (the borte.md metadata template) is delivered in the issue | Alan's metadata; scheduled after #139 |
| #118 | language stages in the TEI headers: the two first-ranked sources of the concept are empty (no header dating, only print years in `works.xml`), the virgule marks 16 texts as a calibration set | KZW's four format and threshold questions; then it is a procurement project |
| #123 | „König vom Odenwald": the text is already in the corpus as `KVO` (Olt 1988) | does KZW want the Schröder 1900 edition as well? Asked 2026-09-23 |
| #63 | update of the concept system: Julia is planning the WSD gold standard, gaps from #498 and #423 are noted | scope (Julia) |
| #93 | moving the text series typology: the tree view was split off as #361; the move itself means six content areas, a co-author outside the team and two vocabularies that disagree | which vocabulary state holds, and how to involve Marco Heiles |
| #109 | FWF single project (deep corpus analysis, NER pipeline, phonetic rhyme analysis, visualizations): proposal by KZW, small budget, max. 50 % external funds | a scope note for the proposal text |

**Index size and a splitting strategy** stands here without an issue number, and
that is deliberate: the budget question of #111 is **decided and gated**, and the
issue is closed. [ADR-019](DECISIONS.md) sets 50 MB gz / 200 MB raw for the corpus
index, `scripts/audit/check-index-budget.py` measures it in `data-integrity.yml`.
Measured 2026-10-05: 42.22 MB gz, **84 percent** of the budget, 7.78 MB of
headroom. No field is pre-selected. ADR-019 fixes only the rule for choosing: the
breached axis names the field (gz → `texts[].lemmata`, raw → `texts[].words`). The
next trigger is a feature, not a date: #27 and #109 breach the budget in every
combination of their estimates.

It sits outside the table for the same reason as the paragraph above: a row in a
table whose first column is `#` has to carry a number, and this point no longer
does. Writing prose into that column instead would leave `pruefe_roadmap()`
structurally blind to the row, and a gate that a text edit can switch off is worse
than a formatting inconsistency.

## What is finished lives in the JOURNAL

This file looks forward. What is completed stands chronologically and with
reasoning in [JOURNAL.md](JOURNAL.md), older entries in
[journal-archive.md](journal-archive.md). Until 2026-08-02 a table „Recently
Completed" stood here as well; keeping a second chronicle next to the JOURNAL
did not work and was given up (#316).

The same happened again on a smaller scale and was cleaned up on 2026-10-05: two
sections from July (the search semantics session of 2026-07-29 and the post-merge
care after 2026-07-08) had stayed here as retrospectives. Their content is in
journal-archive.md under 2026-07-08, 2026-07-09, 2026-07-29 and 2026-07-31.

## Strategic Direction

1. **TEI model consolidation done** – the target model (#32) is fully implemented, the #32 follow-up is complete at 17/17 (P1-5 with 3 context-specific enum patterns for `idno/@type`, plus the WZB shelfmark, the stage 1 PI cleanup, the CI push trigger). Both schemas written (`mhdbdb.rnc`, `mhdbdb-authority.rnc`), all 667 corpus + 8 authority files validated. Target models: [TEI-MODEL.md](TEI-MODEL.md) + [TEI-MODEL-AUTH-FILES.md](TEI-MODEL-AUTH-FILES.md). Architecture Decision Record: [ADR-013 "Data Consolidation Before Schema Relaxation"](DECISIONS.md#adr-013-data-consolidation-before-schema-relaxation).

2. **TEI data quality** – the structural fixes of the first half of 2026 (#23, #26, #30, #85, #110) and the Wenzelsbibel ingest (#34) are closed. The active workstreams are the content-word homograph series (#216, #369 with #371), corpus cleanup tickets such as #228, #252, #390 and #470, and the ingests waiting in the table above (#92, #139, #141).

3. **Playground TEI text analysis** – release 1 (#87 to #90) was closed on 2026-05-11, and the concept distribution of release 2 is live (`concept-distribution.js`, see FEATURES.md). Release 3 (POS shares) depends on #27 and is frozen with it.

4. **FAIR data and citability** – the static JSON API (#45) and the Zenodo concept DOI (#91) make MHDBDB data externally citable and programmatically accessible. Two versions are archived under it: v1.0.0 (2026-06-10) and v1.1.0 (2026-10-05). This enables external collaborations (MWB, Wörterbuchnetz, a ZfdG submission).

5. **Frontend refinements** – reader (#17 ✅), UI polish (#20 ✅), the reading view render policy (#101 ✅ 2026-05-12, Julia) and lemma linking to MWB and Lexer (#73 ✅ 2026-05-12) are complete. The dead-code cleanup of the upload UI is done (#314, 2026-07-31): about 2,200 lines across 19 files, three of them entirely.

6. **Advanced search** – PoS-based search (#18) is frozen with #27 until December 2026; foreign language search (#28) is in its data phase, see „Now".
