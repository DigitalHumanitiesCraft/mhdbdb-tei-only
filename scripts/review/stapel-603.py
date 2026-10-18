# -*- coding: utf-8 -*-
"""Stapel fuer die zweite Lesung (Issue #603): weiter Kontext aus dem TEI, ohne maschinelle Klasse.

Aufruf (liest das Repo, aendert darin nichts; der Ausgabeordner liegt ausserhalb des Repos
oder unter temp/):
    python scripts/review/stapel-603.py <repo> <eingabe.tsv> <ausgabeordner> <stapelgroesse> [<stichprobe_n> <seed>]

Eingabe: TSV mit den Spalten sigle und w_id (wie belege-tier.tsv / alle-belege-vorsortiert.tsv).
Schreibt stapel-NN.tsv (nr, w_id, lemma, form, kontext; die Klasse der Vorsortierung steht
absichtlich nicht darin, damit das Lesen nicht an ihr haengt) und schluessel.tsv (nr -> Eingabezeile).
Kontext: 30 Woerter links und rechts, der Beleg als [[...]]. Fehlt eine w_id im TEI, bricht der Lauf ab.
"""
import sys, os, random, collections
from lxml import etree

sys.stdout.reconfigure(encoding='utf8')
REPO, INP, OUT, SIZE = sys.argv[1].rstrip('/\\'), sys.argv[2], sys.argv[3].rstrip('/\\'), int(sys.argv[4])
SAMPLE = int(sys.argv[5]) if len(sys.argv) > 5 else 0
SEED = int(sys.argv[6]) if len(sys.argv) > 6 else 0
T = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'
WIN = 30
_o, _r = os.path.realpath(OUT), os.path.realpath(REPO)
if (_o == _r or _o.startswith(_r + os.sep)) and not _o.startswith(os.path.join(_r, 'temp') + os.sep):
    sys.exit('FEHLER: Ausgabeordner liegt im Repo (erlaubt nur unter temp/): ' + OUT)
os.makedirs(OUT, exist_ok=True)

lines = open(INP, encoding='utf8').read().splitlines()
head = lines[0].split('\t')
rows = [dict(zip(head, l.split('\t'))) for l in lines[1:]]
if SAMPLE:
    random.seed(SEED)
    rows = random.sample(rows, SAMPLE)
by_sigle = collections.defaultdict(list)
for r in rows:
    by_sigle[r['sigle']].append(r)

out = {}
for sigle, rs in by_sigle.items():
    tr = etree.parse('%s/tei/%s.tei.xml' % (REPO, sigle))
    toks = [e for e in tr.iter(T + 'w', T + 'pc')]
    idx = {e.get(XID): i for i, e in enumerate(toks) if e.get(XID)}
    for r in rs:
        if r['w_id'] not in idx:
            sys.exit('FEHLER: w_id nicht im TEI: ' + r['w_id'])
        i = idx[r['w_id']]
        a = ' '.join(''.join(e.itertext()).strip() for e in toks[max(0, i - WIN):i])
        b = ' '.join(''.join(e.itertext()).strip() for e in toks[i + 1:i + 1 + WIN])
        form = ''.join(toks[i].itertext()).strip()
        out[r['w_id']] = (r, '%s [[%s]] %s' % (a, form, b), form)

order = [r['w_id'] for r in rows]
key = open(OUT + '/schluessel.tsv', 'w', encoding='utf8', newline='')
key.write('nr\t' + '\t'.join(head) + '\n')
for s in range(0, len(order), SIZE):
    chunk = order[s:s + SIZE]
    with open('%s/stapel-%02d.tsv' % (OUT, s // SIZE + 1), 'w', encoding='utf8', newline='') as fh:
        fh.write('nr\tw_id\tlemma\tform\tkontext\n')
        for k, w in enumerate(chunk, s + 1):
            r, c, form = out[w]
            fh.write('%d\t%s\t%s\t%s\t%s\n' % (k, w, r.get('lemma', ''), form, c.replace('\t', ' ')))
    for k, w in enumerate(chunk, s + 1):
        key.write('%d\t%s\n' % (k, '\t'.join(out[w][0][h] for h in head)))
key.close()
print('Belege', len(order), 'Stapel', (len(order) + SIZE - 1) // SIZE, 'Sigle', len(by_sigle))
