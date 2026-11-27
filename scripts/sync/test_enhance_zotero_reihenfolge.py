#!/usr/bin/env python3
"""test_enhance_zotero_reihenfolge.py: Reihenfolge der Zotero-Items darf das
Ergebnis in works.xml nicht beeinflussen (#649).

Zwei Items mit derselben callNumber (wie HZ, KVM, FB) in beiden Reihenfolgen
durch extract_zotero_data und replace_editions_with_biblstructs. Die
biblStruct-Reihenfolge und die xml:id-Suffixe muessen gleich sein.

Aufruf: python -P -E scripts/sync/test_enhance_zotero_reihenfolge.py
"""
import importlib.util
import sys
from pathlib import Path

from lxml import etree

HIER = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("enh", HIER / "enhance_works_with_zotero.py")
enh = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enh)

WORKS = (
    '<TEI xmlns="http://www.tei-c.org/ns/1.0"><listBibl>'
    '<bibl xml:id="work_1"><idno type="sigle">XX</idno>'
    '<bibl type="edition">alt</bibl></bibl></listBibl></TEI>'
)


def item(key, titel, jahr):
    return {'key': key, 'data': {'itemType': 'book', 'callNumber': 'XX',
                                 'title': titel, 'date': jahr}}


# extract_zotero_data verlangt die Items aus SIGLE_ZU_ZOTERO_SCHLUESSEL
FLG = {'key': 'ATWPNQPS', 'data': {'itemType': 'book', 'callNumber': 'FLG1',
                                   'title': 'Flg', 'date': '1990'}}


def ergebnis(items):
    zd = enh.extract_zotero_data(items + [FLG])
    tree = etree.ElementTree(etree.fromstring(WORKS))
    enh.replace_editions_with_biblstructs(tree, zd)
    return etree.tostring(tree, method='c14n').decode('utf-8')


def main():
    a = item('AAAAAAAA', 'Erste Ausgabe', '1861')
    b = item('BBBBBBBB', 'Zweite Ausgabe', '1997')
    c = item('CCCCCCCC', 'Dritte Ausgabe', '2003')
    vor = ergebnis([a, b, c])
    rueck = ergebnis([c, b, a])
    misch = ergebnis([b, c, a])
    assert vor == rueck == misch, "Item-Reihenfolge der Eingabe schlaegt auf works.xml durch"
    # Die Reihenfolge ist die nach Key, mit Suffix-Kette in dieser Reihenfolge
    assert vor.index('Erste') < vor.index('Zweite') < vor.index('Dritte'), vor
    print("OK: drei Eingabereihenfolgen, ein Ergebnis")


if __name__ == "__main__":
    main()
    sys.exit(0)
