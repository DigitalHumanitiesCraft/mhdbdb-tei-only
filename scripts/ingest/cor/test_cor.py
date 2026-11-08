#!/usr/bin/env python3
"""test_cor.py: Mini-Fixtures fuer den CoReMA-Konverter (#139).

Aufruf: python -P -E scripts/ingest/cor/test_cor.py
"""
import collections
import importlib.util
import sys
from pathlib import Path

from lxml import etree

HIER = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("conv", HIER / "01-convert-corema-to-mhdbdb.py")
conv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conv)

NS = 'xmlns="http://www.tei-c.org/ns/1.0"'


def body(inhalt):
    return etree.fromstring(f"<body {NS}><div>{inhalt}</div></body>")


def lauf(inhalt):
    z = conv.Zustand("COR_T")
    einheiten = conv.baue_einheiten(body(inhalt), collections.Counter())
    return conv.baue_body(einheiten, z), z


def fehler(inhalt):
    try:
        lauf(inhalt)
    except conv.HarterFehler as e:
        return str(e)
    raise AssertionError("harter Fehler erwartet")


def test_zerlegung():
    assert conv.zerlege("muosz. vnd , \"x\" 1/2 ..") == [
        ("w", "muosz", 0, 5), ("pc", ".", 5, 6), ("w", "vnd", 7, 10), ("pc", ",", 11, 12),
        ("pc", '"', 13, 14), ("w", "x", 14, 15), ("pc", '"', 15, 16), ("w", "1/2", 17, 20),
        ("pc", ".", 21, 22), ("pc", ".", 22, 23)]


def test_rezept_mit_kopf_und_pb():
    b, z = lauf('<ab xml:id="t.1" n="1" type="recipe"><pb n="1r"/><title key="k">Ein <name>muos</name></title> . '
                '<instruction>nim <ingredient commodity="Q1" en="x">salz</ingredient></instruction>'
                '<note xml:lang="de">Anm.</note></ab>')
    div = b[0][0]
    assert div.get("type") == "recipe" and div.get("n") == "1"
    assert [etree.QName(c).localname for c in div] == ["pb", "head", "p"], [c.tag for c in div]
    assert [w.text for w in div[1]] == ["Ein", "muos"]
    assert [etree.QName(c).localname for c in div[2]] == ["pc", "w", "w", "note"]
    assert div[2][3].get("type") == "editorial-de" and div[2][3].text == "Anm."
    assert div[1][0].get("{http://www.w3.org/XML/1998/namespace}id") == "COR_T_1r_1"
    arten = collections.Counter(r["art"] for r in z.zeilen)
    assert arten == {"ab": 1, "title": 1, "name": 1, "instruction": 1, "ingredient": 1}, arten
    zeile = next(r for r in z.zeilen if r["art"] == "ingredient")
    assert zeile["von"] == zeile["bis"] == "COR_T_1r_5" and zeile["attribute"] == "commodity=Q1 | en=x"


def test_element_in_notiz():
    b, z = lauf('<ab xml:id="t.1" n="1" type="recipe">a b<note xml:lang="en">Siehe <ref target="#t.2">x</ref>.</note></ab>')
    assert z.note_texte == ["Siehe x."]
    zeile = next(r for r in z.zeilen if r["art"] == "note/ref")
    assert zeile["von"] == zeile["bis"] == "COR_T_0_2" and zeile["attribute"] == "target=#t.2" and zeile["text"] == "x"
    assert "unbekanntes Element <name> in <note>" in fehler(
        '<ab xml:id="t.1" n="1" type="recipe">a<note>n <name>x</name></note></ab>')
    assert "unbekanntes Attribut 'foo'" in fehler(
        '<ab xml:id="t.1" n="1" type="recipe">a<note>n <ref foo="1">x</ref></note></ab>')


def test_pb_im_wort_hinter_das_wort():
    b, z = lauf('<ab xml:id="t.1" n="1" type="recipe"><instruction>ge<pb n="2r"/>soten ist</instruction></ab>')
    p = b[0][0][0]
    assert [etree.QName(c).localname for c in p] == ["w", "pb", "w"] and p[0].text == "gesoten"
    assert z.stat["pb_im_wort"] == 1


def test_verschachtelte_ab():
    b, z = lauf('<ab xml:id="t.1" n="1" type="recipe">a <ab xml:id="t.1.s" n="1" type="recipe" '
                'subtype="subrecipe">b</ab> c</ab>')
    div = b[0][0]
    assert [etree.QName(c).localname for c in div] == ["p", "div", "p"]
    assert [w.text for w in div.iter("{http://www.tei-c.org/ns/1.0}w")] == ["a", "b", "c"]


def test_harte_fehler():
    assert "unbekanntes Element <hi>" in fehler('<ab xml:id="t.1" n="1" type="recipe"><hi>x</hi></ab>')
    assert "unbekanntes Attribut 'foo'" in fehler(
        '<ab xml:id="t.1" n="1" type="recipe"><ingredient foo="1">x</ingredient></ab>')
    assert "unbekanntes Element <p>" in fehler('<p>x</p>')
    assert "Text direkt im aeusseren" in fehler('lose <pb n="1r"/>')
    assert "Text zwischen den Kindern" in fehler('<pb n="1r"/>lose')


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    n = 0
    for name, f in sorted(globals().items()):
        if name.startswith("test_") and callable(f):
            f()
            n += 1
            print(f"ok {name}")
    print(f"VERDICT: {n} Tests gruen")


if __name__ == "__main__":
    main()
