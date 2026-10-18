# -*- coding: utf-8 -*-
"""Verbindet die Urteile der zweiten Lesung (Issue #603) mit der Eingabe und prueft sie.

Aufruf:
    python scripts/review/verbinden-lesung-603.py <stapeldir> <eingabe.tsv> <teilname> [n_agenten stapel_je_agent stichprobe_je_agent seed [offset]]

Liest stapel-NN.tsv und urteil-NN.tsv aus <stapeldir> (Ausgabe von stapel-603.py und der
lesenden Agenten) und die Eingabe-TSV, aus der die Stapel gebaut wurden. Verbunden wird ueber
nr, nicht ueber w_id: Agenten haben w_id vereinzelt falsch abgeschrieben, das Urteil gehoert
trotzdem zur Zeile mit dieser nr (am Text geprueft). Jede Korrektur wird gemeldet. Harter Fehler
in der Meldung: unbekannte nr, doppelte w_id, Wert ausserhalb der erlaubten Mengen, tier ohne
Tierklasse, Tierklasse ohne tier. Schreibt <stapeldir>/../teil-<teilname>.tsv. Mit n_agenten
zieht es je Agent (stapel_je_agent Stapel) eine Stichprobe zum Nachlesen am Text.
"""
import sys, glob, collections, random, os
sys.stdout.reconfigure(encoding='utf8')
D, INP, NAME = sys.argv[1:4]
NAG = int(sys.argv[4]) if len(sys.argv) > 4 else 0
PER = int(sys.argv[5]) if len(sys.argv) > 5 else 4
SMP = int(sys.argv[6]) if len(sys.argv) > 6 else 3
random.seed(int(sys.argv[7]) if len(sys.argv) > 7 else 607)
L = open(INP, encoding='utf8').read().splitlines()
H = L[0].split('\t')
rows = [dict(zip(H, l.split('\t'))) for l in L[1:]]
WER = {'mensch', 'tier', 'unklar', 'keine_nahrung'}
TK = {'saeugetier', 'vogel', 'fisch', 'andere', 'unbestimmt', '-'}
ART = {'nahrungsaufnahme', 'fuettern', 'rezept', 'uebertragen', 'sonstiges'}
ctx = {}
for f in glob.glob(D + '/stapel-*.tsv'):
    for l in open(f, encoding='utf8').read().splitlines()[1:]:
        p = l.split('\t'); ctx[p[1]] = p
nrctx = {}
for f in glob.glob(D + '/stapel-*.tsv'):
    for l in open(f, encoding='utf8').read().splitlines()[1:]:
        p = l.split('\t'); nrctx[p[0]] = p
res = {}
fehler = []
korrigiert = []
for f in sorted(glob.glob(D + '/urteil-*.tsv')):
    ls = open(f, encoding='utf8').read().splitlines()
    if ls[0].split('\t')[:5] != ['nr', 'w_id', 'wer', 'tierklasse', 'art']:
        fehler.append('Kopf ' + f)
    for l in ls[1:]:
        p = l.split('\t')
        if len(p) != 6:
            fehler.append('Felder %d: %s' % (len(p), l[:80])); continue
        if p[0] not in nrctx:
            fehler.append('nr unbekannt ' + p[0]); continue
        if nrctx[p[0]][1] != p[1]:
            korrigiert.append((p[0], p[1], nrctx[p[0]][1]))
            p[1] = nrctx[p[0]][1]
        if p[1] in res:
            fehler.append('doppelt ' + p[1])
        if p[2] not in WER or p[3] not in TK or p[4] not in ART:
            fehler.append('Wert ' + l[:120])
        if p[2] == 'tier' and p[3] == '-':
            fehler.append('tier ohne Klasse ' + p[1])
        if p[2] != 'tier' and p[3] != '-':
            fehler.append('Klasse ohne tier ' + p[1])
        res[p[1]] = p
fehlt = [r['w_id'] for r in rows if r['w_id'] not in res]
fremd = [w for w in res if w not in {r['w_id'] for r in rows}]
print('w_id aus nr korrigiert:', korrigiert)
print('Eingabe', len(rows), 'Urteile', len(res), 'fehlt', len(fehlt), 'fremd', len(fremd), 'Formfehler', len(fehler))
for x in fehler[:15]: print('  ', x)
for w in fehlt[:10]: print('  fehlt', w)
out = open(D + '/../teil-' + NAME + '.tsv', 'w', encoding='utf8', newline='')
out.write('\t'.join(['sigle', 'w_id', 'lemma_id', 'lemma', 'form', 'sense_ids_im_ana', 'klasse_vorsortierung', 'wer', 'tierklasse', 'art', 'begruendung']) + '\n')
c = collections.Counter(); kreuz = collections.Counter()
for r in rows:
    p = res.get(r['w_id'])
    if not p: continue
    out.write('\t'.join([r['sigle'], r['w_id'], r['lemma_id'], r['lemma'], r['form'], r['sense_ids_im_ana'], r['klasse'], p[2], p[3], p[4], p[5]]) + '\n')
    c[p[2]] += 1; kreuz[(r['klasse'], p[2])] += 1
out.close()
print('wer:', dict(c), 'Summe', sum(c.values()))
print('Kreuz (Vorsortierung, Lesung):', dict(kreuz))
# Stichprobe: je Agent SMP Belege (2 mit Urteil tier/mensch/unklar, Rest keine_nahrung)
order = [r['w_id'] for r in rows]
if NAG:
    chunk = PER * 80
    for a in range(NAG):
        OFF = int(sys.argv[8]) if len(sys.argv) > 8 else 0
        ids = [w for w in order[OFF + a * chunk:OFF + (a + 1) * chunk] if w in res]
        pos = [w for w in ids if res[w][2] != 'keine_nahrung']
        neg = [w for w in ids if res[w][2] == 'keine_nahrung']
        pick = random.sample(pos, min(SMP - 1, len(pos))) + random.sample(neg, min(1, len(neg)))
        for w in pick:
            k = ctx[w][4]
            i = k.index('[[')
            print('S%d %s lemma=%s | URTEIL %s/%s/%s | %s' % (a + 1, w, res[w][2] and ctx[w][2], res[w][2], res[w][3], res[w][4], k[max(0, i - 130):i + 160]))
