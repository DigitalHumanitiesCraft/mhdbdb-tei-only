#!/usr/bin/env python3
"""
#228, Nachtrag aus Review Runde 2: sense/@ana-Typverweise entfernen, die
apply-228.py ueber die Regeneration von variants.xml haengend gemacht hat.

sense/@ana ist eine Leerzeichenliste von #type_N. Faellt ein Typ aus
variants.xml, weil alle seine Belege entannotiert wurden, bleibt sein Token
im Lexikon stehen und zeigt ins Leere. Entfernt werden nur Tokens, deren Typ
in variants.xml der Basisrevision (vor #228) existierte und im Arbeitsbaum
fehlt. Tokens, die schon auf der Basis hingen (105, aelterer Bestand), bleiben
unberuehrt: das ist keine Entscheidung dieses Tickets.

Wird eine Liste dadurch leer, faellt das Attribut ganz (Schema: ana optional).

Aufruf: python scripts/ingest/entannotate-228/prune-ana-228.py --basis d166fa4b1 [--apply]
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
LEX = ROOT / 'authority-files' / 'lexicon.xml'
VAR = ROOT / 'authority-files' / 'variants.xml'
T = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'
ERWARTET = 82


def typen(root):
    return {e.get(XID) for e in root.iter() if e.get(XID)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--basis', required=True)
    ap.add_argument('--apply', action='store_true')
    a = ap.parse_args()

    basis = typen(etree.fromstring(subprocess.run(
        ['git', '-C', str(ROOT), 'show', f'{a.basis}:authority-files/variants.xml'],
        capture_output=True, check=True).stdout))
    jetzt = typen(etree.parse(str(VAR)).getroot())
    weg = basis - jetzt

    ziele = {}
    for s in etree.parse(str(LEX)).getroot().iter(T + 'sense'):
        toks = (s.get('ana') or '').split()
        raus = [t for t in toks if t.startswith('#type_') and t[1:] in weg]
        if raus:
            ziele[s.get(XID)] = (toks, raus)
    n = sum(len(r) for _, r in ziele.values())
    print(f'{n} Tokens in {len(ziele)} Senses (Basis {a.basis}: {len(weg)} Typen entfallen)')
    if n != ERWARTET:
        sys.exit(f'FEHLER: erwartet {ERWARTET}')

    with open(LEX, encoding='utf-8', newline='') as f:
        text = f.read()
    for sid, (toks, raus) in sorted(ziele.items()):
        alt = f'<sense xml:id="{sid}" ana="{" ".join(toks)}"'
        rest = [t for t in toks if t not in raus]
        neu = f'<sense xml:id="{sid}"' + (f' ana="{" ".join(rest)}"' if rest else '')
        if text.count(alt) != 1:
            sys.exit(f'FEHLER: Anker fuer {sid} nicht genau einmal')
        text = text.replace(alt, neu)
        print(f'  {sid}: -{" ".join(raus)}' + ('' if rest else ' (Attribut entfaellt)'))
    etree.fromstring(text.encode('utf-8'))
    if a.apply:
        with open(LEX, 'w', encoding='utf-8', newline='') as f:
            f.write(text)
        print('geschrieben:', LEX)
    else:
        print('Trockenlauf, nichts geschrieben (--apply)')


if __name__ == '__main__':
    main()
