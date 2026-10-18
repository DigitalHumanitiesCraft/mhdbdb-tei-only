#!/usr/bin/env python3
"""#461: wie viele der Belege an lemma_1958_sense_3004 meinen einen lebenden Koerper?

Frage KZW 16.10.2026 ("Du solltest erst messen, wie viele der 55 Belege an
sense_3004 einen lebenden Koerper meinen"). Kickoff Lauf 18.10.2026, D3.

Messvorschrift
--------------
Menge: jedes <w> in tei/*.tei.xml, dessen @ana auf lemma_1958_sense_3004
zeigt (lxml waere gleichwertig, hier textuell wie in den apply-Skripten).
Die Einstufung ist ein Leseurteil am Kontext (je Beleg 22 Woerter davor und
danach, Versgrenze als /); sie steht unten in EINSTUFUNG und ist von dem
Menschen zu pruefen, der das Skript liest. Das Skript prueft nur, dass die
Menge genau die 55 Belege der Einstufung ist, und schreibt die Liste.

Klassen: tot (Gebeine Verstorbener, Reliquien, Leichen), lebend (Koerper eines
lebenden Menschen), lebend? (lebend, aber mit Zweifel), Tier (lebende Tiere).

Usage:
    python scripts/review/messen-461-sense3004.py            # Zaehlung, schreibt nichts
    python scripts/review/messen-461-sense3004.py --write    # schreibt ingest/review/461-gebeine/sense3004-lebend.tsv
"""

import io
import re
import sys
from collections import Counter
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[2]
ZIEL = ROOT / 'ingest' / 'review' / '461-gebeine' / 'sense3004-lebend.tsv'
SENSE = 'lemma_1958_sense_3004'
FENSTER = 22

# xml:id -> (Klasse, Begruendung); gelesen am 18.10.2026
EINSTUFUNG = {
    'ADP_3105000_0': ('tot', 'Gebein seiner Heiligen (Reliquie)'),
    'ADP_4117900_4': ('lebend', 'Christus am Kreuz gespannt, "man alles sin gebein moecht han gezellet"'),
    'ADP_4122600_12': ('lebend', 'Aufzaehlung der Koerperteile eines essenden Menschen'),
    'ADP_6831200_4': ('tot', '"der toten gebein", Auferstehung'),
    'ADP_6831200_10': ('tot', 'Gebein der Auferstehenden aus den Graebern'),
    'ADP_6832800_8': ('tot', '"das toten gebein"'),
    'ADP_6833600_1': ('tot', '"das gebein der toten"'),
    'HTR_78950_6': ('lebend', 'Geiziger: "derret sin marc und sin gebein", lebender Koerper'),
    'HTR_207990_5': ('lebend', '"sint diu wip fleisch und gebein", lebende Menschen'),
    'HTR_214570_5': ('lebend?', '"die fleisch do waren und gebein, die sint nu holz erde und stein": Menschen, die inzwischen tot sind, gemeint ist ihr Zustand als Lebende'),
    'HUL_1014_4': ('tot', 'heiliges Gebein der Afra'),
    'JEW_393000000_5': ('lebend', 'ein Lebender in Schrecken: "arm houbt und sin gebein"'),
    'JEW_556900000_3': ('Tier', 'Pharaos Traum, sieben magere Ochsen: "unde vil magerz gebein"'),
    'JEW_557800000_0': ('Tier', 'Pharaos Traum, die mageren Ochsen fressen die fetten: "gebein huot noch daz har"'),
    'JEW_1002900000_8': ('lebend', 'Drohrede an einen lebenden Gegner: "swie gros swie lanc dir sin din gebein"'),
    'JEW_1270500000_4': ('lebend', '"in houbt oder in gebein", Koerper eines Lebenden'),
    'JEW_2330900000_1': ('lebend?', 'Ammen werden aufs Rad gebunden, "ir gebein hiez man zerstozen": Hinrichtung, der Koerper ist beim Zerstoszen noch lebend'),
    'KCR_6020_1': ('tot', 'Gebein des erschlagenen Herrschers, begraben'),
    'KCR_26850_3': ('tot', '"ir gebaine solte begraben"'),
    'KCR_43000_4': ('tot', 'Leichnam, "die wolfe frazen sin gebaine"'),
    'KCR_62390_4': ('tot', 'Flaisc und Gebaine des Erschlagenen, "din sele ist hailich"'),
    'KCR_64800_4': ('tot', 'Heiliger, Reliquie'),
    'KCR_103950_3': ('tot', 'Reliquienaufzaehlung: "sancti mathie gebaine"'),
    'KCR_116160_2': ('tot', '"daz hailige gebaine", Reliquie'),
    'KCR_137630_5': ('tot', '"daz hailige gebaine", Reliquie'),
    'KCR_167880_3': ('tot', '"da ruowet sin gebaine"'),
    'LGR_5975000_1': ('tot', 'Gebein der getoeteten Heiden'),
    'LGR_6062000_7': ('tot', 'Leichen toter Koenige, "die toten kunige truoc man", das Fleisch wird vom Gebein gesotten'),
    'LGR_6066000_3': ('tot', 'derselbe Satzzusammenhang (Leichenpraeparation)'),
    'OVG_1945600_1': ('tot', 'Gebein des Koenigs Ludwig in der Erde'),
    'OVG_1948400_1': ('tot', 'Gebein, das aus der Erde erhoben werden soll'),
    'OVG_2829000_1': ('tot', 'Gebein auf den Altar gebracht, Reliquie'),
    'OVW_1021020260_2': ('lebend', 'Liebeslied: "leib gebaine", lebende Geliebte'),
    'OVW_1114050120_3': ('tot', 'Christus: "sein leib gebain in ainen stain gesteckt"'),
    'PUC_661271060_0': ('tot', 'Gebein ist nach Prag gebracht worden, Begraebnis'),
    'PUC_661311310_2': ('tot', 'Gebein nach dem Tod nach Prag gebracht'),
    'PUC_701391260_4': ('tot', 'Gebein nach dem Tod ins Kloster gebracht'),
    'REN_358990_1': ('tot', 'Reliquie, Gebein vom Altar erhoben'),
    'ROL_3841_3': ('lebend?', 'Kaempfer wollen die Heiden toeten, "ir unraine gebaine"; pars pro toto fuer lebende Feinde'),
    'ROL_8669_3': ('tot', '"ir uil heiligiz gebaine", Reliquie'),
    'RSP_1926_5': ('lebend', 'Aufzaehlung "fleisch und gebeyne, blud und herze", Anatomie'),
    'SAL_354030_1': ('tot', '"sin gebein ist mir recht liep", begraben in der Heidenschaft'),
    'SAX_154700_5': ('tot', 'heiliges Gebein des Jeremias'),
    'SAX_155800_3': ('tot', 'heiliges Gebein'),
    'SAX_349600_5': ('tot', 'Grab, Leichnam'),
    'SAX_351500_1': ('tot', 'Leichnam, "das gepain und das har"'),
    'SLG_8770_5': ('lebend', 'ein Lebender deckt "sin alt gebein" mit warmem Gewand zu'),
    'TRY_11371_4': ('lebend', 'Priamus ueber sich selbst: "min fleisch und min gebein"'),
    'TRY_12045_6': ('tot', 'Leichnam in den Marmorstein gelegt'),
    'TRY_17428_1': ('tot', 'Leichen sollen Voegeln und Hunden gegeben werden'),
    'WH_25909_5': ('tot', 'Gebein der Heiligen im Sarkophag'),
    'WL_227_3': ('lebend', 'Aussaetzige, Maden fressen das Fleisch "unz uf daz gebeine", von ihrem "bloeden libe" geht Gestank aus'),
    'WZB_53rb_12_4': ('tot', 'Josephs Gebeine werden mitgenommen'),
    'WZB_67rb_2_2': ('tot', 'Moses nimmt Josephs Gebeine mit'),
    'WZB_67rb_6_2': ('tot', 'Josephs Gebeine'),
}
ERWARTET = {'tot': 38, 'lebend': 12, 'lebend?': 3, 'Tier': 2}


def belege():
    ergebnis = []
    for pfad in sorted((ROOT / 'tei').glob('*.tei.xml')):
        t = pfad.read_text(encoding='utf-8')
        if SENSE not in t:
            continue
        body = t[t.index('<body'):]
        eintraege = []
        for attr, text, zeile in re.findall(r'<w\b([^>]*)>([^<]*)</w>|(<l[ >])', body):
            if zeile:
                eintraege.append(('', '', False, True))
                continue
            mi = re.search(r'xml:id="([^"]+)"', attr)
            ma = re.search(r'\bana="([^"]*)"', attr)
            treffer = bool(ma) and ma.group(1).split('#')[-1].split()[0] == SENSE
            eintraege.append((mi.group(1) if mi else '', text, treffer, False))
        for i, (wid, text, treffer, zeile) in enumerate(eintraege):
            if treffer:
                lo, hi = max(0, i - FENSTER), i + FENSTER + 1
                kontext = ' '.join('/' if e[3] else (f'[[{e[1]}]]' if k == i else e[1])
                                   for k, e in enumerate(eintraege[lo:hi], start=lo))
                ergebnis.append((wid, pfad.name.split('.')[0], text, kontext))
    return ergebnis


def main():
    liste = belege()
    ids = [b[0] for b in liste]
    if len(liste) != len(EINSTUFUNG) or set(ids) != set(EINSTUFUNG) or len(set(ids)) != len(ids):
        fehlt = sorted(set(EINSTUFUNG) - set(ids))
        zuviel = sorted(set(ids) - set(EINSTUFUNG))
        sys.exit(f'ABBRUCH: {len(liste)} Belege im Korpus, {len(EINSTUFUNG)} eingestuft; '
                 f'fehlen im Korpus {fehlt}, ohne Einstufung {zuviel}')
    zaehlung = Counter(k for k, _ in EINSTUFUNG.values())
    if dict(zaehlung) != ERWARTET:
        sys.exit(f'ABBRUCH: Zaehlung {dict(zaehlung)}, erwartet {ERWARTET}')
    print(f'{len(liste)} Belege an {SENSE}: ' + ', '.join(f'{k} {n}' for k, n in sorted(zaehlung.items())))
    if '--write' in sys.argv:
        with open(ZIEL, 'w', encoding='utf-8', newline='') as fh:
            fh.write('xml:id\tSigle\tForm\tKontext\tEinstufung\tBegründung\n')
            for wid, sigle, form, kontext in liste:
                klasse, grund = EINSTUFUNG[wid]
                fh.write(f'{wid}\t{sigle}\t{form}\t{kontext}\t{klasse}\t{grund}\n')
        print('geschrieben:', ZIEL.relative_to(ROOT))
    return 0


if __name__ == '__main__':
    sys.exit(main())
