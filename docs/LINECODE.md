# Linecode → TEI Mapping

Reference for the legacy MHDBDB Linecode system and its translation to TEI. Linecodes predate TEI in the MHDBDB project and survive in the corpus as the numeric portion of `<w>` and `<pc>` `@xml:id` attributes. Understanding them is required for diagnosing structural issues in migrated texts (see Issue #23 for missing stanzas and Issue #85 for the umbrella covering missing `<div>` wrappers).

**Status:** Stable reference. Extracted from Julia Hintersteiner's canonical mapping file and a direct inspection of the corpus.

> **Audience:** This file is a technical reference specification, written primarily for development and automated tooling (precise, machine-oriented).

**Canonical data files:**

- [`docs/data/linecode-mapping.csv`](data/linecode-mapping.csv) – UTF-8 copy of Julia's `Mhdbdb_to_TEI(Linecode).csv`. Letter → TEI element mapping (`c` → `<div type="chapter">`, `s` → `<lg type="stanza">`, etc.). The table in this document mirrors that CSV; edit the CSV first when the mapping changes.
- [`docs/data/linecode-templates.csv`](data/linecode-templates.csv) – UTF-8 export of `scripts/audit/TEXT_DATA_TABLE.xlsx` (Sheet `MHDBDB Texte`, 665 rows × 30 cols). **Per-text Linecode template** (column `LINECODE`, e.g. `MKB` → `000000000000cddss--`) plus full per-text metadata (TITLE, AUTHOR, EDITION, …). Single source of truth for which structural slots a given text encodes. Generated 2026-05-11 from the XLSX in the repo; if KZW updates the XLSX, regenerate the CSV.

**Live exports from MHDBDB-old (Katharina, 2026-05-11):** Beyond Julia's frozen handover, **Katharina can produce fresh Linecode-with-content exports per sigle on demand** from the legacy MHDBDB. First example: BDK.txt for #102 (1056 lines, 70 manuscript folio pages). Use cases:

- Texts not in `OUTDATED-Texte-mit-Linecode/` (e.g. BDK, MSF) can be requested as `<SIG>.txt` exports.
- Cross-checking discrepancies between Julia's handover state and current MHDBDB-old (e.g. DIS: 408 lines in handover vs. 406 in OD – 2 head lines added).
- Resolving structural ambiguities surfaced by Julia's 5-column doc (`Abstellplatz/Dokumentation neues TEI vs alte DB 2.0.csv`) where the handover Linecode lacks a marker the DB tracked separately (e.g. DUB `parallel tradition`).

Workflow: comment on the relevant GitHub issue with a request like *"@wachauer kannst du einen MHDBDB-old-Export für `<SIG>` liefern?"*. Katharina notes that some legacy encodings were technically pragmatic (e.g. encoding recipes as `<lied>` so the frontend would display them with counter numbers), so the Linecode is descriptive of the historic DB state, not necessarily the philologically optimal encoding.

## Context

The old MHDBDB system stored text structure as a parallel **Linecode** – a positional letter+number string alongside the plaintext. Each letter position in the template represented one structural level (paragraph, verse, heading, page, etc.); at the corresponding position in an encoded instance, the digits recorded the running counter for that level. For instance, the letters `cc` in a template would mean "chapter counter, up to two digits wide" – in an encoded line, the two digits at that position record the running chapter number. The letter‑to‑structure mapping was hierarchical but less standardized than TEI.

During the migration to TEI, the Linecodes were automatically converted into TEI markup, and each annotated token received an `xml:id` derived from its Linecode position:

```
SIGLE_<digits>_<tok>
│      │        │
│      │        └── token index within the structural position (0-based)
│      └─────────── numeric portion of the Linecode (leading zeros stripped)
└────────────────── text sigle
```

The original Linecode→TEI conversion scripts are not in this repo. Julia's handover folder contains analysis and QA scripts under `Abstellplatz/`, but not the original converter. Her handover (PDF, CSV, raw `.txt` files for 291 texts) is the surviving source this document reconstructs the mapping from and verifies against the current corpus.

## Letter → TEI Element Table

Mirrors [`docs/data/linecode-mapping.csv`](data/linecode-mapping.csv) with post-#32 status annotations.

| Code | Legacy name | Post-#32 TEI target | Notes |
|------|-------------|---------------------|-------|
| `-`  | LINE | `<l n>` (verse) or `<lb n/>` (prose) | Linecode does not distinguish verse from prose. The original converter emitted `<l>` everywhere; 18 prose texts were migrated to `<lb/>` during #32 (see TEI-MODEL.md §8.1; migration complete, no surviving `<l>` in prose). |
| `a`  | PARAGRAPH | `<p>` | |
| `b`  | BAND | – | Originally `<div type="volume">`. Removed corpus-wide during #32 as an outdated technical structure (volume was a DB-era artifact, not a semantic structural level). Book-level counters preserved as `<div type="section">` where applicable – see TEI-MODEL.md §3.5. |
| `c`  | CHAPTER | `<div type="chapter" n>` | |
| `d`  | LIED | `<div type="song" n>` | |
| `f`  | NONGRADED | – | Originally `<div type="nongraded">`. Not in the post-#32 `<div>/@type` enum. Julia marked these as "unecht eingestuft". No occurrences remain in `tei/` as of 2026-04-15. |
| `h`  | HEADLINE | `<hi rend="head">` (usually) or `<head>` (rare) | **Value `0` → ignore (no element).** Non-zero values usually mean "should be printed bold" in the original source, so the default TEI target is `<hi rend="head">`. Only when the position is clearly a structural heading (between stanzas, at the top of a `<div>`) should `<head>` be emitted. The original converter frequently emitted `<head>` for every non-zero `h` value, producing stray `<head>` elements that are really bold markers – see the "Diagnosing `<head>` vs `<hi rend="head">`" recipe below. |
| `i`  | INSERTION | `<supplied>` | Editorial additions. |
| `k`  | COMMENT | `<note>` | |
| `l`  | HANDWRITINGSHEETCOLUMN | `<cb type="manuscript" n/>` | Value `1` = A (left column), `2` = B (right column). |
| `n`  | TONVARIATION | – | Originally `<div type="tonvariation">`. Julia marked the mapping as uncertain. Not in the post-#32 enum. No occurrences in `tei/` as of 2026-04-15. |
| `p`  | PAGE | `<pb n/>` | |
| `s`  | STANZA | `<lg type="stanza" n>` | Legacy converter often emitted `<div type="stanza">` (per Julia's note referencing Alan). Migrated to `<lg type="stanza">` during #32. Zero `<div type="stanza">` remain in `tei/` as of 2026-04-15. |
| `t`  | TEIL | – | Originally `<div type="part">`. Migrated to `<div type="section">` during #32 (per TEI-MODEL.md §3.5). |
| `u`  | PARALLELUEBERLIEFERUNG | `<div type="parallel" n>` | Counter = number of parallel transmissions for the passage. |
| `v`  | HANDWRITINGSHEETPAGE | `<pb type="manuscript" n/>` | Value `1` = recto, `2` = verso. Julia marked this as a verification point – worth double-checking wherever recto/verso matters downstream. |
| `x`  | DATE | `<note type="date">` | Julia marked the mapping as uncertain. In HZU/HZU2 the `@n` attribute previously carried an encoded MMTT format; migrated to Klartext (e.g. „24. Februar") on 2026-04-15, see closed Issue #84 / TEI-MODEL.md §3.5. |
| `y`  | YEAR | `<note type="year">` | Julia marked the mapping as uncertain. |
| `z`  | NUMBER | `<note type="number">` | Julia marked the mapping as uncertain. |
| `0`  | NULL | (skip) | Padding zero at this position; or "this position is not used by this line". |

**Post-#32 note.** `schema/mhdbdb.rnc` allows seven *standard* `<div>/@type` values (`chapter, section, number, song, parallel, colophon, recipe`) plus ~24 optional arithmetic-domain values (`div.type.arithmetic`, added 2026-05-08 with the ARITHMETIC ingest, see DECISIONS.md PD-001); `@type` itself is optional (GAP 1). The corpus currently uses only the seven standard types (no ARI files ingested yet). Linecode letters `b` (BAND), `f` (NONGRADED), `n` (TONVARIATION), and `t` (TEIL) produced div-types outside this *standard* set and were either migrated (t → section) or removed (b, f, n) during the #32 migration. Letter `s` (STANZA) moved from `<div>` to `<lg>`. Any remaining occurrences of the old types in `tei/*.tei.xml` are bugs.

## xml:id ↔ Linecode

The relation between a Linecode and its surviving `xml:id` form is **leading-zero stripping** – nothing more.

Verified against `tei/ALL.tei.xml` and Julia's `OUTDATED-Texte-mit-Linecode/ALL.txt`:

```
Raw Linecode (ALL line 1): 0000020100010
xml:id numeric part:             20100010
                            ^^^^^
                            5 leading zeros stripped
```

Every line of ALL in the raw file starts with a 13-digit Linecode followed by the plaintext:

```
0000020100010 ich bitte iuch, allez himelischez her,
0000020100020 daz ir hiute unt immer sit min wer
0000020100030 wider den endelosen spot.
0000020100040 helfet mir alle, daz mir got
0000020100050 ein so gutez ende fuge,
...
```

The corresponding TEI:

```xml
<l n="1">
  <w xml:id="ALL_20100010_0" ...>ich</w>
  <w xml:id="ALL_20100010_1" ...>bitte</w>
  ...
</l>
<l n="2">
  <w xml:id="ALL_20100020_0" ...>daz</w>
  ...
</l>
```

Each `<w>` (and each `<pc>`) carries the same numeric portion for all tokens in the same structural position; the trailing `_0`, `_1`, … is the token index, resetting whenever the `<digits>` portion changes. For ALL and other verse texts that means at every new `<l>`; for prose it means at every new `<lb/>`, `<p>`, or whichever boundary the text's Linecode encodes.

## Per-Text Variation

**Both the internal field layout and the overall Linecode width vary per text.**

- *Same overall width, different field roles:* `tei/ALL.tei.xml` (verse, 13-digit Linecode encoding paragraph / parallel / line / head **per Julia's template gloss**; ALL's TEI body itself is flat `<l>` elements with no containing `<lg>`, `<p>`, or `<div>`) and `tei/BRIX.tei.xml` (recipe) both have 13-digit Linecodes, but BRIX encodes a recipe counter in positions where ALL encodes a paragraph counter.
- *Different overall widths:* Julia's stanza fix script (`Stanza Problem/fix_tei_stanzas.py` in the handover folder) hard-codes per-text regex patterns with different widths – `0000000(\d{3})(\d{2})` for ANN (12-char Linecodes, 5 non-zero digits) versus `0000000000(\d{2})(\d)` for AT (13-char Linecodes, 3 non-zero digits). There is no single template that fits the whole corpus.

**Julia's published example template** in the handover PDF – `0000000000aaau----h`, glossed as paragraph (3 digits) + parallel (1) + line (4) + head (1) = 9 active positions – is **illustrative only**. It does not match ALL's actual 13-digit layout, nor any single general pattern. Treat the PDF template as a teaching device, not as a mechanical decoder.

**Consequence for decoding.** There is no single formula that turns `20100010` into "paragraph 2, parallel 1, line 1, head 0" without first knowing ALL's specific field layout. If mechanical decoding is needed, the per-text layout must be recovered by inspecting the raw `.txt` files in `OUTDATED-Texte-mit-Linecode/` and matching digit changes to observable structural boundaries in the plaintext. (`TEXT_DATA_TABLE.csv` has a `LINECODE` column but was empty in the rows sampled – see Source Material.)

## Reading `xml:id` Patterns in Practice

Every annotated token carries:

```
<w xml:id="SIG_<digits>_<tok>" lemmaRef="..." pos="..." ana="..." corresp="...">wort</w>
```

- `SIG` – text sigle (`ALL`, `NIB`, `PZ`, …)
- `<digits>` – numeric portion of the Linecode, leading zeros stripped. Width varies per text; for ALL it is always 8 digits. Julia's ANN/AT regex patterns imply 5 non-zero digits for ANN and 3 for AT, so the observed range is at least 3–8 digits, with no verified upper bound.
- `<tok>` – token index within the current structural position, 0-based. It resets whenever `<digits>` changes from one token to the next.

A change in `<digits>` signals **some** structural boundary – which one depends on the text's Linecode layout (new line for a verse text, new paragraph or `<lb/>` for a prose text, new recipe for a recipe text, and so on). Without the per-text layout, you cannot tell *which* level changed, but you can still tell *that* a boundary occurred – that alone is often enough for diagnostics.

## Practical Diagnosis Without Positional Decoding

The recipes below avoid the decoding trap by working from the raw Linecoded plaintext side by side with the current TEI, rather than from the xml:ids alone. For 199 sigles that plaintext is now in the repo under [`sources/linecode/`](../sources/linecode/) (#248); look up the file for a sigle in [`sources/linecode-manifest.csv`](../sources/linecode-manifest.csv). Otherwise use Julia's `OUTDATED-Texte-mit-Linecode/<SIG>.txt` or request a fresh MHDBDB-old export.

### Diagnosing Missing Stanzas (Issue #23)

**Preconditions:** Julia's raw `<SIG>.txt` file for the affected text (one line per verse, each prefixed with its Linecode) and the current `tei/<SIG>.tei.xml`.

1. Open the raw `<SIG>.txt` file. Each line of text is prefixed with its Linecode. **Read the plaintext column, not the Linecode digits**, to identify where stanza boundaries occur in the text: use the usual philological cues – new topic, new verse group, rhyme or meter shift, or a stanza division from the source edition. Without the per-text field layout there is no reliable way to read boundaries from the Linecode digits alone, so plaintext stays the primary signal.
2. For each identified stanza boundary, note the Linecode prefix of the first line of the new stanza. That prefix becomes an anchor for cross-referencing against the TEI.
3. Open `tei/<SIG>.tei.xml` and search for the anchor as an `xml:id` (Linecode with leading zeros stripped). The corresponding `<l>` should be wrapped in a `<lg type="stanza">` element.
4. If the wrapper is missing, that is a case to fix. Repeat for every stanza boundary in the text.

Julia's `Stanza Problem/fix_tei_stanzas.py` was her earlier attempt at fixing stanzas, using the **positional-decoding approach this section deliberately avoids** – it hard-codes per-text regex patterns for specific sigles (e.g. ANN, AT). It is useful as a reference for which texts she had already tackled and which regex shapes fit them, but do not run it blindly: it was written before #32, has not been re-verified against the current corpus, and in general the plaintext-first workflow above is more robust than extending its per-text regex table.

### Diagnosing `<head>` vs `<hi rend="head">`

A `<head>` element embedded *inside* a verse line or stanza – typically with only one or two words, and no accompanying chapter/section break – is the typical fingerprint of a mis-conversion: the original `h` position was non-zero (so the converter emitted `<head>`) but the intended semantics were "print this bold" (so the target should have been `<hi rend="head">`). Real structural headings sit between stanzas or at the top of a `<div>`, not mid-verse.

### Diagnosing Verse vs. Prose Line Markup

The Linecode's `-` always became `<l>` in the original conversion. If a text is clearly prose (paragraphs, no verse numbering, no stanzas) but has `<l n>` elements, it is a candidate for the same migration that was applied to the 18 prose texts listed in TEI-MODEL.md §8.1 during #32. That migration is complete; a newly discovered case would need its own fix rather than an add-on to a batch. See TEI-MODEL.md §8.1 for the prose-vs-verse criteria.

### Recovering a Flattened Level (Issue #236, FR3)

The second documented case of a lost structural level after DUB in #85 – and the first where the level was recovered mechanically and verified end to end.

**Symptom.** FR3's handover Linecode is `0000000uddaaass---h`; the leading `u` is PARALLELUEBERLIEFERUNG. The ingest dropped that level, leaving 23 sibling `<div type="song">` with `@n` reused across witnesses: 28 (Ton, Strophe) pairs were multiply occupied, one stanza five times over. No passage in the text was uniquely addressable, and 1,563 of 9,595 `<l>` (16.3 %) entered every frequency, keyness and co-occurrence calculation as if they were independent text.

**Why decoding worked here.** The sections above warn against positional decoding – rightly, because the per-text field layout is usually unknown. FR3 is the opposite case: its template is recorded in `docs/data/linecode-templates.csv`, so the field layout is *given*, not guessed. **When the template is known, decoding is exact and is the better tool.** The distinction is template-known vs. template-unknown, not "decoding is unreliable".

**Recipe.**

1. Read the per-text template from `docs/data/linecode-templates.csv` and the letter semantics from `docs/data/linecode-mapping.csv`. For FR3: `u` at position 8, `dd` Ton, `aaa` Strophe, `ss` stanza, `---` verse, `h` heading.
2. Join source to TEI via the `@xml:id` stem, which is the **Linecode with leading zeros stripped**: `0000000105201010010` → `FR3_105201010010_0`. This is lossless in both directions and needs no text matching.
3. Compare the structure derived from the source against the structure present in the TEI *before* changing anything, and treat a mismatch as a stop condition (`scripts/ingest/frauenlob/01-verify-linecode-vs-tei.py`). Derive the level per `<lg>` from its first token's `xml:id`, not from the enclosing `<div>` – then the same check stays valid after the rebuild and can serve as a permanent gate.
4. Rebuild the level (`02-restore-parallel-level.py`), asserting afterwards that every (Ton, Strophe) address is now unique.

**Watch out for defective codes.** 86 of the 9,605 lines in FR3's source carry only 18 digits instead of 19 – a missing leading zero, affecting exactly VIII,215 `u=1` and V,209 `u=2`. Left-pad with `zfill(19)` before slicing. Without that, two witnesses vanish silently and the structure looks self-consistent while being wrong.

**The `h` position in the same file.** FR3 also illustrates the `<head>` mis-conversion described above, in its other failure mode: the converter emitted *nothing at all*. The roman tone numerals sit in the text flow as ordinary tokens, some carrying `@lemmaRef` and `@ana`. They are found by the same rule – the last digit of the `xml:id` stem is the `h` position, so a stem not ending in `0` is a heading token. That located 26 tokens in FR1, 2 in FR2 and 14 in FR3.

## Source Material

**In the repo since 2026-07-30 (#248): [`sources/linecode/`](../sources/linecode/)** – 306
Linecoded plaintext files covering 199 of the 667 corpus sigles, byte-verbatim copies from the
legacy archive, with per-file provenance and sha256 in
[`sources/linecode-manifest.csv`](../sources/linecode-manifest.csv). This is the **first
in-repo Linecode source**: the diagnosis recipes above no longer require a file handover for
those 199 texts. Not normative, never indexed, never edited – see
[`sources/README.md`](../sources/README.md).

For the 468 sigles it does not cover, the routes below still apply.
[`sources/INVENTAR-ARCHIV.md`](../sources/INVENTAR-ARCHIV.md) records what else the archive holds,
names four sigles (`OVW`, `OSW`, `MSG`, `MSW`) whose coded source survives only as a Word file, and
flags the `FnhdC/` folder as licence-blocked. The Word template that *produced* the Linecodes is
preserved as [`sources/legacy-tooling/linecode-generator.dot`](../sources/legacy-tooling/) – the
generating side of the conversion, the only part of the original tooling that survives.

Julia's handover folder (stored on Katharina's SharePoint/OneDrive):

- `Mhdbdb_to_TEI(Linecode).csv` – canonical letter→TEI mapping. Copied into this repo as [`docs/data/linecode-mapping.csv`](data/linecode-mapping.csv).
- `Zusammenfassung-Linecode2TEI.pdf` – Julia's handover summary. Attached to Issue #31 on GitHub.
- `OUTDATED-Texte-mit-Linecode/<SIG>.txt` – raw Linecoded plaintext for 291 texts. Primary source for per-text layout recovery and diagnosis. **Frozen state** – for fresher data, request a Katharina export (see live-export note above).
- `TEXT_DATA_TABLE.xlsx` – full per-text metadata table including Linecode templates. **Now in the repo** as `scripts/audit/TEXT_DATA_TABLE.xlsx` and exported to [`docs/data/linecode-templates.csv`](data/linecode-templates.csv). Earlier audit-note ("LINECODE column empty in sampled rows") was wrong: the XLSX has 665/665 templates filled, distinct templates: 131. The misread came from looking at the older CSV export.
- `Dokumentation.xlsx` – older comparison table between the legacy DB and the TEI export. The 5-column "Anmerkung"-CSV variant (`Abstellplatz/Dokumentation neues TEI vs alte DB 2.0.csv`) is the source of Julia's per-text "fehlt"-notes (e.g. DJEM "parallel tradition fehlt"); used by #85.
- `Stanza Problem/fix_tei_stanzas.py` – Julia's exploratory fix script for missing stanzas, with hard-coded per-text regex patterns for ANN and AT.

The letter→TEI mapping in this document and in `docs/data/linecode-mapping.csv` is the authoritative post-#32 reference. The PDF remains useful as the original narrative explanation.

## Cross-References

- [`docs/data/linecode-mapping.csv`](data/linecode-mapping.csv) – letter → TEI element mapping (canonical, mirrored in the table above)
- [`docs/data/linecode-templates.csv`](data/linecode-templates.csv) – per-sigle Linecode template + full text metadata (665 rows; the lookup table for "which slots does text X encode")
- **TEI-MODEL.md §3.5** – post-#32 `<div>/@type` enum and migration history for Linecode letters `b` (BAND/volume), `t` (TEIL/part), and `s` (STANZA)
- **TEI-MODEL.md §8.1** – the 18 prose texts where Linecode `-` became `<l>` and was then migrated to `<lb/>`
- **Issue #23** (closed 2026-06-11) – Fehlende Stanza-Auszeichnung (104 Fälle). Decoding durch dieses Dokument freigeschaltet; Bulk-Stanza-Sweep gelaufen (Corpus-Index v4.1.1), Rest via WVV-Rebuild (v4.1.3).
- **Issue #85** (closed 2026-05-12) – Umbrella for 26 texts with missing `<div>` wrappers (chapter/song/parallel + DL1 edge case). Unblocked by this document.
- **Issue #84** (closed 2026-04-15) – HZU/HZU2 `<note type="date">` MMTT→Klartext migration (Linecode letter `x` in Urkunden-Texten); new ingests use the Klartext form directly
- **Issue #31** – Julia's original handover issue
