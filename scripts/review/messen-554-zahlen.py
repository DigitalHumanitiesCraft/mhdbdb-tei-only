#!/usr/bin/env python3
"""#554: heutige Zahlen fuer die Glossarkommentare, am Korpus gemessen.

Ersetzt die historischen MHDBDB-Trefferzahlen (Suchsyntax von 2016–2018) in den
Kommentaren von ei, enbiʒen, braamber, hunger, hungerc, huon, nagel/jeroffel, win, brot.
KZW hat am 16.10.2026 beides freigegeben: historische Ergebnisse entfallen, heutige
Zahlen am heutigen Korpus treten an ihre Stelle.

Zaehlregeln (in jeder Ausgabezeile mit Menge):
- Gezaehlt werden nur Woerter mit Lemma-Annotation: ein <w> ohne @lemmaRef zaehlt nirgends mit
  und wird in einer Folge uebersprungen (A, unannotiertes Wort, B zaehlt als A B). Formen, die im Text stehen, aber nicht annotiert sind, fehlen.
- Token: <w> mit @lemmaRef, das die Lemma-ID als eigenes Element der Liste enthaelt.
- "Zeile": ein <l>-Element in einem Text ohne <lb/>. Texte mit <lb/> (Prosa, auch WZB, wo <l> eine
  Satzeinheit ist) und Prosatexte ohne <l> tragen zu Zeilenmessungen nichts bei.
- "A + B in einer Zeile": beide Lemmata kommen in demselben <l> vor. Bei zwei Lemmata in
  beliebiger Reihenfolge, bei drei (niht + ein + ei, umbe + ein + ei) in der genannten.
- "A B hintereinander": aufeinanderfolgende <w> mit @lemmaRef in Dokumentreihenfolge.
- "A nahe B (±k)": zaehlt die A-Token, bei denen B in derselben oder in den k
  davorliegenden bzw. folgenden <l> desselben Textes vorkommt.

Aufruf: python scripts/review/messen-554-zahlen.py
"""
import re
import sys
from pathlib import Path

from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')

TEI = '{http://www.tei-c.org/ns/1.0}'
ROOT = Path(__file__).resolve().parents[2]

L = {
    'niht': 'lemma_4377', 'ein': 'lemma_1331', 'ei': 'lemma_1324', 'umbe': 'lemma_6422',
    'rot': 'lemma_4954', 'rose': 'lemma_4951', 'wiz': 'lemma_7549', 'lilje': 'lemma_3775',
    'gruene': 'lemma_2540', 'louch': 'lemma_21803', 'venichel': 'lemma_19933', 'venchelkrut': 'lemma_19934',
    'hunger': 'lemma_2954', 'hungerc': 'lemma_2955', 'not': 'lemma_4400', 'durst': 'lemma_1275',
    'huon': 'lemma_2961', 'und': 'lemma_6467', 'visch': 'lemma_7100', 'nagel': 'lemma_4302',
    'win': 'lemma_7532', 'brot': 'lemma_879', 'ezzen': 'lemma_1764', 'spise': 'lemma_5669',
    'enbizen': 'lemma_1383',
}
ID2KEY = {v: k for k, v in L.items()}


def ids_of(w):
    ref = w.get('lemmaRef')
    if not ref:
        return ()
    return tuple(r.split('#')[-1] for r in ref.split())


def laden():
    """je Text: Tokenfolge [Menge von Keys] und Zeilenfolge [Liste von Key-Mengen]."""
    for p in sorted((ROOT / 'tei').glob('*.tei.xml')):
        tree = etree.parse(str(p))
        folge = []
        for w in tree.iter(TEI + 'w'):
            ks = {ID2KEY[i] for i in ids_of(w) if i in ID2KEY}
            if w.get('lemmaRef'):
                folge.append(ks)
        zeilen = []
        # Prosatexte (WZB): <l> ist dort eine Satzeinheit, die Handschriftenzeile steht in <lb/>
        ist_prosa = next(tree.iter(TEI + 'lb'), None) is not None
        for l in ([] if ist_prosa else tree.iter(TEI + 'l')):
            ks = [ID2KEY[i] for w in l.iter(TEI + 'w') for i in ids_of(w) if i in ID2KEY]
            zeilen.append(ks)
        yield p.name.split('.')[0], folge, zeilen


def main():
    z = {}
    texte = {}

    def add(name, sigle, n=1):
        z[name] = z.get(name, 0) + n
        texte.setdefault(name, set()).add(sigle)

    for sigle, folge, zeilen in laden():
        for ks in folge:
            for k in ks:
                add('token ' + k, sigle)
        # A + B (+ C) in einer Zeile
        def zeile_mit(*keys, geordnet=True):
            for ks in zeilen:
                if not geordnet:
                    ok = all(k in ks for k in keys)
                else:
                    pos = -1
                    ok = True
                    for k in keys:
                        try:
                            pos = ks.index(k, pos + 1)
                        except ValueError:
                            ok = False
                            break
                if ok:
                    add(' + '.join(keys) + ' in einer Zeile', sigle)
        zeile_mit('niht', 'ein', 'ei')
        zeile_mit('umbe', 'ein', 'ei')
        zeile_mit('rot', 'rose', geordnet=False)
        zeile_mit('wiz', 'lilje', geordnet=False)
        zeile_mit('gruene', 'louch', geordnet=False)
        zeile_mit('gruene', 'venichel', geordnet=False)
        zeile_mit('gruene', 'venchelkrut', geordnet=False)
        # hintereinander
        def folge_mit(*keys):
            n = len(keys)
            for i in range(len(folge) - n + 1):
                if all(keys[j] in folge[i + j] for j in range(n)):
                    add(' '.join(keys) + ' hintereinander', sigle)
        folge_mit('hunger', 'not')
        folge_mit('huon', 'und', 'visch')
        folge_mit('win', 'und')
        folge_mit('und', 'brot')
        folge_mit('brot', 'und')
        folge_mit('und', 'win')

        for ks in zeilen:
            if 'hungerc' in ks:
                add('token hungerc in einer Verszeile', sigle, ks.count('hungerc'))

        # A nahe B (±k Zeilen)
        def nahe(a, b, k):
            for i, ks in enumerate(zeilen):
                na = ks.count(a)
                if not na:
                    continue
                lo, hi = max(0, i - k), min(len(zeilen), i + k + 1)
                if any(b in zeilen[j] for j in range(lo, hi)):
                    add('%s nahe %s (±%d Zeilen), Token von %s' % (a, b, k, a), sigle, na)
        nahe('hunger', 'durst', 2)
        nahe('enbizen', 'hunger', 3)
        nahe('enbizen', 'spise', 3)
        nahe('enbizen', 'ezzen', 3)

    for name in sorted(z):
        print('%-60s %6d  in %3d Texten' % (name, z[name], len(texte[name])))


if __name__ == '__main__':
    main()
