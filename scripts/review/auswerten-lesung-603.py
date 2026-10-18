# -*- coding: utf-8 -*-
"""Auswertung der zweiten Lesung (Issue #603): fuegt die Teile zusammen und zaehlt fuer die Konzeptfrage.

Aufruf (liest das Repo und die Teildateien, aendert im Repo nichts ausser dem Ausgabeordner):
    python scripts/review/auswerten-lesung-603.py <repo> <teil-tier.tsv> <teil-unklar.tsv> <teil-mensch.tsv> <ausgabeordner>

Die Teildateien haben die Spalten sigle, w_id, lemma_id, lemma, form, sense_ids_im_ana,
klasse_vorsortierung, wer, tierklasse, art, begruendung (Urteile von Agenten, Eingabe).
Schreibt zweite-lesung.tsv (alle Teile, Spalte pruefen aus pruefen-603.tsv), senses-lesung.tsv
(je Bedeutung mit concept_21111000 die Lesung ihrer Belege), lemmata-lesung.tsv (je Lemma) und
konzeptfrage.txt (Zaehlung zu den beiden Optionen). Ein Beleg mit Urteil, aber ohne Eintrag
in senses-21111000.tsv bei gesetztem Sense, ist ein harter Fehler.
"""
import sys, re, glob, os, collections
sys.stdout.reconfigure(encoding='utf8')
REPO = sys.argv[1].rstrip('/\\')
TEILE = sys.argv[2:5]
OUT = sys.argv[5].rstrip('/\\')
os.makedirs(OUT, exist_ok=True)
DIR = REPO + '/ingest/review/603-ernaehrung'


def tsv(path):
    L = open(path, encoding='utf8').read().splitlines()
    h = L[0].split('\t')
    return h, [dict(zip(h, l.split('\t'))) for l in L[1:]]


pruefen = {}
pp = DIR + '/pruefen-603.tsv'
if os.path.exists(pp):
    for r in tsv(pp)[1]:
        pruefen[r['w_id']] = r['grund']

_, senses = tsv(DIR + '/senses-21111000.tsv')
SENSE = {r['sense_id']: r for r in senses}
rows = []
for t in TEILE:
    rows += tsv(t)[1]
ids = [r['w_id'] for r in rows]
if len(ids) != len(set(ids)):
    sys.exit('FEHLER: doppelte w_id ueber die Teile')
for r in rows:
    r['pruefen'] = pruefen.get(r['w_id'], '')
    for s in r['sense_ids_im_ana'].split(','):
        if s.startswith('lemma_') and s not in SENSE:
            pass  # ana-Token auf eine Bedeutung ohne 21111000 (weitere Bedeutung desselben Worts)
H = ['sigle', 'w_id', 'lemma_id', 'lemma', 'form', 'sense_ids_im_ana', 'klasse_vorsortierung', 'wer', 'tierklasse', 'art', 'begruendung', 'pruefen']
with open(OUT + '/zweite-lesung.tsv', 'w', encoding='utf8', newline='') as fh:
    fh.write('\t'.join(H) + '\n')
    for r in rows:
        fh.write('\t'.join(r[h] for h in H) + '\n')

# je Bedeutung
ana_rows = [r for r in rows if r['sense_ids_im_ana'].startswith('lemma_')]
per_sense = collections.defaultdict(collections.Counter)
per_sense_tk = collections.defaultdict(collections.Counter)
for r in ana_rows:
    for s in r['sense_ids_im_ana'].split(','):
        if s in SENSE:
            per_sense[s][r['wer']] += 1
            if r['wer'] == 'tier':
                per_sense_tk[s][r['tierklasse']] += 1
with open(OUT + '/senses-lesung.tsv', 'w', encoding='utf8', newline='') as fh:
    fh.write('\t'.join(['sense_id', 'lemma_id', 'orth', 'gelesen', 'mensch', 'tier', 'unklar', 'keine_nahrung', 'tier_saeugetier', 'tier_vogel', 'tier_fisch', 'tier_andere', 'tier_unbestimmt', 'weitere_konzepte']) + '\n')
    for s, r in SENSE.items():
        c, k = per_sense[s], per_sense_tk[s]
        fh.write('\t'.join(str(x) for x in [s, r['lemma_id'], r['orth'], sum(c.values()), c['mensch'], c['tier'], c['unklar'], c['keine_nahrung'],
                                            k['saeugetier'], k['vogel'], k['fisch'], k['andere'], k['unbestimmt'], r['weitere_konzepte']]) + '\n')

# je Lemma (alle gelesenen Belege)
per_lem = collections.defaultdict(collections.Counter)
for r in rows:
    per_lem[(r['lemma_id'], r['lemma'])][r['wer']] += 1
with open(OUT + '/lemmata-lesung.tsv', 'w', encoding='utf8', newline='') as fh:
    fh.write('\t'.join(['lemma_id', 'lemma', 'gelesen', 'mensch', 'tier', 'unklar', 'keine_nahrung']) + '\n')
    for (lid, lem), c in sorted(per_lem.items(), key=lambda x: -sum(x[1].values())):
        fh.write('\t'.join(str(x) for x in [lid, lem, sum(c.values()), c['mensch'], c['tier'], c['unklar'], c['keine_nahrung']]) + '\n')

# Konzeptfrage
S = []
tier_rows = [r for r in rows if r['wer'] == 'tier']
S.append('Gelesen: %d Belege (%s)' % (len(rows), ', '.join('%s %d' % (k, v) for k, v in collections.Counter(r['wer'] for r in rows).most_common())))
S.append('Davon mit @ana auf eine Bedeutung mit concept_21111000: %d' % len(ana_rows))
S.append('Urteil tier: %d Belege, nach Tierklasse: %s' % (len(tier_rows), ', '.join('%s %d' % kv for kv in collections.Counter(r['tierklasse'] for r in tier_rows).most_common())))
S.append('Urteil tier, davon mit @ana: %d, ohne @ana: %d' % (sum(1 for r in tier_rows if r['sense_ids_im_ana'].startswith('lemma_')), sum(1 for r in tier_rows if not r['sense_ids_im_ana'].startswith('lemma_'))))
S.append('Urteil tier nach art: %s' % ', '.join('%s %d' % kv for kv in collections.Counter(r['art'] for r in tier_rows).most_common()))
sk = [s for s in SENSE if per_sense_tk[s]['saeugetier']]
S.append('Bedeutungen mit concept_21111000, in denen mindestens ein Beleg als Saeugetier gelesen ist: %d, mit %d Belegen' % (len(sk), sum(per_sense_tk[s]['saeugetier'] for s in sk)))
for kl in ('vogel', 'fisch', 'andere', 'unbestimmt'):
    sl = [s for s in SENSE if per_sense_tk[s][kl]]
    S.append('Bedeutungen mit mindestens einem Beleg Tierklasse %s: %d, mit %d Belegen' % (kl, len(sl), sum(per_sense_tk[s][kl] for s in sl)))
ts = [s for s in SENSE if per_sense[s]['tier']]
S.append('Bedeutungen mit mindestens einem Beleg als tier gelesen: %d von %d Bedeutungen mit concept_21111000 (%d mit mindestens einem gelesenen Beleg)' % (len(ts), len(SENSE), sum(1 for s in SENSE if sum(per_sense[s].values()))))
mj = [s for s in ts if per_sense[s]['tier'] * 2 > sum(per_sense[s].values())]
S.append('Davon Bedeutungen, in denen mehr als die Haelfte der gelesenen Belege tier ist: %d, mit %d tier-Belegen' % (len(mj), sum(per_sense[s]['tier'] for s in mj)))
S.append('Pruefen-Liste: %d Belege' % sum(1 for r in rows if r['pruefen']))

# Korpusbelege auf die Bedeutungen unter concept_14011240 (Option A)
lex = open(REPO + '/authority-files/lexicon.xml', encoding='utf8').read()
sid14 = set()
for m in re.finditer(r'<sense\b[^>]*xml:id="([^"]+)"[^>]*>(.*?)</sense>', lex, re.S):
    if 'concepts.xml#concept_14011240"' in m.group(2):
        sid14.add(m.group(1))
S.append('Optionsrechnung A (Umbenennen von concept_14011240): Bedeutungen im Lexikon mit diesem Konzept: %d' % len(sid14))
n14 = collections.Counter()
for f in glob.glob(REPO + '/tei/*.xml'):
    t = open(f, encoding='utf8').read()
    for m in re.finditer(r'<w\b[^>]*?\bana="([^"]*)"', t):
        for s in m.group(1).split():
            s = s.split('#')[-1]
            if s in sid14:
                n14[s] += 1
S.append('Korpusbelege (w mit @ana) auf diese Bedeutungen: %d, auf %d der %d Bedeutungen' % (sum(n14.values()), len(n14), len(sid14)))
both = [s for s in sid14 if s in SENSE]
S.append('Davon Bedeutungen, die auch concept_21111000 tragen: %d (%s)' % (len(both), ', '.join(both)))
open(OUT + '/konzeptfrage.txt', 'w', encoding='utf8').write('\n'.join(S) + '\n')
print('\n'.join(S))
