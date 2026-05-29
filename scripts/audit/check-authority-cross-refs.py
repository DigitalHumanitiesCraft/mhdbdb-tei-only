#!/usr/bin/env python3
"""
Authority Cross-Reference Integrity Audit (Issue #115, Phase 1)

Scans all base TEI corpus files (tei/*.tei.xml, excluding *.disamb.tei.xml) for
cross-references into the authority files and reports *unresolved* targets, i.e.
references that point at an xml:id which does not exist in the target file.

Reference attributes scanned (on any element):
  @lemmaRef  -> lexicon.xml#lemma_N
  @ana       -> lexicon.xml#lemma_N_sense_M
  @corresp   -> variants.xml#type_N   (legacy @wordRef target, migrated in #32)
  @ref       -> persons.xml#person_N, works.xml#work_N, ...
  @target    -> any authority target

Out of scope: internal refs (#fragment without a file part) and external URIs
(http...). The authority->authority direction is covered by
`audit-authority-files.py` (and was clean as of 2026-05-28).

Output:
  scripts/audit/authority-cross-refs-audit.json   (machine-readable, Phase-2 cleanup input)
  console summary

This is a read-only, idempotent diagnostic. The JSON report is a disposable
artifact and should not be committed.

Usage:
    python scripts/audit/check-authority-cross-refs.py
"""

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from lxml import etree

XML_NS = '{http://www.w3.org/XML/1998/namespace}'

# Reference-bearing attributes to scan, in priority order.
REF_ATTRS = ('lemmaRef', 'ana', 'corresp', 'ref', 'target')

# Authority files live here; we resolve fragments against their xml:id sets.
AUTHORITY_DIR = Path('authority-files')
TEI_DIR = Path('tei')
SCRIPT_DIR = Path(__file__).resolve().parent
JSON_OUT = SCRIPT_DIR / 'authority-cross-refs-audit.json'

NEG_TYPE_RE = re.compile(r'^type_-\d+$')
LEMMA_RE = re.compile(r'^lemma_\d+$')
SENSE_RE = re.compile(r'^lemma_\d+_sense_\d+$')


def collect_ids(filepath):
    """Return the set of all xml:id values in an XML file."""
    ids = set()
    tree = etree.parse(str(filepath))
    for elem in tree.iter():
        if not isinstance(elem.tag, str):
            continue
        xid = elem.get(f'{XML_NS}id')
        if xid:
            ids.add(xid)
    return ids


def sigle_of(filepath):
    """ABG.tei.xml -> ABG"""
    return filepath.name.split('.', 1)[0]


def build_authority_ids():
    """filename -> set of xml:id for every authority file."""
    auth_ids = {}
    for f in sorted(AUTHORITY_DIR.glob('*.xml')):
        ids = collect_ids(f)
        auth_ids[f.name] = ids
        print(f'  {f.name:20} {len(ids):>9,} ids')
    return auth_ids


def iter_refs(elem):
    """Yield (attribute, target_file, fragment) for authority-targeted refs.

    Splits whitespace-separated value lists (@ana/@corresp may carry several).
    Skips internal (#frag) and external (http...) references.
    """
    for attr in REF_ATTRS:
        val = elem.get(attr)
        if not val:
            continue
        for token in val.split():
            if '#' not in token:
                continue
            target_file, fragment = token.split('#', 1)
            if not target_file or not target_file.endswith('.xml'):
                continue  # internal or non-authority target
            yield attr, target_file, fragment


def main():
    if not TEI_DIR.exists() or not AUTHORITY_DIR.exists():
        print('Error: run from repo root (tei/ and authority-files/ required)')
        return 1

    print('Building authority id-sets...')
    auth_ids = build_authority_ids()

    base_files = sorted(f for f in TEI_DIR.glob('*.tei.xml') if '.disamb.' not in f.name)
    print(f'\nScanning {len(base_files)} base corpus files...')

    total_scanned = 0
    total_unresolved = 0

    by_target = Counter()                     # target_file -> unresolved count
    by_attr = Counter()                       # attribute -> unresolved count
    distinct = defaultdict(lambda: {'count': 0, 'sigles': set()})  # (tf, frag) -> ...
    per_sigle = defaultdict(lambda: {'unresolved': 0, 'ids': Counter(), 'by_target': Counter()})
    missing_target_files = Counter()          # referenced .xml that we do not have

    for i, fp in enumerate(base_files):
        if (i + 1) % 100 == 0:
            print(f'  {i + 1}/{len(base_files)}...', flush=True)
        sigle = sigle_of(fp)
        tree = etree.parse(str(fp))
        for elem in tree.iter():
            if not isinstance(elem.tag, str):
                continue
            for attr, tf, frag in iter_refs(elem):
                total_scanned += 1
                known_file = tf in auth_ids
                if not known_file:
                    missing_target_files[tf] += 1
                resolved = known_file and frag in auth_ids[tf]
                if resolved:
                    continue
                # --- unresolved ---
                total_unresolved += 1
                by_target[tf] += 1
                by_attr[attr] += 1
                d = distinct[(tf, frag)]
                d['count'] += 1
                d['sigles'].add(sigle)
                ps = per_sigle[sigle]
                ps['unresolved'] += 1
                ps['ids'][f'{tf}#{frag}'] += 1
                ps['by_target'][tf] += 1

    print(f'  done. {total_scanned:,} authority-targeted refs scanned.\n')

    # ---- categorise distinct unresolved ----
    distinct_pairs = [(tf, frag, info['count'], sorted(info['sigles']))
                      for (tf, frag), info in distinct.items()]
    distinct_pairs.sort(key=lambda x: (-x[2], x[0], x[1]))

    by_target_distinct = Counter()
    for tf, frag, cnt, sigles in distinct_pairs:
        by_target_distinct[tf] += 1

    # Negative type-IDs (variants.xml placeholders, the chsteiner question)
    neg_type = {}
    for tf, frag, cnt, sigles in distinct_pairs:
        if tf == 'variants.xml' and NEG_TYPE_RE.match(frag):
            neg_type[frag] = {'count': cnt, 'sigle_count': len(sigles)}

    # lexicon split: lemma corpses vs sense corpses
    lex_lemma = {}
    lex_sense = {}
    lex_other = {}
    for tf, frag, cnt, sigles in distinct_pairs:
        if tf != 'lexicon.xml':
            continue
        rec = {'count': cnt, 'sigles': sigles}
        if SENSE_RE.match(frag):
            lex_sense[frag] = rec
        elif LEMMA_RE.match(frag):
            lex_lemma[frag] = rec
        else:
            lex_other[frag] = rec

    neg_type_total = sum(v['count'] for v in neg_type.values())

    # ---- per-sigle top list ----
    sigle_rows = sorted(per_sigle.items(), key=lambda kv: -kv[1]['unresolved'])
    by_sigle_top = {}
    for sigle, info in sigle_rows[:40]:
        by_sigle_top[sigle] = {
            'unresolved': info['unresolved'],
            'by_target': dict(info['by_target']),
            'top_ids': dict(info['ids'].most_common(10)),
        }
    by_sigle_counts = {s: info['unresolved'] for s, info in sigle_rows}

    pct = (total_unresolved / total_scanned * 100) if total_scanned else 0.0

    report = {
        'meta': {
            'date': date.today().isoformat(),
            'script': 'scripts/audit/check-authority-cross-refs.py',
            'issue': 115,
            'corpus_files_scanned': len(base_files),
            'ref_attributes': list(REF_ATTRS),
        },
        'summary': {
            'total_refs_scanned': total_scanned,
            'total_unresolved': total_unresolved,
            'unresolved_pct': round(pct, 2),
            'distinct_unresolved_pairs': len(distinct_pairs),
        },
        'by_target_file': {
            tf: {'unresolved_refs': by_target[tf], 'distinct_ids': by_target_distinct[tf]}
            for tf in sorted(by_target, key=lambda t: -by_target[t])
        },
        'by_attribute': dict(by_attr.most_common()),
        'missing_target_files': dict(missing_target_files.most_common()),
        'negative_type_ids': {
            'distinct': len(neg_type),
            'total_refs': neg_type_total,
            'by_id': dict(sorted(neg_type.items(), key=lambda kv: -kv[1]['count'])),
        },
        'lexicon_corpses': {
            'lemma_ids': {'distinct': len(lex_lemma), 'refs': sum(r['count'] for r in lex_lemma.values())},
            'sense_ids': {'distinct': len(lex_sense), 'refs': sum(r['count'] for r in lex_sense.values())},
            'other': {'distinct': len(lex_other), 'refs': sum(r['count'] for r in lex_other.values())},
            'lemma_detail': dict(sorted(lex_lemma.items(), key=lambda kv: -kv[1]['count'])),
            'sense_detail': dict(sorted(lex_sense.items(), key=lambda kv: -kv[1]['count'])),
            'other_detail': lex_other,
        },
        'top_unresolved_ids': [
            {'target': tf, 'id': frag, 'refs': cnt, 'sigle_count': len(sigles)}
            for tf, frag, cnt, sigles in distinct_pairs[:100]
        ],
        'by_sigle_top40': by_sigle_top,
        'by_sigle_counts': by_sigle_counts,
        # Full distinct list for Phase-2 cleanup (target, id, ref-count, sigles).
        'distinct_unresolved': [
            {'target': tf, 'id': frag, 'refs': cnt, 'sigles': sigles}
            for tf, frag, cnt, sigles in distinct_pairs
        ],
    }

    with open(JSON_OUT, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # ---- console summary ----
    print('=' * 60)
    print('Authority Cross-Reference Integrity Audit (#115)')
    print('=' * 60)
    print(f'Refs scanned:            {total_scanned:>12,}')
    print(f'Unresolved:              {total_unresolved:>12,}  ({pct:.2f} %)')
    print(f'Distinct (target, id):   {len(distinct_pairs):>12,}')
    print()
    print('By target file (unresolved refs / distinct ids):')
    for tf, info in report['by_target_file'].items():
        print(f'  {tf:20} {info["unresolved_refs"]:>10,} / {info["distinct_ids"]:>7,}')
    if missing_target_files:
        print('\nReferenced files NOT present in authority-files/:')
        for tf, c in missing_target_files.most_common():
            print(f'  {tf:20} {c:>10,}')
    print('\nBy attribute (unresolved):')
    for attr, c in by_attr.most_common():
        print(f'  @{attr:18} {c:>10,}')
    print(f'\nNegative type-IDs (variants.xml): {len(neg_type)} distinct, {neg_type_total:,} refs')
    for frag, info in list(report['negative_type_ids']['by_id'].items())[:8]:
        print(f'  {frag:16} {info["count"]:>9,} refs  ({info["sigle_count"]} sigles)')
    lc = report['lexicon_corpses']
    print(f'\nlexicon.xml corpses: '
          f'{lc["lemma_ids"]["distinct"]} lemma-ids ({lc["lemma_ids"]["refs"]:,} refs), '
          f'{lc["sense_ids"]["distinct"]} sense-ids ({lc["sense_ids"]["refs"]:,} refs), '
          f'{lc["other"]["distinct"]} other')
    print(f'\nTop unresolved sigles:')
    for sigle, info in sigle_rows[:8]:
        print(f'  {sigle:8} {info["unresolved"]:>10,}')
    print(f'\nReport written: {JSON_OUT}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
