#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#370 Punkt 2: die Paare, die seit der Arbeitsliste vom 31.08. dazugekommen sind.

offene-faelle.csv stammt vom 31.08.2026 (484 Paare, 5.273 Tokens). Seither hat
der Korpus (#235-Breve-Batch vom 24.09., #387/#418/#464, #459) weitere WZB-Tokens
mit @lemmaRef und ohne @corresp bekommen. Dieses Skript zaehlt die Paare aus
Schreibung und Lemma, die jetzt ohne @corresp sind und nicht in der Arbeitsliste
stehen, und schreibt sie im selben Format nach offene-faelle-nachtrag.csv.

Schluessel wie in #370 Punkt 1: NFC-normalisierte, kleingeschriebene Schreibung
und das erste Lemma aus @lemmaRef.

Nur Lesen. Aufruf aus dem Repo-Wurzelverzeichnis:
    python scripts/review/find-370-nachtrag.py
"""

import csv
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parent.parent.parent
DIR = ROOT / 'ingest' / 'wzb' / '370-corresp'
TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'


def main():
    with open(DIR / 'offene-faelle.csv', encoding='utf-8-sig', newline='') as f:
        bekannt = {(r['form_schluessel'], r['lemma']) for r in csv.DictReader(f, delimiter=';')}

    zaehl = Counter()
    bsp = defaultdict(list)
    for _, el in etree.iterparse(str(ROOT / 'tei' / 'WZB.tei.xml'), tag=TEI + 'w'):
        ref = el.get('lemmaRef')
        if ref and not el.get('corresp'):
            lem = ref.split('#')[-1].split()[0]
            form = unicodedata.normalize('NFC', ''.join(el.itertext()).strip()).lower()
            k = (form, lem)
            if k not in bekannt:
                zaehl[k] += 1
                if len(bsp[k]) < 3:
                    bsp[k].append('%s %s' % (el.get(XMLID), form))
        el.clear()

    zeilen = sorted(zaehl.items(), key=lambda t: (-t[1], t[0]))
    with open(DIR / 'offene-faelle-nachtrag.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';', lineterminator='\n')
        w.writerow(['form_schluessel', 'lemma', 'tokens', 'grund', 'beispiele'])
        for (form, lem), n in zeilen:
            w.writerow([form, lem, n, 'seit dem 31.08.2026 dazugekommen, nicht in offene-faelle.csv',
                        ' | '.join(bsp[(form, lem)])])
    print('%d Paare, %d Tokens' % (len(zeilen), sum(zaehl.values())))


if __name__ == '__main__':
    main()
