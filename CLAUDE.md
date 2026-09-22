# CLAUDE.md

Operational briefing for Claude Code. Details live in `docs/`: this file is the concise pointer.

## Project in One Paragraph

MHDBDB TEI Repository: 667 TEI-encoded Middle High German texts with semantic annotations. **Frontend-only** (GitHub Pages, no backend). Pre-built JSON indexes replace runtime XML parsing. Target audience: medievalists and DH researchers.

**Transformation → active project:** Started as a one-time migration (old MHDBDB + RDF export → TEI-only repo); that migration is done. It is now an **active project with ongoing ingest** (WZB, ARITHMETIC, more planned), so every data change must propagate through the derived layer (indexes, corpus-derived `variants.xml`) or it drifts silently. The mandatory step sequence lives in `docs/DATA-MODEL.md` → Data-Change-Lifecycle; the normative ingest procedure (Stage-0 → Phase 1–3 → Backfill) in `docs/DATA-MODEL.md` → Ingest procedure.

## Documentation Hub

@docs/INDEX.md is imported here, so its catalog of the 15 promptotyping documents is already in context and is not repeated. Not part of that set: `docs/features/` (planning docs, alive only while their issue is open) and `docs/playbooks/` (reusable session procedures).

**Data that belongs to this project but may not live in it is listed in `sources/INVENTAR-ARCHIV.md`**: the 9.1 GB legacy archive at KZW's, and since 2026-09-22 also the two holdings in the DHCraft Drive under `Projekte/mhdbdb/extern/` (Trier Findebuch dump for #259, a De Gruyter volume), each with its licence condition and the byte count to check a copy against. A script whose data is missing is answered there rather than by asking KZW again.

### Language and constraints

Two questions, kept apart: **who is the text for** (decides the language) and **what is mechanically checked** (one rule, everywhere).

**Audience decides the language.**

- **Users** (`hilfe-*.html`, `impressum.html`, every page a reader sees in the browser): German.
- **The `docs/` set** (the 15 promptotyping documents): uniformly English. Not a matter of taste: the files cite each other, are read together, and are linked from seven places in the delivered help pages. #316 paid four stages for that uniformity, and one German section undoes it. German stays where it is *data*: frozen corpus header wording, Middle High German attestations, work titles, notes from `contributors.xml`. Nothing gates this, it is a writing rule.
- **Working notes** (`CLAUDE.md`, `JOURNAL.md`, `journal-archive.md`, `fehlerjournal.md`): no language rule at all. Pick whatever carries the thought best and never translate for its own sake. This file happens to be English, the JOURNAL happens to be German, and nothing hangs on either.

**Red lines go to `fehlerjournal.md` in the repository root, not into the JOURNAL** (since 2026-09-16). The JOURNAL is the promptotyping working log that `orient` and `handoff` look for by that exact name; the error counter is a different thing, jumped into by number rather than read end to end. The 35 lines written before that date were pulled out into `fehlerjournal.md` and left a one-line pointer at each original spot.

**One mechanical rule on top, and it holds everywhere:** no em-dashes (U+2014) in `.md` or in user-visible HTML, no exceptions by folder. Use a colon, a comma, a parenthesis or a sentence of its own; if the dash is the *subject* (a quoted title, a bibliographic entry), put it in backticks, which is the Markdown equivalent of `chr(0x2014)` in code. Code comments are the only carve-out. The gate is `scripts/audit/check-no-em-dash.py` (CI: `no-cdn-check.yml`): HTML, JS and CSS in full, Markdown only in the lines a PR **adds** (`--diff-base <rev>`, fences and inline code excluded). Existing text is never rewritten for it, so a red gate means the line you just wrote, not the file you touched.

The narrow version was tried on 2026-08-03 and dropped the same day: carving out "user-visible Markdown" cost 267 lines of scope machinery, produced two fresh holes of its own (`git mv docs/x.md publications/x.md` smuggled the existing dashes into the publication path), and reopened the question "is this file user-facing?" for every new file. One blunt rule is cheaper than a boundary that has to be adjudicated. Measured cost of the blunt version: 5 of the last 100 commits, 6 lines.

**Real umlauts (ä ö ü ß) wherever German prose is actually written**, meaning the delivered pages and the German that remains inside `.md`. Not in `scripts/`, whose comments have used ASCII substitutes from the start (534 of them, and the Windows console is the reason). This one has **no** gate and none is planned: measured on 2026-08-03, German prose in the delivered pages carries zero substitutes, and the only HTML hits are anchor ids like `#ueberblick`, which are correct as they stand.

Commit messages and the comments inside `scripts/` are German by habit; nothing hangs on it.

## Directory Layout

```
assets/js/           # Main site JS (app.js, search/, rendering/, storage/, lib/)
assets/css/          # Stylesheets
authority-files/     # 8 XML authority files (source of truth, incl. contributors.xml since 2026-04-14)
tei/                 # 667 TEI corpus files
data/                # Pre-built indexes (.json.gz, generated)
api/                 # Static JSON API (generated by scripts/build-api.py, #45)
sources/             # Legacy ingest sources (Linecode), not normative, #248
schema/              # RELAX NG (mhdbdb.rnc/.rng, mhdbdb-authority.rnc/.rng) + examples
scripts/             # Python build scripts + data wrangling (topology: scripts/README.md)
ingest/              # Review artefacts of the ingest and disambiguation runs (ari, pos-disambig, wvv, wzb)
includes/            # Nav/footer/Matomo fragments, injected into the pages by build-pages.py
playground/          # Research tool (self-contained sub-app)
lemma/               # Persistent lemma pages (Issue #42)
testing/             # Playwright tests (results in testing/test-results/, gitignored)
docs/                # Knowledge documentation
publications/        # Blog posts, reports
temp/                # Scratch, gitignored, never commit
```

## Commands

```bash
npm run serve                    # Dev server on :8080
npm test                         # Playwright via scripts/run-tests.js. The VERDICT line is the result, not the console summary or the exit code. NEVER use `npx playwright test` from root
npm run test:changed             # only specs touched since origin/main; does NOT replace npm test before a push
npm run test:quick               # three core specs as a smoke test (22 tests)
python scripts/build-authority-index.py   # Rebuild authority index
python scripts/build-corpus-index.py      # Rebuild corpus index
python scripts/build-api.py               # Rebuild static JSON API
```

## Hard Constraints

- **TEI namespace**: `http://www.tei-c.org/ns/1.0`, always
- **UTF-8**: all files
- **Desktop-only**: min 1200px width
- **IndexedDB required**: large indexes cached in browser
- **Position counting**: only `<w>` elements with `@lemmaRef`; Python and JS must match exactly
- **Data before schema**: when existing data (corpus, authority files) conflicts with the schema, migrate the data first, do not loosen the schema. Loosening is admissible only where the data migration would be disproportionately expensive or semantically dangerous, and then it is documented explicitly as a `GAP` comment in the schema (see `schema/mhdbdb.rnc`, GAPs 1–11).

## Git Rules

- **NEVER commit or push without user testing and approval**
- **Concurrent sessions share the working directory**: never use `git add -A` or `git add .`. Always stage specific files by name (`git add path/to/file1 path/to/file2`). Another Claude session may have staged files that do not belong in your commit. Example: commit `8b5d0e6ac` swept router files into an unrelated #84 commit because `git add -A` captured another session's staged playground edits.
- Never force push to `main`
- **Small documentation changes go straight to `main`**: no branch, no PR, no waiting for CI. Branch plus PR plus review is for code, data, build scripts and anything a gate or test can catch.
- **Evergreen issue (#44): NEVER close**, no `Closes #44` or `Fixes #44` in commits. Permanent tracking issue (labeled `evergreen`, pinned). (#91 Zenodo was mislabeled `evergreen` and is a normal closeable task, corrected 2026-06-09.)
- **`fable-reviewer` before the first push of every PR branch, mandatory.** The local review is not a second opinion on top of the CI bot, it is the one that costs nothing: what it finds costs zero CI rounds, what the bot finds costs one by construction. Use `fable-reviewer` (the diff), never `fable-advisor` (open design questions, and on a finished diff it produces rounds without behavioural change). Pass what it cannot see: branch and base, the goal in one sentence, the round number, and from round 2 on the previous findings and how they were handled. Rationale and history in the `feedback_fable_review_all_prs` memory; the same rule is Regel 11 of `docs/playbooks/BETRIEBSVERTRAG.md`, but that document only binds playbook sessions.
  - **On a diff that fixes something, add one question to the handover: what has this change made true that could be false before?** (#397, from a case on #386.) A fix that establishes an invariant robs every check built on its opposite of its subject. There, a transitive hull started returning the root unconditionally, and the caller's `if not concepts` guard could never fire again: it still stood there, looked like a check, and was none. Three instances missed it, and not out of carelessness. All three were looking at the numbers of the changed set, because that was what the fix was about; the guard was untouched by the change, stood elsewhere, and nobody searches there. **Whoever reviews a fix reviews the new thing. What hung on the old thing, nobody reviews.** The question costs nothing, needs no tool and no run. A mutation probe does not replace it: it would have helped here, but only if someone had thought to mutate the **unchanged** part, and after a fix nobody does.
  - **If a session is not allowed to spawn agents** (some session configurations forbid it), that does not void the rule: ask for the review **before** pushing, not after. On 2026-08-10 the missing local round let a live-breaking bug reach an open PR (`NARRATOR_KEY` as U+0000; both reviewers found it on the first look, and the merge was already requested when it surfaced).
- **On a data PR the CI review bot goes red, and the local review therefore has to carry the PR. But open the bot's comment before dismissing it: a red check is not a finding, and it is not proof that there is none.** Twice the run was a finished review with measured findings that the action merely marked red, and #377 was merged with that comment unread. In practice: no rerun (a run that genuinely aborted aborts identically), no splitting the PR into a corpus and an index commit (that buys a bot pass with an index that does not match the corpus, which the Data-Change-Lifecycle forbids), no hunting for a config switch (there is none). And never judge from `gh api .../pulls/N -q .changed_files`, which returns 0 even on a PR whose diff the platform did compute: read the `<changed_files>` block in the job log, or use `gh pr view N --json files`. `gh pr checks` shows only the last run, `gh run list --workflow claude-code-review.yml` the history, and a `skipped` or `cancelled` is no statement about the review. **And a conflicting PR runs nothing at all, which reads exactly like a run that has not started yet.** A `pull_request` workflow checks out the merge commit GitHub builds for the PR, and on a conflict that commit is never built, so no workflow is triggered: not red, not skipped, absent. `gh pr checks` prints „no checks reported“ in that case and in the waiting-for-CI case alike, and the value that separates them is `mergeable`, which it does not show. Measured on #456 on 2026-09-21 with a before and after on the same branch: 0 check runs while `CONFLICTING`, 4 within seconds of the merge commit that resolved it, with no other change. So on a PR whose checks stay empty, read `gh pr view N --json mergeable` before waiting, and note that it answers `UNKNOWN` for a few seconds while GitHub computes. **The bot cannot execute Python, so on a measurement PR it reviews the code and not the result**, which leaves the numbers to the local round. Run table, measurements and the explanations already ruled out: [DEVELOPMENT.md → CI: Claude Review Bot](docs/DEVELOPMENT.md#ci-claude-review-bot).
- Rebuild indexes after modifying XML in `authority-files/` or `tei/`
- **Tests never need permission, and that is deliberate** (chsteiner, 2026-08-24). `npm test` and any other check worth running starts without asking: before a push, after a data change, as a verification at the end of a task. The older rule asked first, on the grounds that a run occupies port 8080 and starts browsers alongside somebody else's frontend work. In practice it mostly stalled sessions that had nothing else to do but wait for the answer, and it sat crosswise to "run tests before pushing": a test that needs clearance first is, in case of doubt, a test that did not run. What stays untouched is the commit and push rule below. A free test run is not a free release.
- Run tests before pushing
- Update `docs/` when architecture changes

### Commit Format
```
Brief description

## Changes
- What changed

Co-Authored-By: Claude <noreply@anthropic.com>
```

### Branches
- `main` is production; everything else is a topic branch off it, named by whoever opens it (`claude/*` dominates, plus `docs/*`, `fix/*`, `feature/*`)
- `initial-data-wrangling` is archived (`pre-main-site` has since been deleted)

## Self-Inflicted Overhead

Measured on 2026-08-02 across three PRs (#330, #332, #333): 27 findings in 18 review rounds, only 10 of them real defects. 13 were false claims in comments this project had written itself. Half the review load was homemade, hence:

- **A finding is itself a claim.** Measure before adopting it, whether it comes from the CI bot, from `fable-reviewer` or from a human. A second opinion once quoted 60 and 1,360 where the measured values were 51 and 1,406: it had carried forward the very numbers that were the problem. Adopting that turns a correct figure into a wrong one and attaches a citation to it.
- **No claim in a comment that does not hold.** Every number in one has to be measured. What the statement does not need gets deleted rather than sourced.
- **From review round 3 on, only act on behavioural findings.** Wording findings are settled by shortening the comment. In #332 rounds 3 and 4 cost around 20 minutes each for zero change in behaviour.
- **No full CI run for comment-only commits.**
- **Issue threshold:** a finding becomes a ticket only if it needs a **decision** the agent may not take, needs a **human**, or is a **work package of its own** (ingest, corpus change, more than half a day). Everything else is fixed on the spot or dropped (#331 was filed and fixed by the same session an hour later).

## Asking, and what has to happen before you ask

**"Bei unsicheren Entscheidungen immer beim Mensch nachfragen, aber erst, nachdem alle seriösen Quelldaten (Normdaten, Lexika usw.) geprüft wurden."** (chsteiner relaying @wachauer, 2026-09-10, #28. She wrote it as a general rule, not as an answer to that ticket, which is why it stands here rather than there.)

The sentence has two halves and both are load-bearing. Half one forbids writing an uncertain assignment into the data as if it were settled. Half two forbids spending a human's attention on something the sources would have answered: an "is this right?" that could have been a `grep` is not diligence, it is a delegation.

**The case it was written for.** On 2026-09-10 this project's own session characterised the lemma `Alanya` as a Turkish toponym, from the headword alone. The corpus said otherwise, and it said so cheaply: the lemma has seven attestations, all in `WVO`, and six of them read "der kuenc von alanye". A land with a king, so Alanien, the Iranian people, not the town on the Turkish coast. One minute of looking at the attestations. **Both halves were broken in the same move**: the source data went unchecked, and nothing was asked. A one-text lemma is almost always story-world specific and almost never modern geography, and that alone should have stopped the guess.

The practical form of the rule for a corpus or authority decision: put the **attestations with their context** in front of yourself, not the headword; check what the existing annotation already says; only then form a judgement; and what remains uncertain after that goes on a list for the human rather than into `lexicon.xml`. A run that writes 8,559 names from headwords alone makes the `Alanya` mistake 8,559 times and nobody sees it.

The rule does not compete with the issue threshold above, under Self-Inflicted Overhead. That one says which findings become tickets; this one says what you owe before you put a question to a person at all.

## Corpus scope, in one line

**Texts written before 1600.** Early New High German is in, markedly younger material is out. Decided by @wachauer on 2026-09-10 (#263), and it replaces an earlier reading of "around 1500" that was derived from two examples and was too narrow.

The rights side sits next to it and is separate: a text has to pass the period **and** the licence. Both, with their legal sources and the 25-year rule from § 76b UrhG-AT, are in `docs/RESEARCH.md` under Corpus Scope and Rights Basis; the ingest procedure in `docs/DATA-MODEL.md` names them as the gate before Stage 0. Date a candidate first, a text outside the period needs no rights clearance.

## Working an Issue

**Read the comments, never only the body. Always** (chsteiner, 2026-09-06). In this project the body is where the question was *first* asked; the thread is where it was answered, narrowed, measured and often turned around. A session that reads only the body is not underinformed, it is misinformed, and it will redo work that is already merged or ask for a decision that has already been made. Measured on the tickets open on 2026-09-06: **#216** carries its whole work package in 12 comments and its body does not even contain the keyword of the next step; **#392, #393 and #394** say „zu entscheiden" in the body while their comments say implemented and merged; **#28** holds a chain in which the author twice withdraws his own earlier finding. **The body is the oldest text in the ticket, and in an active project the oldest text is the least likely to be true.**

- **How to read one:** `issue_read` with `method: "get_comments"` on every ticket you touch, and page through when there are more than a handful. Over `gh` it is `gh issue view N --json title,body,comments`; the bare `gh issue view N` shows the body alone and does not say so.
- **Never start an `auto:blocked` issue "anyway".** Several of them have their material sitting outside the repo entirely. **The same goes for `auto:frozen`, where the temptation is larger** because no `wait:*` sits next to it: the ticket is parked until a date that lives in the thread, and it owes nobody anything. An absent debt is not a clearance.
- **A `Closes #N` is not an acceptance.** Where KZW, Julia or an external reviewer still has to sign off, the issue stays open even though the code is merged and live (see `feedback_kzw_ui_final_testing`). On 2026-08-05 six issues were in exactly that state.
- **Before putting a question to a person**, see "Asking" above: the sources come first.

## Issue Labels

Rebuilt on 2026-08-05, down from 28 labels. **No count is given here**, because the one that stood here did not survive its own month: "16" was written on 2026-08-05 before the four `wait:*` labels were added later the same day, and it was still standing on 2026-09-21, when `gh label list` printed 20. That command is the count. The scheme is built **for agents**: the team barely uses labels, so they exist to tell a session what it is allowed to touch. Three orthogonal axes, **exactly one label per axis**, plus two flags. Full legend, per-issue reasoning and the ping list live in the body of **#44**.

- **`auto:*`** is the one that governs a session's behaviour: `auto:full` (just do it) | `auto:brief` (1 to 3 questions up front, then run to completion) | `auto:checkin` (decision points along the way: sampling, batch size, scope) | `auto:pair` (only in a session with Chris) | `auto:blocked` (waiting on KZW, Julia, Linda, or an external party such as Carina, Alan, Silvan or a funder) | `auto:frozen` (deliberately parked until a date). The dividing line between `pair` and `blocked`: a missing **answer from a third party** is `blocked`, a need for **Chris's time and authority** is `pair`. The one between `blocked` and `frozen` is who owes something: `blocked` waits for a person, `frozen` waits for the calendar, so **a frozen ticket carries no `wait:*`** and stays out of the ping list.
  - `auto:frozen` enters the scheme with this commit; the GitHub label and the first holder, **#271**, follow once it is merged, because until then the ticket would drop out of every table while the headline count kept counting it. #271 is parked until June 2027 by KZW's decision of 2026-09-10 (proposed 15:24, year confirmed 16:41). Before the label existed, that ticket kept `wait:kzw` for want of anything better and appeared in her daily ping list although she had answered. A session noted that in the ticket instead of fixing it, and on 2026-09-17 KZW called the reliability of the whole triage into question in #406 over exactly this class of error: "Bereits beantwortete Fragen dürfen nicht erneut als Entscheidungsrückstand bei mir erscheinen." **A label that cannot express a state produces a false one**, and a note next to it does not repair that, because the ping list is generated and the note is not.
  - What a session does with an `auto:frozen` ticket: nothing. Do not start it, do not ping anyone about it, read the date in the ticket. It is the one state in which neither work nor an answer is owed.
- **`area:*`**: `data` | `frontend` | `playground` | `pipeline` | `docs` | `orga`
- **`effort:*`**: `small` (an hour or less) | `medium` (half a day) | `large` (a day or more)
- **`wait:*`** (`kzw`, `julia`, `linda`, `extern`): only on `auto:blocked`, and mandatory there. More than one is allowed and often right (#315 waits on KZW and Julia). Everyone outside the team is `wait:extern`, whoever they are, and the name lives in the ticket: four labels stay readable, a dozen do not. Any other `wait:` value is a hard error in the daily run. This is what the ping list in #44 is built from.
- **Flags**: `ingest` (corpus intake, its own workstream) and `evergreen` (#44 only, the sole issue exempt from the axes because it is maintained rather than worked off)

**Half of #44 is generated.** `scripts/audit/build-issue-matrix.py` writes the quick stats, the ping list and one table per autonomy level between the `MATRIX` markers in the issue body; `issue-matrix.yml` runs it daily. Everything outside the markers is hand-written and carries a date, not a truth. The same run checks the axes: a ticket without `auto:*` turns the run red **and** gets named in the body itself, because it falls out of every table while the headline count still includes it.

**Re-label every issue a session touches, in the same session.** That is what keeps the matrix from rotting, which is what happened to the old labels: the 2026-08-05 pass had to read all 53 open issues end to end because nobody had.

## Temporal Artifacts (promptotyping convention)

- **Feature docs** (`docs/features/`): live while the issue is open. On completion, extract the critical knowledge into the stable docs (CONTRACTS.md, ARCHITECTURE.md and so on), then delete. Git history is the archive.
- **Playbooks** (`docs/playbooks/`): a deliberate exception to the deletion rule, being reusable rather than ticket-bound. After each session: work in the lessons, refill the session-specific appendix, move the core knowledge into the JOURNAL. They authorize NOTHING by themselves and run only after an explicit kickoff by the user. The shared operating contract lives in `docs/playbooks/BETRIEBSVERTRAG.md` and is copied verbatim into the kickoff prompt; `docs/playbooks/README.md` is the entry point.
- **Health check reports**: run via `/promptotyping check` (skill in `~/.claude/skills/promptotyping/`). Full report → scorecard in JOURNAL.md (3-4 lines, dated). Action items → separate issues. **No .md file in `docs/`**: the report is disposable once the action items are extracted.

### Health check list (MHDBDB-specific)

After larger documentation changes, and quarterly even without them, against creeping drift.

- **Flow check:** read every modified doc end to end. Does it flow logically?
- **Algorithm spot check:** pick 3 algorithms, compare the pseudocode in the docs against the actual code
- **XPath spot check:** verify 3 XPaths from the docs against the build scripts
- **Rebuild test:** ask "could I delete every `.js`/`.py` and reconstruct them from the docs?" If yes for the critical paths (search, build pipeline, reader), we are at 85%+
- **Meta questions:** are the .md names self-explanatory? Are there too many or too few promptotyping docs (overlap vs. mixed concerns)? Always list structural doc changes with a reason.

**Triggers:** after PRs touching `docs/`, after new build scripts or changed algorithms, after new authority files or TEI elements, quarterly.

## Gotchas

- **Angle bracket entities** (`&lt;`, `&gt;`) in `<pc>` are correct XML, not bugs
- **Nav and footer are build-injected**: do not edit them in the HTML pages. The source is `includes/` plus `scripts/build-pages.py` (marker regions); `build-pages.py --check` is the drift gate. The mobile menu stays inline. See DEVELOPMENT.md.
- **Zotero cache** (`.zotero_cache.json`) is gitignored, use `--offline` for reproducible builds
- **German title case**: Zotero sync capitalizes words except articles and prepositions (der, die, von, und...)

## Key Patterns

- **3-stage lemma resolution**: exact match → variants dictionary → prefix-match fallback. The dictionary holds normalized **mappings**, not the raw forms from `variants.xml`, so there are markedly fewer mappings than forms; both numbers are correct and measure different things, and the values live in CONTRACTS.md §C rather than here (#279). Stage 3 matches prefixes in both directions (stem input → lemma, inflected input → lemma), never unbounded substrings: that made "böses" resolve to `ês`/`ô`/`sê` (#224). Predicate shared by main site and playground in `assets/js/lib/lemma-resolve.js`.
- **Lemma highlight matching**: a `<w>` is highlighted only if `@lemmaRef` contains the searched id as an exact whitespace-separated token (never a substring: `#lemma_308` must not match `#lemma_3089`). Centralized in `assets/js/lib/lemma-match.js` (`lemmaRefMatchesId`). See CONTRACTS.md §B.1 (#126/#130).
- **MHG normalization**: `â→a, ê→e, î→i, ô→o, û→u, ä→ae, ö→oe, ü→ue, ŏ→oe, ŭ→ue`. Centralized in `assets/js/lib/text-normalizer.js`.
- **Pre-built indexes**: authority (~3 MB gz) + corpus (~40 MB gz). Current versions in TEI-MODEL.md §11 (source of truth). See DATA-MODEL.md for schemas.
