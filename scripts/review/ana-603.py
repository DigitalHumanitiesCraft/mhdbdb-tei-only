"""Kennzahlen zu den Senses mit concept_21111000 (#603), aus den Ausgaben von vorsortieren-603.py.

Aufruf: python scripts/review/ana-603.py <ordner>
Liest senses-21111000.tsv und lemmata-ohne-ana.tsv aus dem Ordner (etwa ingest/review/603-ernaehrung)
und gibt die Zaehlungen auf der Konsole aus; schreibt nichts.
"""
import sys
sys.stdout.reconfigure(encoding='utf8')
rows = [l.split('\t') for l in open(sys.argv[1] + '/senses-21111000.tsv', encoding='utf8').read().splitlines()[1:]]
n = len(rows)
b = [int(r[3]) for r in rows]
print('Senses', n, 'mit >=1 Beleg', sum(1 for x in b if x), 'ohne Beleg', sum(1 for x in b if not x), 'Summe', sum(b))
print('Senses mit >=1 Tier-Beleg', sum(1 for r in rows if int(r[4]) > 0))
print('Senses mit >=5 Tier-Belegen', sum(1 for r in rows if int(r[4]) >= 5))
tiercon = [r for r in rows if any(c.startswith('concept_140') or c.startswith('concept_141') for c in r[8].split())]
print('Senses mit zusaetzlichem Konzept 14xxxxxx:', len(tiercon), [(r[0], r[2], r[3]) for r in tiercon])
top = sorted(rows, key=lambda r: -int(r[4]))[:25]
for r in top:
    print(r[0], r[2], 'gesamt', r[3], 'tier', r[4], 'mensch', r[5], 'unklar', r[6])
top = sorted(rows, key=lambda r: -int(r[3]))[:8]
for r in top:
    print('gross', r[0], r[2], r[3])
oa = [l.split('\t') for l in open(sys.argv[1] + '/lemmata-ohne-ana.tsv', encoding='utf8').read().splitlines()[1:]]
print('Lemmata', len(oa), 'ohne-ana-Summe', sum(int(r[2]) for r in oa), 'tier', sum(int(r[3]) for r in oa), 'mensch', sum(int(r[4]) for r in oa), 'unklar', sum(int(r[5]) for r in oa))
