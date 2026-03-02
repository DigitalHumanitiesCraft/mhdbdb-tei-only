#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extract unmatched word forms from auto-match report for editorial review.

Produces a TSV file (`Wenzelsbibel/wzb-unmatched-forms.tsv`) containing
unique forms that had no variant match, along with a sample context and
frequency count.  This helps lexicon editors identify gaps.

Usage:
    python scripts/wzb-extract-unmatched.py
"""

import csv
from pathlib import Path
from collections import Counter, defaultdict
import sys

# ensure UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

PROJECT_ROOT = Path(__file__).parent.parent
REPORT_CSV = PROJECT_ROOT / 'Wenzelsbibel' / 'wzb-auto-match-report.csv'
OUTPUT_TSV = PROJECT_ROOT / 'Wenzelsbibel' / 'wzb-unmatched-forms.tsv'

if __name__ == '__main__':
    if not REPORT_CSV.exists():
        print(f"ERROR: missing report file {REPORT_CSV}")
        sys.exit(1)

    counter = Counter()
    contexts = defaultdict(lambda: [])
    with REPORT_CSV.open(encoding='utf-8') as inf:
        reader = csv.DictReader(inf)
        for row in reader:
            if row.get('match_type') == 'unmatched':
                form = row['form']
                counter[form] += 1
                if len(contexts[form]) < 3:
                    contexts[form].append(row.get('context',''))

    with OUTPUT_TSV.open('w', encoding='utf-8', newline='') as outf:
        writer = csv.writer(outf, delimiter='\t')
        writer.writerow(['form','count','sample_contexts'])
        for form, cnt in counter.most_common():
            samples = ' || '.join(contexts[form])
            writer.writerow([form, cnt, samples])
    print(f"Unmatched forms list written to {OUTPUT_TSV} ({len(counter)} unique forms)")
