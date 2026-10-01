#!/usr/bin/env python3
"""Gattungen im TEI-Kopf gegen die Gattungen des Werks pruefen (#495).

Jeder Kopf traegt eine Gattungsklassifikation in
classDecl/taxonomy[@xml:id="genres"]/category, jede category mit xml:id und
@corresp auf genres.xml; uebergeordnete Gattungen tragen ana="parent".
Gelesen wird sie nur als Rueckfall in der Leseansicht (tei-text-reader.js,
wenn kein Werk aufloest). Index, Suche und Gattungsfilter nehmen die Gattung
ueber das Werk: msIdentifier/@corresp -> works.xml -> ptr auf genres.xml.
Eine Gattung, die nur im Kopf steht, kommt deshalb nirgends an, und bis #495
hat das niemand geprueft: geschrieben wird der Block beim Ingest
(scripts/ingest/ari/, scripts/ingest/frauenlob/, 2025 von
scripts/_archived/tei-transformation.py), danach gleicht ihn kein
Sync-Skript mehr ab.

Die Invariante, gemessen am 01.10.2026 ueber alle 667 Dateien:

  Hauptgattungen des Kopfs  <=  Werkgattungen  <=  Haupt- und Elterngattungen des Kopfs

Die rechte Haelfte laesst Elterngattungen des Kopfs zu, die nicht im Werk
stehen (sie stammen aus dem RDF-Feld genreFormMainParent und lassen sich aus
genres.xml nicht eindeutig ableiten), und sie laesst zu, dass der Kopf eine
Werkgattung als Elterngattung fuehrt: das tun 82 Koepfe, etwa AML.

Fehlerklassen, alle mit Exit 1 unter --check:

  ohne-werk      msIdentifier/@corresp fehlt oder loest in works.xml nicht auf
  ohne-taxonomie kein category-Element unter taxonomy[@xml:id="genres"],
                 obwohl das Werk Gattungen hat
  unbekannt      category/@xml:id steht nicht in genres.xml
  corresp        category/@corresp ist nicht "genres.xml#" plus die xml:id
  kopf-mehr      Hauptgattung im Kopf, die das Werk nicht fuehrt: sie kommt
                 im Index nicht an
  werk-mehr      Werkgattung, die der Kopf weder als Haupt- noch als
                 Elterngattung fuehrt
  veraltet       eine Ausnahme aus AUSNAHMEN trifft nicht mehr genau zu

Usage:
    python scripts/audit/check-header-genres.py           # Bericht
    python scripts/audit/check-header-genres.py --check   # exit 1 bei jedem Befund
"""
import argparse
import sys
from pathlib import Path

from lxml import etree

# Gemeinsame Korpusauswahl (#287).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corpus_files import corpus_files  # noqa: E402

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}
XID = '{http://www.w3.org/XML/1998/namespace}id'

# Bekannte kopf-mehr-Faelle, benannt statt gezaehlt. Die Ausnahme haengt an
# genau dieser Menge zusaetzlicher Gattungen: kommt eine dazu oder faellt eine
# weg, greift sie nicht mehr und der Fall wird als veraltet gemeldet.
FRAUENDIENST = frozenset({'genre_4ecfe25e', 'genre_e513a99c'})  # Minnesang, Brief
_GRUND_FD = ('Frauendienst (work_6): der Kopf fuehrt Minnesang und Brief, das Werk '
             'nur Liebesroman und Abenteuerroman. Ob work_6 die beiden bekommt oder '
             'die Koepfe gekuerzt werden, liegt bei KZW (#495).')
AUSNAHMEN = {s: (FRAUENDIENST, _GRUND_FD) for s in ('FD', 'FDS', 'FH', 'FLD', 'FP')}


def werk_gattungen(root: Path) -> dict:
    tree = etree.parse(str(root / 'authority-files' / 'works.xml'))
    out = {}
    for bibl in tree.xpath('//tei:bibl[starts-with(@xml:id, "work_")]', namespaces=NS):
        out[bibl.get(XID)] = {
            p.get('target').split('#', 1)[1]
            for p in bibl.xpath('./tei:ptr[starts-with(@target, "genres.xml#")]', namespaces=NS)
        }
    return out


def bekannte_gattungen(root: Path) -> set:
    tree = etree.parse(str(root / 'authority-files' / 'genres.xml'))
    return set(tree.xpath('//tei:category/@xml:id', namespaces=NS))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true', help='exit 1 bei jedem Befund')
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    werke = werk_gattungen(root)
    bekannt = bekannte_gattungen(root)
    if not werke or not bekannt:
        sys.exit('ABBRUCH: works.xml oder genres.xml ohne Eintraege gelesen')

    befunde = {k: [] for k in ('ohne-werk', 'ohne-taxonomie', 'unbekannt', 'corresp',
                               'kopf-mehr', 'werk-mehr', 'veraltet')}
    dateien = corpus_files()
    deckungsgleich = 0
    ausnahme_genutzt = set()
    for path in dateien:
        sigle = path.name.replace('.tei.xml', '')
        kopf = etree.parse(str(path)).find('tei:teiHeader', NS)
        werkref = kopf.xpath('.//tei:msIdentifier/@corresp', namespaces=NS)
        wid = werkref[0].split('#', 1)[-1] if werkref else None
        if wid not in werke:
            befunde['ohne-werk'].append((sigle, wid or '(kein @corresp)'))
            continue
        kats = kopf.xpath('.//tei:classDecl/tei:taxonomy[@xml:id="genres"]/tei:category',
                          namespaces=NS)
        if not kats and werke[wid]:
            befunde['ohne-taxonomie'].append((sigle, wid))
            continue
        haupt, eltern = set(), set()
        for k in kats:
            gid = k.get(XID)
            if gid not in bekannt:
                befunde['unbekannt'].append((sigle, gid))
            if k.get('corresp') != f'genres.xml#{gid}':
                befunde['corresp'].append((sigle, gid, k.get('corresp')))
            (eltern if k.get('ana') == 'parent' else haupt).add(gid)
        mehr = haupt - werke[wid]
        fehlt = werke[wid] - haupt - eltern
        if sigle in AUSNAHMEN:
            erwartet, _ = AUSNAHMEN[sigle]
            if mehr == erwartet:
                ausnahme_genutzt.add(sigle)
                mehr = set()
            else:
                befunde['veraltet'].append((sigle, sorted(mehr), sorted(erwartet)))
        if mehr:
            befunde['kopf-mehr'].append((sigle, wid, sorted(mehr)))
        if fehlt:
            befunde['werk-mehr'].append((sigle, wid, sorted(fehlt)))
        if not mehr and not fehlt and sigle not in ausnahme_genutzt:
            deckungsgleich += 1
    for sigle in sorted(set(AUSNAHMEN) - {p.name.replace('.tei.xml', '') for p in dateien}):
        befunde['veraltet'].append((sigle, 'Datei fehlt im Korpus', ''))

    print(f'Geprueft: {len(dateien)} Korpusdateien, {len(werke)} Werke, '
          f'{len(bekannt)} Gattungen in genres.xml')
    print(f'  Kopf deckt das Werk          {deckungsgleich}')
    print(f'  bekannte Ausnahme            {len(ausnahme_genutzt)}')
    for name, faelle in befunde.items():
        print(f'  {name:28} {len(faelle)}')
        for f in faelle:
            print('      ' + '  '.join(str(x) for x in f))
    print()
    for sigle, (_, grund) in sorted(AUSNAHMEN.items()):
        if sigle in ausnahme_genutzt:
            print(f'  Ausnahme, bewusst: {sigle} - {grund}')

    if args.check and any(befunde.values()):
        sys.exit(1)


if __name__ == '__main__':
    main()
