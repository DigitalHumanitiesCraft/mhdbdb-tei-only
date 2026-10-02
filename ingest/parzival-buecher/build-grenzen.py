#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#358: die 16 Buchgrenzen des Parzival (Lachmann-Zaehlung) auf die erste Wort-ID in
tei/PZ.tei.xml abbilden und nach ingest/parzival-buecher/grenzen.csv schreiben.

Die Buchanfaenge (Spalte beginn_stelle) stehen in BUECHER, mit den Quellen, auf
denen sie stehen. Das Skript prueft sie gegen das TEI: die Zeile muss existieren,
und ihre ersten Woerter muessen der in BUECHER genannten Anfangszeile gleichen,
sonst bricht es ab. Die erste Wort-ID ist die des ersten <w> der Zeile in
Dokumentordnung; ein <pc> davor (in Buch IX steht eine editorische Klammer
vor dem ersten Wort) zaehlt nicht.

Aufruf aus dem Repo-Wurzelverzeichnis:
    python ingest/parzival-buecher/build-grenzen.py
"""

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
TEI = ROOT / 'tei' / 'PZ.tei.xml'
ZIEL = Path(__file__).resolve().parent / 'grenzen.csv'

BARTSCH = ("Bartsch (Hrsg.), Wolfram's von Eschenbach Parzival und Titurel, Deutsche Classiker des "
           'Mittelalters 9-11, Leipzig: Brockhaus 1875-77, %s, Buchueberschrift mit erstem Vers')
MARTIN = ('Martin (Hrsg.), Wolframs von Eschenbach Parzival und Titurel, Zweiter Teil: Kommentar, '
          'Halle: Waisenhaus 1903, https://archive.org/details/parzival00wolfuoft, '
          'Kommentar zu Buch %s setzt bei %s ein')
B9 = 'Bd. 9 (2. Aufl. 1875), https://archive.org/details/wolframsvonesch01bartgoog'
B10 = 'Bd. 10 (1876), https://archive.org/details/wolframsvonesch03bartgoog'
B11 = 'Bd. 11 (2. Aufl. 1877), https://archive.org/details/wolframsvonesch00bartgoog'

# (Buch, Stelle, erste Woerter laut TEI, Bartsch-Band, erste kommentierte Stelle bei Martin)
BUECHER = [
    ('I', '1,1', 'ist zwîvel herzen', B9, '1,1'),
    ('II', '58,27', 'dâ ze spâne', B9, '58,27'),
    ('III', '116,5', 'ez machet trûrec', B9, '116,5'),
    ('IV', '179,13', 'dannen schiet sus', B9, '179,14'),
    ('V', '224,1', 'swer ruochet hoeren', B9, '224,2'),
    ('VI', '280,1', 'welt ir nû hoeren', B9, '280,1'),
    ('VII', '338,1', 'der nie gewarp', B10, '338,1'),
    ('VIII', '399,1', 'nû hoert von âventiuren', B10, '399,7'),
    ('IX', '433,1', 'tuot ûf wem', B10, '433,1'),
    ('X', '503,1', 'ez naehet nû', B10, '503,1'),
    ('XI', '553,1', 'grôz müede im', B10, '553,5'),
    ('XII', '583,1', 'swer im nû ruowe', B10, '583,4'),
    ('XIII', '627,1', 'arnîve zorn bejagete', B11, '627,1'),
    ('XIV', '679,1', 'ob von dem werden', B11, '679,4'),
    ('XV', '734,1', 'vil liute des hât', B11, '734,2'),
    ('XVI', '787,1', 'amfortas und die', B11, '787,3'),
]


def lade_zeilen():
    """Zeilenschluessel (Abschnitt + 2stelliger Vers) -> [(wort_id, text)] in Dokumentordnung."""
    t = TEI.read_text(encoding='utf-8')
    zeilen = {}
    for m in re.finditer(r'<w xml:id="(PZ_(\d+)_(\d+))"[^>]*>([^<]*)</w>', t):
        zeilen.setdefault(m.group(2), []).append((m.group(1), m.group(4)))
    return zeilen


def main():
    zeilen = lade_zeilen()
    ausgabe = []
    for buch, stelle, anfang, bartsch, martin in BUECHER:
        sec, vers = stelle.split(',')
        key = '%s%02d' % (sec, int(vers))
        if key not in zeilen:
            sys.exit('Zeile %s (Buch %s) fehlt im TEI' % (stelle, buch))
        woerter = zeilen[key]
        text = ' '.join(w for _, w in woerter)
        if not text.startswith(anfang):
            sys.exit('Buch %s: Zeile %s beginnt mit "%s", erwartet "%s"' % (buch, stelle, text[:40], anfang))
        quelle = '%s: Buch %s beginnt bei %s mit "%s"; %s; Text in tei/PZ.tei.xml an dieser Stelle gleich' % (
            BARTSCH % bartsch, buch, stelle, anfang, MARTIN % (buch, martin))
        ausgabe.append(['Buch ' + buch, stelle, woerter[0][0], quelle])
    if len(ausgabe) != 16 or len({a[2] for a in ausgabe}) != 16:
        sys.exit('Erwartet 16 verschiedene Buchanfaenge')
    with open(ZIEL, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';', lineterminator='\n')
        w.writerow(['buch', 'beginn_stelle', 'erste_wort_id', 'quelle'])
        w.writerows(ausgabe)
    print('%d Buchgrenzen geschrieben: %s' % (len(ausgabe), ZIEL))


if __name__ == '__main__':
    main()
