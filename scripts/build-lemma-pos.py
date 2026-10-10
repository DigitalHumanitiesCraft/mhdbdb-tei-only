#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Baut data/lemma-pos.json.gz: je Lemma, wie oft jeder Teil-Tag im Korpus vorkommt (#462).

Quelle fuer lemma.pos und lemma.posAll in build-authority-index.py. Der
Authority-Build liest tei/ nicht (G1, 02.10.2026, und G3, 10.10.2026), deshalb
steht die Zaehlung in einer eigenen kleinen Datei, die dieses Skript aus tei/
ableitet und der Authority-Build wie corpus-index.json.gz liest. Reihenfolge im
Lifecycle: dieses Skript, dann build-authority-index.py (der Korpus-Index ist
davon unabhaengig).

Format: ein JSON-Objekt, Schluessel lemma-ID, Wert ein Objekt Teil-Tag -> Anzahl.
    {"lemma_1": {"NOM": 12, "VRB": 1}, ...}

Zaehlregel (wie in der Vorab-Messung zu #462 vom 10.10.2026):
- Es zaehlt jedes <w> im <body> mit @lemmaRef und nichtleerem @pos.
- Ein Token mit mehreren Lemmata in @lemmaRef zaehlt bei jedem.
- Kompositum-Tags (POS-TAGSET.md, Abschnitt 2) werden in ihre Teile zerlegt;
  jeder verschiedene Teil zaehlt je Token einmal.
- Ein Token ohne @pos oder mit leerem @pos zaehlt nirgends.

Deterministisch (#125): sortierte Dateiliste, sortierte Schluessel, gzip ohne
mtime. Der Wert von --jobs aendert das Ergebnis nicht.

Usage:
    python scripts/build-lemma-pos.py            # baut data/lemma-pos.json.gz
    python scripts/build-lemma-pos.py --check    # baut im Speicher, vergleicht mit der
                                                 # committeten Datei, Exit 1 bei Abweichung
"""

import argparse
import concurrent.futures
import gzip
import json
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from corpus_files import PROJECT_ROOT, corpus_files, default_jobs  # noqa: E402

OUTPUT_FILE = PROJECT_ROOT / 'data' / 'lemma-pos.json.gz'

W_TAG = re.compile(r'<w\s[^>]*>')
LEMMA_REF = re.compile(r'\blemmaRef="([^"]*)"')
POS = re.compile(r'\bpos="([^"]*)"')
LEMMA_ID = re.compile(r'#(lemma_\d+)$')


def count_file(path):
    """Teil-Tag-Zaehlung je Lemma fuer eine Korpusdatei, als reines dict (prozessgrenzentauglich)."""
    text = Path(path).read_text(encoding='utf-8')
    start = text.find('<body')
    if start < 0:
        raise ValueError(f'{path}: kein <body> gefunden')
    out = defaultdict(Counter)
    for m in W_TAG.finditer(text, start):
        tag = m.group(0)
        ref = LEMMA_REF.search(tag)
        if not ref:
            continue
        pos = POS.search(tag)
        parts = set(pos.group(1).split()) if pos else set()
        if not parts:
            continue
        for token in ref.group(1).split():
            lid = LEMMA_ID.search(token)
            if not lid:
                raise ValueError(f'{path}: unbekannter @lemmaRef-Wert {token!r}')
            for part in parts:
                out[lid.group(1)][part] += 1
    return {lemma: dict(counts) for lemma, counts in out.items()}


def iter_counts(files, jobs):
    if jobs <= 1:
        yield from map(count_file, files)
        return
    with concurrent.futures.ProcessPoolExecutor(max_workers=jobs) as pool:
        yield from pool.map(count_file, files, chunksize=1)


def build(jobs):
    files = corpus_files()
    if not files:
        sys.exit('❌ ERROR: keine TEI-Dateien gefunden')
    total = defaultdict(Counter)
    start = time.time()
    for per_file in iter_counts(files, jobs):
        for lemma, counts in per_file.items():
            total[lemma].update(counts)
    print(f'   {len(files)} Dateien in {time.time() - start:.1f} s ({jobs} Prozess(e))')
    return {lemma: {tag: total[lemma][tag] for tag in sorted(total[lemma])}
            for lemma in sorted(total)}


def serialize(data):
    return json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')


def main():
    parser = argparse.ArgumentParser(description='Baut data/lemma-pos.json.gz aus tei/')
    parser.add_argument('--check', action='store_true',
                        help='nichts schreiben; Exit 1, wenn die committete Datei nicht zum Korpus passt')
    parser.add_argument('--jobs', type=int, default=default_jobs(),
                        help='Worker-Prozesse (1 = sequentiell); das Ergebnis haengt nicht davon ab')
    args = parser.parse_args()
    if args.jobs < 1:
        parser.error('--jobs muss mindestens 1 sein')

    print('Lemma-POS-Zaehlung aus tei/')
    data = build(args.jobs)
    fresh = serialize(data)
    n_tokens = sum(sum(c.values()) for c in data.values())
    print(f'   {len(data):,} Lemmata, {n_tokens:,} Teil-Tag-Zaehlungen')

    if args.check:
        if not OUTPUT_FILE.exists():
            print(f'::error file=data/lemma-pos.json.gz::{OUTPUT_FILE.name} fehlt. '
                  'Lokal python scripts/build-lemma-pos.py ausfuehren und mitcommitten.')
            return 1
        with gzip.open(OUTPUT_FILE, 'rb') as f:
            committed = f.read()
        if committed == fresh:
            print('data/lemma-pos.json.gz: OK (Neuaufbau byte-identisch nach Dekompression)')
            return 0
        print('::error file=data/lemma-pos.json.gz::lemma-pos.json.gz ist nicht mit dem Korpus synchron '
              '(DATA-MODEL.md -> Data-Change-Lifecycle). Lokal python scripts/build-lemma-pos.py '
              'ausfuehren, danach build-authority-index.py, und mitcommitten.')
        return 1

    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with gzip.GzipFile(OUTPUT_FILE, mode='wb', mtime=0) as f:
        f.write(fresh)
    print(f'   geschrieben: {OUTPUT_FILE} ({OUTPUT_FILE.stat().st_size / 1024:.0f} KB gz, '
          f'{len(fresh) / 1024:.0f} KB roh)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
