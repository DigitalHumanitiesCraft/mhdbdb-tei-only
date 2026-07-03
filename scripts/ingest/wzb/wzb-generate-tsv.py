#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generate Phase 1b TSV template from the auto-match report.

The resulting file (`Wenzelsbibel/wzb-disambiguation.tsv`) contains all
ambiguous and unmatched rows with empty columns for the human/LLM to fill
(`resolved_lemma`, `confidence`, `reviewer`).

Usage:
    python scripts/wzb-generate-tsv.py
"""

import csv
from pathlib import Path
import sys

# ensure UTF-8 output for Windows consoles
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
REPORT_CSV = PROJECT_ROOT / 'Wenzelsbibel' / 'reports' / 'wzb-auto-match-report.csv'
OUTPUT_TSV = PROJECT_ROOT / 'Wenzelsbibel' / 'phase1b' / 'wzb-disambiguation.tsv'

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Generate Phase1b TSV from auto-match CSV')
    parser.add_argument('--report', help='path to auto-match CSV', default=str(REPORT_CSV))
    parser.add_argument('--output', help='TSV output path', default=str(OUTPUT_TSV))
    args = parser.parse_args()

    report_path = Path(args.report)
    out_path = Path(args.output)
    if not report_path.exists():
        print(f"ERROR: report file not found: {report_path}")
        sys.exit(1)

    matched=amb=unm=0
    with report_path.open(encoding='utf-8') as inf, \
         out_path.open('w', encoding='utf-8', newline='') as outf:
        reader = csv.DictReader(inf)
        fieldnames = ['xml_id','form','count','context','match_type','candidate_lemmas',
                      'resolved_lemma','confidence','reviewer']
        writer = csv.DictWriter(outf, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        for row in reader:
            mtype = row.get('match_type','')
            if mtype == 'matched':
                matched += 1
            if mtype in ('ambiguous','unmatched'):
                if mtype == 'ambiguous':
                    amb += 1
                else:
                    unm += 1
                writer.writerow({
                    'xml_id': row['xml_id'],
                    'form': row['form'],
                    'count': row.get('count','1'),
                    'context': row.get('context',''),
                    'match_type': mtype,
                    'candidate_lemmas': row.get('lemma_ids',''),
                    'resolved_lemma': '',
                    'confidence': '',
                    'reviewer': '',
                })
    print(f"TSV template written to {out_path}")
    total = matched+amb+unm
    print(f"Report contained {total} words ({matched} matched, {amb} ambiguous, {unm} unmatched)")
