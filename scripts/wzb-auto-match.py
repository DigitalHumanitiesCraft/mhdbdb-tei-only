#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Auto-match lemmata for Wenzelsbibel TEI file using the existing
MHDBDB lexicon/variants index.

Produces two artifacts:
  * annotated TEI file (adds @lemmaRef attributes for unambiguous
    matches)
  * CSV report (matched/unmatched/ambiguous forms with context)

Usage: python scripts/wzb-auto-match.py

This is Phase 1 of the WZB annotation pipeline (see
`docs/features/034-wenzelsbibel-annotation.md` for background).

The script normalizes every word form using `mhg_normalizer.normalize_mhg`
so that matching behaviour is identical to the web application.
"""

import sys
import csv
from pathlib import Path
from collections import defaultdict

# force UTF-8 output (matches mhg_normalizer behavior)
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# third-party
try:
    from lxml import etree
except ImportError:
    print("❌ Please install lxml: pip install lxml")
    sys.exit(1)

# local utilities
sys.path.insert(0, str(Path(__file__).parent))
from mhg_normalizer import normalize_mhg

# default paths relative to project root
PROJECT_ROOT = Path(__file__).parent.parent
VARIANTS_FILE = PROJECT_ROOT / 'authority-files' / 'variants.xml'
LEXICON_FILE = PROJECT_ROOT / 'authority-files' / 'lexicon.xml'  # may not be used here
DEFAULT_WZB_FILE = PROJECT_ROOT / 'Wenzelsbibel' / 'WZB.tei.xml'
DEFAULT_OUTPUT_TEI = PROJECT_ROOT / 'Wenzelsbibel' / 'WZB.lemma-autofill.tei.xml'
DEFAULT_REPORT_CSV = PROJECT_ROOT / 'Wenzelsbibel' / 'wzb-auto-match-report.csv'

# TEI namespace
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


def get_namespaces(tree):
    nsmap = tree.getroot().nsmap.copy()
    if None in nsmap:
        nsmap['tei'] = nsmap[None]
        del nsmap[None]
    if 'tei' not in nsmap:
        nsmap['tei'] = TEI_NS['tei']
    return nsmap


def build_variant_lookup(variants_path):
    """Return dict(normalized_form -> set(lemma_id))."""
    lookup = defaultdict(set)

    tree = etree.parse(str(variants_path))
    ns = get_namespaces(tree)

    for entry in tree.xpath('//tei:entry', namespaces=ns):
        corresp = entry.get('corresp', '')
        # corresp should be something like 'lexicon.xml#lemma_123'
        lemma_id = corresp.split('#')[-1] if corresp else None
        if not lemma_id:
            continue

        for form in entry.xpath('./tei:form', namespaces=ns):
            text = (form.text or '').strip()
            if not text:
                continue
            norm = normalize_mhg(text)
            lookup[norm].add(lemma_id)

    return lookup


def annotate_wzb(variant_lookup, wzb_path, out_path, report_path):
    # parse with recovery mode because the source file may contain invalid
    # xml:id values (e.g. characters not allowed in NCNames).
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(str(wzb_path), parser)
    ns = get_namespaces(tree)

    rows = []
    empty_words = []
    counters = {'matched':0, 'ambiguous':0, 'unmatched':0}
    form_counts = Counter()

    # build list of all w elements so we can compute a context window
    w_elements = tree.xpath('//tei:w', namespaces=ns)
    texts = [(w.get('{http://www.w3.org/XML/1998/namespace}id', ''), (w.text or '').strip()) for w in w_elements]

    # first pass to count forms
    for w in w_elements:
        form_text = (w.text or '').strip()
        if form_text:
            form_counts[form_text] += 1

    for idx, w in enumerate(w_elements):
        xml_id = w.get('{http://www.w3.org/XML/1998/namespace}id', '')
        form = (w.text or '').strip()
        if not form:
            empty_words.append(xml_id)
            continue

        # compute 5-word window (2 before + current + 2 after)
        start = max(0, idx - 2)
        end = min(len(texts), idx + 3)
        context = ' '.join(t for _, t in texts[start:end])

        norm = normalize_mhg(form)
        candidates = variant_lookup.get(norm, set())

        if len(candidates) == 1:
            lemma = list(candidates)[0]
            w.set('lemmaRef', f'lexicon.xml#{lemma}')
            match_type = 'matched'
        elif len(candidates) > 1:
            match_type = 'ambiguous'
        else:
            match_type = 'unmatched'

        counters[match_type] += 1

        rows.append({
            'xml_id': xml_id,
            'form': form,
            'count': form_counts.get(form, 1),
            'context': context,
            'normalized': norm,
            'match_type': match_type,
            'lemma_ids': '|'.join(sorted(candidates)),
        })

    # write annotated TEI if requested
    if out_path:
        tree.write(str(out_path), encoding='utf-8', xml_declaration=True, pretty_print=True)
        print(f"Annotated TEI written to {out_path}")
    else:
        print("Skipping TEI output (--skip-tei)")

    # write CSV report with frequency column
    fieldnames = ['xml_id', 'form', 'count', 'context', 'normalized', 'match_type', 'lemma_ids']
    with report_path.open('w', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"Report CSV written to {report_path}")

    # summary
    total = sum(counters.values())
    print(f"Summary: {total} words analysed ({counters['matched']} matched, "
          f"{counters['ambiguous']} ambiguous, {counters['unmatched']} unmatched)")

    if empty_words:
        print(f"⚠️  {len(empty_words)} <w> elements had empty text; see below:")
        for eid in empty_words[:20]:
            print(f"    {eid}")
        if len(empty_words) > 20:
            print("    ...")


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Auto-match WZB lemmata")
    parser.add_argument('--tei', help='Path to WZB TEI file', default=str(DEFAULT_WZB_FILE))
    parser.add_argument('--output-tei', help='Annotated TEI output', default=str(DEFAULT_OUTPUT_TEI))
    parser.add_argument('--report', help='CSV report path', default=str(DEFAULT_REPORT_CSV))
    parser.add_argument('--skip-tei', action='store_true', help='Do not write annotated TEI')
    args = parser.parse_args()

    variant_lookup = build_variant_lookup(VARIANTS_FILE)
    print(f"Loaded {len(variant_lookup)} unique normalized forms from variants")

    wzb_path = Path(args.tei)
    out_path = Path(args.output_tei)
    report_path = Path(args.report)

    annotate_wzb(variant_lookup, wzb_path, out_path if not args.skip_tei else None, report_path)
