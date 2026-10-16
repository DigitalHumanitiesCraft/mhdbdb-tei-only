"""Zweite Stichprobe: Klasse tier OHNE Mensch-Treffer (Belege mit @ana), Seed 604, 10 Stueck + Zaehlungen (#603).

Aufruf: python scripts/review/stichprobe2-603.py <ordner>
Der Ordner ist der Ausgabeordner von vorsortieren-603.py: gelesen wird dort
alle-belege-vorsortiert.tsv, geschrieben stichprobe2-tier-ohne-mensch.tsv.
"""
import sys, random, collections
sys.stdout.reconfigure(encoding='utf8')
OUT = sys.argv[1]
rows = [l.split('\t') for l in open(OUT + '/alle-belege-vorsortiert.tsv', encoding='utf8').read().splitlines()[1:]]
ana = [r for r in rows if r[2].startswith('lemma_')]
tier = [r for r in ana if r[6] == 'tier']
t_only = [r for r in tier if r[7] != 'ja']
print('mit ana:', len(ana), 'tier:', len(tier), 'davon ohne Mensch-Treffer:', len(t_only), 'mit:', len(tier) - len(t_only))
ordered = [r for r in tier if 'T1' in r[8]]
print('tier mit mindestens einem T1-Treffer:', len(ordered), '; nur T2:', len(tier) - len(ordered))
random.seed(604)
out = random.sample(t_only, 10)
with open(OUT + '/stichprobe2-tier-ohne-mensch.tsv', 'w', encoding='utf8') as fh:
    fh.write('\t'.join(['sigle', 'w_id', 'sense', 'lemma', 'form', 'tierwort', 'kontext']) + '\n')
    for i, r in enumerate(out):
        fh.write('\t'.join([r[0], r[1], r[2], r[4], r[5], r[8], r[10]]) + '\n')
        print(i + 1, r[1], r[4], '|', r[8], '|', r[10])
ohne = [r for r in rows if r[2] == '(ohne ana)']
print('ohne ana (Ziel-Lemmata):', len(ohne), collections.Counter(r[6] for r in ohne))
