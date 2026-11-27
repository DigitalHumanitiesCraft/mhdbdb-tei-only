#!/usr/bin/env python3
"""test_apk.py: Tests fuer Stufe 0 der Hesler-Apokalypse (APK, #262).

Die Rohdatei apk_free.xml darf nicht ins Repository, auch nicht in Teilen als Fixture (Kickoff
apk-262). Die Mini-Fixture hier ist deshalb erfunden: Aufbau und Auszeichnung wie in der
Quelle (CSS-Vorspann, Doctype, TEI.2, div1/lg1/lg2, fw, hi, orig/lb, corr, pb, milestone),
der Wortlaut nicht aus ihr: kein sic- oder reg-Wert der Fixture steht in der Rohdatei, gemeinsam
sind nur kurze Wortfolgen aus allgemeinen Woertern wie "Daz ist" (geprueft am 19.11.2026 ueber jeden
sic- und reg-Wert und jede Folge aus zwei und drei Woertern). Gegen die echte Datei laufen die Bilanzen zusaetzlich, wenn sie da
ist (apk_common.rohdatei); fehlt sie, meldet der Test das als SKIP und nicht als bestanden.

Aufruf: python -P -E scripts/ingest/apk/test_apk.py
"""
import importlib.util
import sys
import traceback
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
import apk_common as ac  # noqa: E402

spec = importlib.util.spec_from_file_location("konv", HIER / "01-convert-apk-to-mhdbdb.py")
konv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(konv)
q = konv.q

CSS = ("@namespace html url(http://www.w3.org/1999/xhtml); :root { font:small Verdana; } "
       "* { display: block; } html|style { display: none; }")

FIXTURE = """<?xml version="1.0"?>
{css}
 <!DOCTYPE TEI.2 SYSTEM "mhg-tei.dtd">
<TEI.2> <teiHeader type="aacr2"> <fileDesc> <titleStmt> <title>Probe</title> </titleStmt>
 </fileDesc> </teiHeader> <text> <front> <titlePage> <docAuthor>Niemand</docAuthor>
 </titlePage> </front> <body> <div1 id="Apk"> <head/> <pb n="1"/>
 <lg1> <head><fw type="folio"><hi>[</hi><hi rend="superscript">*</hi><hi>1<hi
rend="superscript">r</hi>]</hi></fw> Diz ist ein probe.</head> <milestone n="1" unit="column"/>
 <lg2> <l n="1" id="Apk-00001"><fw type="folio"><hi>[1<hi rend="superscript">ra</hi>]</hi></fw>
 <hi rend="bold">E</hi>in ritter reit in <lb/>einen walt,</l>
 <l n="2" id="Apk-00002">Der was <orig reg="wunneclich">wunne- <lb/>clich</orig> und kalt;</l>
 <pb n="2"/> <milestone n="1" unit="column"/>
 <l n="3" id="Apk-00003"><hi rend="doublespace">Got sprach</hi>: dar <hi>i</hi>n gesche<hi
rend="superscript">e</hi>n!</l> </lg2>
 <lg2> <l n="4" id="Apk-00004">Daz ist engel<hi><corr resp="editor" sic="x"/></hi>ich (wol) <corr
resp="editor" sic="tagewerc">tage werc</corr></l>
 <l n="5" id="Apk-00005">Und rief -Da</l> </lg2> </lg1> </div1> </body> </text> </TEI.2>
"""

SOLL = {"l": 5, "lg2": 2, "pb": 2, "milestone": 2, "fw": 2, "orig": 1, "corr": 2, "lb": 2}


def daten(text=None):
    return ("﻿" + (text or FIXTURE.replace("{css}", CSS))).encode("utf-8")


def woerter(tei, n):
    l = next(x for x in tei.iter(q("l")) if x.get("n") == str(n))
    return ["".join(w.itertext()) for w in l.iter(q("w"))]


def erwarte_fehler(text, teil, soll=SOLL):
    try:
        konv.konvertiere(daten(text), soll)
    except ac.HarterFehler as e:
        assert teil in str(e), f"falscher Fehler: {e}"
        return
    raise AssertionError(f"kein Fehler, erwartet: {teil}")


def test_verszahl_und_kein_vers_verloren():
    tei, stat, _, quell = konv.konvertiere(daten(), SOLL)
    ziel = [l.get("n") for l in tei.iter(q("l"))]
    assert quell == ["1", "2", "3", "4", "5"], quell
    assert ziel == quell, ziel
    assert stat["section"] == 2 and stat["pb"] == 2 and stat["cb"] == 2


def test_css_block_entfernt():
    tei, stat, _, _ = konv.konvertiere(daten(), SOLL)
    from lxml import etree
    xml = etree.tostring(tei, encoding="unicode")
    assert "@namespace" not in xml and "Verdana" not in xml
    assert stat["css_zeichen"] == len(CSS)


def test_css_block_mit_markup_bricht_ab():
    erwarte_fehler(FIXTURE.replace("{css}", CSS + " <b>x</b>"), "CSS-Block")


def test_ohne_doctype_bricht_ab():
    erwarte_fehler(FIXTURE.replace("{css}", CSS).replace(' <!DOCTYPE TEI.2 SYSTEM "mhg-tei.dtd">', ""),
                   "Prolog unerwartet")


def test_luecke_in_der_verszaehlung_bricht_ab():
    t = FIXTURE.replace("{css}", CSS).replace('<l n="3" id="Apk-00003">', '<l n="7" id="Apk-00007">')
    erwarte_fehler(t, "lueckenlos")


def test_vers_id_passt_nicht_bricht_ab():
    t = FIXTURE.replace("{css}", CSS).replace('id="Apk-00002"', 'id="Apk-00020"')
    erwarte_fehler(t, "Vers-ID")


def test_fehlender_vers_bricht_ab():
    # ein Vers weniger als erwartet: die Bestandspruefung schlaegt an, bevor etwas geschrieben wird
    t = FIXTURE.replace("{css}", CSS).replace('\n <l n="5" id="Apk-00005">Und rief -Da</l>', "")
    erwarte_fehler(t, "Bestand weicht ab")


def test_unbekanntes_element_bricht_ab():
    t = FIXTURE.replace("{css}", CSS).replace("Und rief", "Und <foreign>rief</foreign>")
    erwarte_fehler(t, "unbekannte Elemente")


def test_abbildung():
    tei, stat, protokoll, _ = konv.konvertiere(daten(), SOLL)
    # Initiale im Wort, Druckzeilenwechsel zwischen Woertern faellt weg
    assert woerter(tei, 1) == ["Ein", "ritter", "reit", "in", "einen", "walt"]
    # Trennung am Druckzeilenende aufgehoben, ein <w>
    assert woerter(tei, 2) == ["Der", "was", "wunneclich", "und", "kalt"]
    assert stat["orig_abweichend"] == 0 and not protokoll
    # Kursive und Hochstellung im Wort, Sperrung je Wort
    assert woerter(tei, 3) == ["Got", "sprach", "dar", "in", "gescheen"]
    # leere Korrektur mitten im Wort trennt das Wort nicht; Korrektur ueber zwei Woerter
    assert woerter(tei, 4) == ["Daz", "ist", "engelich", "wol", "tage", "werc"]
    # Strich am Wortrand ist <pc>
    assert woerter(tei, 5) == ["Und", "rief", "Da"]
    l5 = next(x for x in tei.iter(q("l")) if x.get("n") == "5")
    assert [(p.text, p.get("join")) for p in l5.iter(q("pc"))] == [("-", "right")]
    # fw -> cb mit dem Text der eckigen Klammer
    assert [c.get("n") for c in tei.iter(q("cb"))] == ["*1r", "1ra"]
    assert all(c.get("type") == "manuscript" for c in tei.iter(q("cb")))
    assert [p.get("n") for p in tei.iter(q("pb"))] == ["1", "2"]
    assert all(p.get("type") == "edition" for p in tei.iter(q("pb")))
    # keine Einrueckung im Wort
    w = next(next(tei.iter(q("l"))).iter(q("w")))
    assert w.text is None and w[0].text == "E" and w[0].tail == "in"
    # Korrekturen als Kommentar hinter dem Wort, mit der Auszeichnung der Vorlage
    from lxml import etree
    kommentare = [c.text for c in tei.iter(etree.Comment)]
    assert ' apk_free.xml: <corr resp="editor" sic="x"></corr> ' in kommentare, kommentare
    assert ' apk_free.xml: <corr resp="editor" sic="tagewerc">tage werc</corr> ' in kommentare
    # Rubrik im <head>, xml:id mit Vers 0
    head = next(tei.iter(q("head")))
    assert [w.get("{http://www.w3.org/XML/1998/namespace}id") for w in head.iter(q("w"))] == \
        ["APK_0_0", "APK_0_1", "APK_0_2", "APK_0_3"]
    # Klammern: oeffnend join=right, schliessend left
    l4 = next(x for x in tei.iter(q("l")) if x.get("n") == "4")
    assert [(p.text, p.get("join")) for p in l4.iter(q("pc"))] == [("(", "right"), (")", "left")]


def test_echte_datei():
    try:
        _, roh = ac.rohdatei()
    except ac.HarterFehler as e:
        return f"SKIP ({e})"
    tei, stat, _, quell = konv.konvertiere(roh, konv.SOLL)
    ziel = [l.get("n") for l in tei.iter(q("l"))]
    assert len(quell) == 23254 and ziel == quell
    assert [str(i) for i in range(1, 23255)] == ziel
    return f"ok, {len(ziel)} Verse in Quelle und Ziel, {stat['w']} <w>"


def main():
    ac.ausgabe_utf8()
    fehler = 0
    tests = [(n, f) for n, f in sorted(globals().items()) if n.startswith("test_") and callable(f)]
    for name, f in tests:
        try:
            r = f()
            print(f"{name}: {r or 'ok'}")
        except Exception:  # noqa: BLE001
            fehler += 1
            print(f"{name}: FEHLER")
            traceback.print_exc()
    print(f"{len(tests) - fehler} von {len(tests)} Tests ohne Fehler")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
