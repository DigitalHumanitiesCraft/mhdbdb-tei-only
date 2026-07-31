#!/usr/bin/env python3
"""Autorangaben im titleStmt gegen persons.xml pruefen (#228).

Anlass: sieben Texte trugen ein <author ref="#person_N"/> OHNE Textinhalt.
Die Referenz war intakt, nur der Name fehlte, und im Frontend erschienen die
Texte dadurch ohne Autor. Der Fall war jahrelang unsichtbar, weil ihn nichts
geprueft hat: die Referenz loest ja auf, und ein leeres Element ist
schema-valide (mhdbdb.rnc verlangt keinen Textinhalt).

Geprueft wird das Feld, aus dem der Korpus-Index text.author speist
(build-corpus-index.py, //tei:titleStmt/tei:author). Vier Klassen:

  leer        <author ref="..."/> ohne Textinhalt: Text erscheint autorlos
  toter-ref   @ref zeigt auf eine ID, die es in persons.xml nicht gibt
  praefix     @ref traegt den Dateinamen ("persons.xml#person_N"). Erlaubt,
              aber im Korpus die Ausnahme; der Rest schreibt "#person_N"
  abweichend  Textinhalt != preferred-Name der referenzierten Person

Nur "leer" und "toter-ref" sind eindeutig Fehler. "abweichend" ist oft eine
legitime bibliographische Variante und braucht eine fachliche Entscheidung,
deshalb meldet das Skript es getrennt und ohne Exit-Code.

Usage:
    python scripts/audit/check-author-refs.py           # Bericht
    python scripts/audit/check-author-refs.py --check   # exit 1 bei leer/toter-ref
"""
import argparse
import sys
from pathlib import Path

from lxml import etree

# Gemeinsame Korpusauswahl (#287).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corpus_files import corpus_files  # noqa: E402

NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


def preferred_names(root: Path) -> dict:
    tree = etree.parse(str(root / 'authority-files' / 'persons.xml'))
    out = {}
    for person in tree.xpath('//tei:person', namespaces=NS):
        pid = person.get('{http://www.w3.org/XML/1998/namespace}id')
        name = person.xpath('./tei:persName[@type="preferred"]/text()', namespaces=NS)
        out[pid] = name[0].strip() if name else ''
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--check', action='store_true',
                    help='exit 1, wenn ein leeres oder totes @ref gefunden wird')
    args = ap.parse_args()

    root = Path(__file__).resolve().parents[2]
    pref = preferred_names(root)

    leer, tot, praefix, abweichend, ohne_ref = [], [], [], [], []
    for path in corpus_files():
        sigle = path.name.replace('.tei.xml', '')
        tree = etree.parse(str(path))
        for author in tree.xpath('//tei:titleStmt/tei:author', namespaces=NS):
            text = ''.join(author.itertext()).strip()
            raw = author.get('ref') or ''
            if not raw:
                ohne_ref.append((sigle, text))
                continue
            if '#' in raw and not raw.startswith('#'):
                praefix.append((sigle, raw))
            pid = raw.split('#')[-1]
            if pid not in pref:
                tot.append((sigle, raw))
                continue
            if not text:
                leer.append((sigle, pid))
            elif ' '.join(text.split()) != pref[pid]:
                abweichend.append((sigle, pid, ' '.join(text.split()), pref[pid]))

    print(f'Geprueft: {len(corpus_files())} Korpusdateien')
    print()
    print(f'  leer (ohne Textinhalt)       {len(leer)}')
    for sigle, pid in leer:
        print(f'      {sigle:6} {pid}')
    print(f'  toter @ref                   {len(tot)}')
    for sigle, raw in tot:
        print(f'      {sigle:6} {raw}')
    print(f'  @ref ohne #-Praefixform      {len(praefix)}')
    for sigle, raw in praefix:
        print(f'      {sigle:6} {raw}')
    print(f'  ohne @ref                    {len(ohne_ref)}')
    for sigle, text in ohne_ref:
        print(f'      {sigle:6} {text!r}')
    print()
    print(f'  Text weicht vom preferred-Namen ab: {len(abweichend)}')
    print('      (kein Fehler an sich, aber jeder Fall ist eine Entscheidung)')
    for sigle, pid, text, name in abweichend:
        print(f'      {sigle:6} {pid:12} TEI {text!r} <-> persons.xml {name!r}')

    if args.check and (leer or tot):
        sys.exit(1)


if __name__ == '__main__':
    main()
