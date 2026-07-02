#!/usr/bin/env python3
"""
#143: Konvertiert die drei als Prosa bestätigten Texte (APO, HMT, HH)
von <l>-Verszeilen auf <lb/>-Zeilenumbrüche nach dem TEI-MODEL §8.1-Muster.

KZW-Entscheid 2026-06-12 (Issue #143):
- HMT (Hans Mair, Buch von Troja): Prosa lt. geschichtsquellen.de/werk/3419
- APO (Heinrich Steinhöwel, Apollonius 1461): Prosa (Terrahe-Edition)
- HH (Himmel und Hölle): frühmhd. rhythmische Prosa

Transformation (byte-minimal, analog insert-lg-stanzas-138.py):
- Zeile `<l n="X">`  →  `<lb n="X"/>`  (gleiche Einrückung)
- Zeile `</l>`       →  entfällt
- Alle anderen Zeilen (insbesondere <w>-Elemente) bleiben byte-identisch,
  damit die Positionszählung (CONTRACTS §B) unberührt ist.

Vorbedingung je Datei: jedes <l ...> eröffnet eine eigene Zeile, jedes
</l> steht allein auf seiner Zeile (wird geprüft, sonst Abbruch).
"""

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SIGLES = ['APO', 'HMT', 'HH']

L_OPEN = re.compile(r'^(\s*)<l n="([^"]+)">\s*$')
L_CLOSE = re.compile(r'^\s*</l>\s*$')
L_ANY = re.compile(r'<l[ >]|</l>')


def convert(sigle: str) -> bool:
    path = REPO / 'tei' / f'{sigle}.tei.xml'
    lines = path.read_text(encoding='utf-8').splitlines(keepends=True)

    opens = sum(1 for ln in lines if L_OPEN.match(ln))
    closes = sum(1 for ln in lines if L_CLOSE.match(ln))
    total_l = sum(len(L_ANY.findall(ln)) for ln in lines)
    if opens != closes or opens * 2 != total_l:
        print(f'❌ {sigle}: Layout-Annahme verletzt '
              f'(opens={opens}, closes={closes}, l-Tokens={total_l}) — Abbruch')
        return False

    out = []
    converted = 0
    for ln in lines:
        m = L_OPEN.match(ln)
        if m:
            indent, n = m.groups()
            out.append(f'{indent}<lb n="{n}"/>\n')
            converted += 1
            continue
        if L_CLOSE.match(ln):
            continue
        out.append(ln)

    path.write_text(''.join(out), encoding='utf-8')
    print(f'✅ {sigle}: {converted} <l> → <lb/> konvertiert')
    return True


def main():
    ok = all(convert(s) for s in SIGLES)
    if not ok:
        sys.exit(1)
    print('\nNächste Schritte: Schema-Validierung, Index-Rebuild '
          '(lineStarts/lineEnds ändern sich), TEI-MODEL §8.1 korrigieren.')


if __name__ == '__main__':
    main()
