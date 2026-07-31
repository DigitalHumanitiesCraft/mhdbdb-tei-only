#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Classify lexicon.xml backfill gaps (Issue #115 / #44, Phase 2).

Read-only, idempotent. Consumes the base TEI corpus + lexicon.xml and groups
every *unresolved* lexicon reference (the 977 dangling refs found by
`check-authority-cross-refs.py`) by its lemma, then classifies each lemma:

  (A) MISSING_ENTRY  — lemma_N is absent from lexicon.xml; the whole <entry>
                       is gone. Form + POS are reconstructable from the corpus
                       (form = <w> text, POS = @pos), so a stub is proposable.
                       The sense->concept assignment stays curatorial.
  (B) MISSING_SENSE  — lemma_N exists, but one or more of its referenced senses
                       are absent. Either a curatorial gap (which concept?) or a
                       corpus @ana typo. Existing senses are listed for context.
  (C) TYPO_SUSPECT   — overlay on A: the dominant corpus form (normalised)
                       matches an *existing* lemma's <orth> under a different
                       id, so the corpus @lemmaRef/@ana is a likely typo,
                       fixable in the corpus (not the lexicon).

Why this matters (the Authority-Source-Model, ADR-015 / CONTRACTS §F):
the corpus leads, lexicon.xml is an index that must follow. Forward-only
ingest (e.g. wzb-sense-apply.py sets @ana on <w> but never writes lexicon.xml)
mints ids the index never learns about — the WZB drift. This script turns the
drift into an actionable, classified worklist; it never writes lexicon.xml.
Inserting stubs / enriching senses is a separate, team-approved step that
ends with an index rebuild.

Outputs (disposable work products, gitignored — not committed):
  scripts/audit/lexicon-backfill.json            machine-readable, full detail
  scripts/audit/lexicon-backfill-curatorial.md   human worklist for KZW/Julia
  scripts/audit/lexicon-backfill-stubs.xml       proposed <entry> stubs (A only)

Usage:
    py scripts/audit/classify-lexicon-backfill.py
"""

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    sys.exit("ERROR: lxml not installed — run: pip install lxml")

# Reuse the canonical MHG normalizer (parity with text-normalizer.js)
# und die gemeinsame Korpusauswahl (#287).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from mhg_normalizer import normalize_mhg
from corpus_files import PROJECT_ROOT, TEI_DIR, corpus_files

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

XML_NS = '{http://www.w3.org/XML/1998/namespace}'
TEI_NS = '{http://www.tei-c.org/ns/1.0}'

LEXICON = PROJECT_ROOT / 'authority-files' / 'lexicon.xml'
SCRIPT_DIR = Path(__file__).resolve().parent
JSON_OUT = SCRIPT_DIR / 'lexicon-backfill.json'
MD_OUT = SCRIPT_DIR / 'lexicon-backfill-curatorial.md'
STUBS_OUT = SCRIPT_DIR / 'lexicon-backfill-stubs.xml'

LEMMA_RE = re.compile(r'^lemma_(\d+)$')
SENSE_RE = re.compile(r'^lemma_(\d+)_sense_(\d+)$')
MAX_EXAMPLES = 4  # corpus citations kept per lemma for the worklist

# Id-range heuristics (see #115 forensics): ids minted by post-migration ingest
# (WZB Phase 1b et al.) start here. Below the threshold = legacy MHDBDB stock,
# so a dangling ref there is a *lost migration target*, not ingest drift.
INGEST_LEMMA_MIN = 78000
INGEST_SENSE_MIN = 117000


def sense_source(sense_id):
    """'ingest' for ids >= INGEST_SENSE_MIN, else 'legacy' (lost migration)."""
    m = SENSE_RE.match(sense_id)
    return 'ingest' if m and int(m.group(2)) >= INGEST_SENSE_MIN else 'legacy'


def parse_lexicon():
    """Return (lemma_ids, sense_ids, orth_by_lemma, pos_by_lemma,
    lemmas_by_norm_orth, senses_by_lemma)."""
    tree = etree.parse(str(LEXICON))
    lemma_ids = set()
    sense_ids = set()
    orth_by_lemma = {}
    pos_by_lemma = {}
    lemmas_by_norm_orth = defaultdict(set)
    senses_by_lemma = defaultdict(list)
    for entry in tree.iter(f'{TEI_NS}entry'):
        lid = entry.get(f'{XML_NS}id')
        if not lid:
            continue
        lemma_ids.add(lid)
        orth_el = entry.find(f'.//{TEI_NS}form[@type="lemma"]/{TEI_NS}orth')
        if orth_el is None:
            orth_el = entry.find(f'.//{TEI_NS}orth')
        orth = (orth_el.text or '').strip() if orth_el is not None else ''
        if orth:
            orth_by_lemma[lid] = orth
            lemmas_by_norm_orth[normalize_mhg(orth)].add(lid)
        pos_el = entry.find(f'{TEI_NS}gramGrp/{TEI_NS}pos')
        pos_by_lemma[lid] = (pos_el.text or '').strip() if pos_el is not None else ''
        for sense in entry.iter(f'{TEI_NS}sense'):
            sid = sense.get(f'{XML_NS}id')
            if sid:
                sense_ids.add(sid)
                senses_by_lemma[lid].append(sid)
    return (lemma_ids, sense_ids, orth_by_lemma, pos_by_lemma,
            lemmas_by_norm_orth, senses_by_lemma)


def sigle_of(filepath):
    return filepath.name.split('.', 1)[0]


def iter_refs(elem):
    """Yield (kind, lemma_id, sense_id_or_None) for lexicon-targeted refs.

    kind is 'lemmaRef' (from @lemmaRef -> lexicon.xml#lemma_N) or
    'ana' (from @ana -> lexicon.xml#lemma_N_sense_M). Whitespace-separated
    value lists are split. Non-lexicon and internal/external refs are skipped.
    """
    for attr, kind in (('lemmaRef', 'lemmaRef'), ('ana', 'ana')):
        val = elem.get(attr)
        if not val:
            continue
        for token in val.split():
            if '#' not in token:
                continue
            tf, frag = token.split('#', 1)
            if tf != 'lexicon.xml':
                continue
            m = SENSE_RE.match(frag)
            if m:
                yield 'ana', f'lemma_{m.group(1)}', frag
                continue
            m = LEMMA_RE.match(frag)
            if m:
                yield 'lemmaRef', frag, None


def scan_corpus(lemma_ids, sense_ids):
    """Collect corpus evidence per lemma that carries any unresolved ref.

    Returns {lemma_id: record} where record has:
      forms (Counter), pos (Counter), sigles (set), examples (list),
      lemma_ref_count (int, unresolved @lemmaRef refs),
      dangling_senses (Counter of sense_id -> ref count, only unresolved),
      resolved_sense_refs (int, refs whose sense DID resolve — context only).
    """
    base_files = corpus_files()
    records = defaultdict(lambda: {
        'forms': Counter(), 'pos': Counter(), 'sigles': set(),
        'examples': [], 'lemma_ref_count': 0,
        'dangling_senses': Counter(), 'resolved_sense_refs': 0,
    })

    for i, fp in enumerate(base_files):
        if (i + 1) % 150 == 0:
            print(f'  scanned {i + 1}/{len(base_files)} files...', flush=True)
        sigle = sigle_of(fp)
        tree = etree.parse(str(fp))
        for elem in tree.iter():
            if not isinstance(elem.tag, str):
                continue
            for kind, lemma_id, sense_id in iter_refs(elem):
                lemma_dangling = lemma_id not in lemma_ids
                sense_dangling = sense_id is not None and sense_id not in sense_ids
                if not lemma_dangling and not sense_dangling:
                    continue  # fully resolved — ignore
                rec = records[lemma_id]
                rec['sigles'].add(sigle)
                # Corpus evidence (form + POS) — only from <w> carrying text.
                if elem.tag == f'{TEI_NS}w':
                    text = (elem.text or '').strip()
                    if text:
                        rec['forms'][text] += 1
                    posv = elem.get('pos')
                    if posv:
                        rec['pos'][posv] += 1
                    if len(rec['examples']) < MAX_EXAMPLES:
                        wid = elem.get(f'{XML_NS}id') or ''
                        rec['examples'].append({
                            'sigle': sigle, 'xml_id': wid, 'form': text,
                            'pos': posv or '', 'lemmaRef': elem.get('lemmaRef') or '',
                            'ana': elem.get('ana') or '',
                        })
                if kind == 'lemmaRef':
                    rec['lemma_ref_count'] += 1
                elif kind == 'ana':
                    if sense_dangling:
                        rec['dangling_senses'][sense_id] += 1
                    else:
                        rec['resolved_sense_refs'] += 1
    return records, len(base_files)


def classify(records, lemma_ids, orth_by_lemma, pos_by_lemma,
             lemmas_by_norm_orth, senses_by_lemma):
    """Turn raw corpus records into classified, sorted worklist rows."""
    rows = []
    for lemma_id, rec in records.items():
        lemma_exists = lemma_id in lemma_ids
        forms = rec['forms']
        dominant_form = forms.most_common(1)[0][0] if forms else ''
        dominant_pos = rec['pos'].most_common(1)[0][0] if rec['pos'] else ''
        corpus_pos_set = {p for v in rec['pos'] for p in v.split()}
        total_refs = (rec['lemma_ref_count']
                      + sum(rec['dangling_senses'].values()))

        # Typo overlay: does the dominant corpus form (normalised) exist as an
        # orth under a DIFFERENT, existing lemma id? POS agreement separates a
        # likely typo/duplicate from a homograph (same spelling, other word
        # class -> a genuine new lemma, NOT a typo).
        typo_targets = []
        pos_match = False
        if dominant_form:
            norm = normalize_mhg(dominant_form)
            cand = lemmas_by_norm_orth.get(norm, set()) - {lemma_id}
            for cid in sorted(cand):
                tpos = pos_by_lemma.get(cid, '')
                agree = bool(corpus_pos_set & set(tpos.split())) if tpos else False
                pos_match = pos_match or agree
                typo_targets.append({'lemma_id': cid,
                                     'orth': orth_by_lemma.get(cid, ''),
                                     'pos': tpos, 'pos_match': agree})

        if not lemma_exists:
            category = 'C_TYPO_SUSPECT' if typo_targets else 'A_MISSING_ENTRY'
        else:
            category = 'B_MISSING_SENSE'

        # Drift-source split of this lemma's dangling senses.
        src = Counter(sense_source(s) for s in rec['dangling_senses'])

        rows.append({
            'lemma_id': lemma_id,
            'lemma_id_num': int(lemma_id.split('_')[1]),
            'category': category,
            'lemma_exists': lemma_exists,
            'ingest_range': int(lemma_id.split('_')[1]) >= INGEST_LEMMA_MIN,
            'total_unresolved_refs': total_refs,
            'lemma_ref_count': rec['lemma_ref_count'],
            'dangling_senses': dict(sorted(rec['dangling_senses'].items(),
                                           key=lambda kv: -kv[1])),
            'sense_source': dict(src),
            'resolved_sense_refs': rec['resolved_sense_refs'],
            'existing_senses': senses_by_lemma.get(lemma_id, []),
            'existing_orth': orth_by_lemma.get(lemma_id, ''),
            'candidate_orth': dominant_form,
            'candidate_pos': dominant_pos,
            'distinct_forms': dict(forms.most_common(8)),
            'sigles': sorted(rec['sigles']),
            'typo_targets': typo_targets,
            'typo_pos_match': pos_match,  # True = likely typo; False = homograph
            'examples': rec['examples'],
        })
    # Sort: category (A, B, C), then by ref weight desc.
    cat_order = {'A_MISSING_ENTRY': 0, 'B_MISSING_SENSE': 1, 'C_TYPO_SUSPECT': 2}
    rows.sort(key=lambda r: (cat_order[r['category']], -r['total_unresolved_refs'],
                             r['lemma_id_num']))
    return rows


def build_stub(row):
    """Return a proposed <entry> XML string for an A-category lemma."""
    orth = row['candidate_orth'] or '???'
    pos = (row['candidate_pos'] or '???').split()[0]  # first POS if multi-valued
    senses = list(row['dangling_senses'].keys())
    lines = [f'  <entry xml:id="{row["lemma_id"]}">',
             f'    <form type="lemma"><orth>{orth}</orth></form>',
             f'    <gramGrp><pos>{pos}</pos></gramGrp>']
    if senses:
        for sid in senses:
            # Empty sense = referential integrity restored, concept curatorial.
            lines.append(f'    <sense xml:id="{sid}"/>  <!-- TODO concept ptr -->')
    else:
        # Corpus referenced lemma via @lemmaRef only — needs a fresh sense id.
        lines.append('    <!-- TODO: corpus uses @lemmaRef only; assign a new sense id -->')
        lines.append(f'    <sense xml:id="{row["lemma_id"]}_sense_NEW"/>')
    lines.append('  </entry>')
    notes = []
    if row['candidate_pos'] and ' ' in row['candidate_pos']:
        notes.append(f'ambiguous POS in corpus: "{row["candidate_pos"]}"')
    if len(row['distinct_forms']) > 1:
        notes.append('orth is the most frequent inflected form — verify base form')
    prefix = f'  <!-- {row["lemma_id"]}: {row["total_unresolved_refs"]} refs, '
    prefix += f'sigles {",".join(row["sigles"][:6])}'
    if notes:
        prefix += ' | ' + '; '.join(notes)
    prefix += ' -->'
    return prefix + '\n' + '\n'.join(lines)


def write_markdown(rows, totals, corpus_files):
    cat = lambda c: [r for r in rows if r['category'] == c]
    A, B, C = cat('A_MISSING_ENTRY'), cat('B_MISSING_SENSE'), cat('C_TYPO_SUSPECT')
    sense_src = Counter()
    for r in rows:
        for k, v in r['sense_source'].items():
            sense_src[k] += v
    c_typo = [r for r in C if r['typo_pos_match']]
    c_homograph = [r for r in C if not r['typo_pos_match']]
    lines = []
    w = lines.append
    w('# lexicon.xml Backfill — Kuratorische Arbeitsliste (#115 / #44)')
    w('')
    w(f'Stand: {date.today().isoformat()} | Quelle: '
      '`scripts/audit/classify-lexicon-backfill.py` (read-only, disposable)')
    w('')
    w('Erzeugt aus dem aktuellen Korpus-Stand. Der **Korpus führt** '
      '(ADR-015 / CONTRACTS §F): jede hier gelistete Referenz ist eine im '
      'Korpus belegte Annotation, deren Ziel in `lexicon.xml` (noch) fehlt. '
      'Das Skript schreibt `lexicon.xml` **nicht** — Einfügen/Anreichern ist '
      'ein freigegebener Team-Schritt mit anschließendem Index-Rebuild.')
    w('')
    w('## Überblick')
    w('')
    w(f'- **{totals["distinct_lemmas"]}** betroffene Lemmata, '
      f'**{totals["total_refs"]}** unaufgelöste Korpus-Referenzen '
      f'(Scan: {corpus_files} Basis-TEI-Dateien)')
    w(f'- **A — Ganzes `<entry>` fehlt:** {len(A)} Lemmata '
      f'({sum(r["total_unresolved_refs"] for r in A)} refs). Stub aus Korpus '
      'vorschlagbar (Form+POS); Sense→Konzept bleibt kuratorisch.')
    w(f'- **B — Sense fehlt an vorhandenem Lemma:** {len(B)} Lemmata '
      f'({sum(r["total_unresolved_refs"] for r in B)} refs). Rein kuratorisch '
      '(welches Konzept?) oder Korpus-`@ana`-Tippfehler.')
    w(f'- **C — Tippfehler-/Homograph-Verdacht:** {len(C)} Lemmata '
      f'({sum(r["total_unresolved_refs"] for r in C)} refs). Korpus-Form trifft '
      'eine vorhandene Lemma-`<orth>` unter anderer ID. Davon **'
      f'{len(c_typo)} mit POS-Übereinstimmung** (wahrscheinlich Tippfehler/Dublette '
      f'→ Korpus-`@lemmaRef` korrigieren) und **{len(c_homograph)} mit POS-Abweichung** '
      '(wahrscheinlich echter Homograph = neues Lemma, *kein* Tippfehler).')
    w('')
    w('**Drift-Quellen der fehlenden Senses** (ID-Heuristik): '
      f'**{sense_src.get("ingest", 0)}** aus Post-Migrations-Ingest '
      f'(Sense-ID ≥ {INGEST_SENSE_MIN}, z.B. WZB), '
      f'**{sense_src.get("legacy", 0)}** aus dem Alt-Bestand '
      f'(Sense-ID < {INGEST_SENSE_MIN} = bei der Migration verlorenes Ziel, '
      'nicht neu ingestiert). Das trennt „neue Daten" von „geänderten/verlorenen Daten".')
    w('')

    def lemma_block(r):
        w(f'### `{r["lemma_id"]}` — {r["total_unresolved_refs"]} refs')
        w('')
        ex_forms = ', '.join(f'`{f}`×{c}' for f, c in list(r['distinct_forms'].items())[:8])
        w(f'- Korpus-Formen: {ex_forms or "—"}')
        w(f'- POS: `{r["candidate_pos"] or "—"}` | Sigles ({len(r["sigles"])}): '
          f'{", ".join(r["sigles"][:12])}{" …" if len(r["sigles"]) > 12 else ""}')
        if r['category'] == 'B_MISSING_SENSE':
            w(f'- Vorhandenes Lemma: `<orth>{r["existing_orth"]}</orth>` mit '
              f'{len(r["existing_senses"])} vorhandenen Senses '
              f'({", ".join(s.split("_sense_")[-1] for s in r["existing_senses"][:10])})')
            w(f'- **Fehlende Senses:** '
              + ', '.join(f'`{s}`×{c}' for s, c in r['dangling_senses'].items()))
        elif r['category'] == 'C_TYPO_SUSPECT':
            tg = '; '.join(f'`{t["lemma_id"]}` (`{t["orth"]}`, POS `{t["pos"]}`'
                           f'{", **POS=**" if t["pos_match"] else ", **POS≠**"})'
                           for t in r['typo_targets'])
            if r['typo_pos_match']:
                w(f'- **Tippfehler-/Dublettenverdacht (POS stimmt):** Form trifft '
                  f'{tg} — Korpus-`@lemmaRef`/`@ana` auf vorhandene ID korrigieren prüfen')
            else:
                w(f'- **Homograph-Verdacht (POS weicht ab):** gleiche Schreibung wie '
                  f'{tg}, aber andere Wortart → wahrscheinlich **echtes neues Lemma**, '
                  'kein Tippfehler. Wie Kategorie A behandeln (Stub), Querverweis prüfen.')
            if r['dangling_senses']:
                w(f'- Mit-betroffene Senses: '
                  + ', '.join(f'`{s}`' for s in r['dangling_senses']))
        else:  # A
            w(f'- Stub-Vorschlag-`<orth>`: `{r["candidate_orth"]}` '
              f'(häufigste Form) | fehlende Senses: '
              + (', '.join(f'`{s}`' for s in r['dangling_senses']) or '— (nur @lemmaRef)'))
        if r['examples']:
            ex = r['examples'][0]
            w(f'- Beleg: `{ex["sigle"]}` `{ex["xml_id"]}` → `{ex["form"]}` '
              f'(`@pos={ex["pos"]}`)')
        w('')

    for title, group in (('A — Ganzes `<entry>` fehlt', A),
                         ('B — Sense fehlt an vorhandenem Lemma', B),
                         ('C — Tippfehler-/Homograph-Verdacht', C)):
        w(f'## {title}')
        w('')
        if not group:
            w('_(keine)_')
            w('')
            continue
        for r in group:
            lemma_block(r)
    MD_OUT.write_text('\n'.join(lines), encoding='utf-8')


def write_stubs(rows):
    A = [r for r in rows if r['category'] == 'A_MISSING_ENTRY']
    lines = ['<!-- Proposed lexicon.xml <entry> stubs for #115 backfill (category A).',
             '     REVIEW REQUIRED before insertion — orth may be an inflected form,',
             '     POS may be ambiguous, and every <sense> still needs concept ptrs.',
             '     This file is a disposable work product, not committed. -->',
             '']
    for r in A:
        lines.append(build_stub(r))
        lines.append('')
    STUBS_OUT.write_text('\n'.join(lines), encoding='utf-8')


def main():
    if not LEXICON.exists() or not TEI_DIR.exists():
        print('Error: run from repo root (tei/ and authority-files/lexicon.xml required)')
        return 1

    print(f'Parsing {LEXICON.name} ...')
    (lemma_ids, sense_ids, orth_by_lemma, pos_by_lemma,
     lemmas_by_norm_orth, senses_by_lemma) = parse_lexicon()
    print(f'  {len(lemma_ids):,} lemma entries, {len(sense_ids):,} senses')

    print(f'Scanning corpus in {TEI_DIR} ...')
    records, corpus_files = scan_corpus(lemma_ids, sense_ids)
    print(f'  {len(records)} lemmas carry at least one unresolved ref')

    rows = classify(records, lemma_ids, orth_by_lemma, pos_by_lemma,
                    lemmas_by_norm_orth, senses_by_lemma)

    by_cat = Counter(r['category'] for r in rows)
    total_refs = sum(r['total_unresolved_refs'] for r in rows)
    # Drift-source split across all dangling senses.
    sense_src = Counter()
    for r in rows:
        for k, v in r['sense_source'].items():
            sense_src[k] += v
    typo_likely = sum(1 for r in rows
                      if r['category'] == 'C_TYPO_SUSPECT' and r['typo_pos_match'])
    homograph = sum(1 for r in rows
                    if r['category'] == 'C_TYPO_SUSPECT' and not r['typo_pos_match'])
    totals = {'distinct_lemmas': len(rows), 'total_refs': total_refs}

    report = {
        'meta': {
            'date': date.today().isoformat(),
            'script': 'scripts/audit/classify-lexicon-backfill.py',
            'issue': 115,
            'corpus_files_scanned': corpus_files,
            'lexicon_entries': len(lemma_ids),
            'lexicon_senses': len(sense_ids),
        },
        'summary': {
            'distinct_lemmas': len(rows),
            'total_unresolved_refs': total_refs,
            'by_category': dict(by_cat),
            'ingest_range_lemmas': sum(1 for r in rows if r['ingest_range']),
            'dangling_sense_source': dict(sense_src),
            'typo_likely_lemmas': typo_likely,
            'homograph_suspect_lemmas': homograph,
        },
        'rows': rows,
    }
    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    write_markdown(rows, totals, corpus_files)
    write_stubs(rows)

    # ---- console summary ----
    print('=' * 64)
    print('lexicon.xml Backfill Classification (#115 / #44)')
    print('=' * 64)
    print(f'Distinct affected lemmas:   {len(rows):>8}')
    print(f'Total unresolved refs:      {total_refs:>8}')
    print(f'  lemma ids >= {INGEST_LEMMA_MIN} (ingest):{sum(1 for r in rows if r["ingest_range"]):>8}')
    print(f'Dangling senses by source:  ingest={sense_src.get("ingest", 0)}  '
          f'legacy(lost migration)={sense_src.get("legacy", 0)}')
    print()
    print('By category:')
    labels = {'A_MISSING_ENTRY': 'A  whole <entry> missing  (stub proposable)',
              'B_MISSING_SENSE': 'B  sense missing, lemma exists (curatorial)',
              'C_TYPO_SUSPECT':  'C  typo/homograph suspect (corpus fix cand.)'}
    for c in ('A_MISSING_ENTRY', 'B_MISSING_SENSE', 'C_TYPO_SUSPECT'):
        refs = sum(r['total_unresolved_refs'] for r in rows if r['category'] == c)
        print(f'  {labels[c]:48} {by_cat.get(c, 0):>4} lemmas / {refs:>4} refs')
    print(f'    (C splits: {typo_likely} likely typo/dupe [POS match], '
          f'{homograph} homograph [POS mismatch -> probably new lemma])')
    print()
    print(f'Worklist:  {MD_OUT}')
    print(f'Stubs (A): {STUBS_OUT}')
    print(f'JSON:      {JSON_OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
