#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Split a TSV file into smaller chunk files with a fixed number of rows.

Useful for feeding the disambiguation TSV to Claude in manageable batches.

Usage:
    python scripts/wzb-split-tsv.py [--input path] [--size N]

Produces files named `<basename>-partNN.tsv` in the same directory as
`input`.
"""

import csv
from pathlib import Path
import argparse
import sys

# ensure UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Split TSV into chunks')
    parser.add_argument('--input', '-i', help='input TSV file',
                        default='Wenzelsbibel/wzb-disambiguation.tsv')
    parser.add_argument('--size', '-s', type=int, help='rows per chunk',
                        default=50)
    args = parser.parse_args()

    in_path = Path(args.input)
    if not in_path.exists():
        print(f"ERROR: input file not found: {in_path}")
        sys.exit(1)

    base = in_path.stem
    directory = in_path.parent

    with in_path.open(encoding='utf-8') as inf:
        reader = csv.reader(inf, delimiter='\t')
        header = next(reader)

        part = 1
        out_file = directory / f"{base}-part{part:02d}.tsv"
        outf = out_file.open('w', encoding='utf-8', newline='')
        writer = csv.writer(outf, delimiter='\t')
        writer.writerow(header)
        row_count = 0

        for row in reader:
            if row_count >= args.size:
                outf.close()
                part += 1
                row_count = 0
                out_file = directory / f"{base}-part{part:02d}.tsv"
                outf = out_file.open('w', encoding='utf-8', newline='')
                writer = csv.writer(outf, delimiter='\t')
                writer.writerow(header)
            writer.writerow(row)
            row_count += 1

        outf.close()

    print(f"Split into {part} parts of up to {args.size} rows each")
