#!/usr/bin/env python3
"""Tests fuer 02-convert-wiki-to-mhdbdb.py (BRE, #147), pytest-frei.

Aufruf: python -P -E scripts/ingest/bre/test_bre.py
Die meisten Tests laufen ohne Netz und ohne Cache auf einer Mini-Fixture (Ausschnitt aus Cgm 713,
Revision 21352). Den Wiki-Cache `temp/bre-wiki` brauchen das Druckfahnen-Gate und die fuenf
Sperre-Tests, die `konvertiere` direkt aufrufen; fehlt er, schlagen sie fehl. Der Test "alle bricht
vor dem ersten Schreiben ab" besteht ohne Cache auch dann, wenn die Vorpruefung in `main` fehlt (dann
bricht die erste Konversion am fehlenden Cache ab), sein Befund zaehlt nur mit Cache.
Beendet mit Exit 1, wenn ein Test fehlschlaegt.
"""
import collections
import importlib.util
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))
spec = importlib.util.spec_from_file_location("conv", HIER / "02-convert-wiki-to-mhdbdb.py")
conv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conv)

SEITE = """==Signatur==
Test, Cgm 713, 188r-188v

==Transkription<ref>Richtlinien</ref>==

[188r]<br />
<span style="color:#FF0000">Der Segen</span><br />
<span style="color:#FF0000">Gr</span>üß dich got<br />
Mit her(r) v(er)stoppffen<br />
Selig sey der wirth der schen-<br />

[188v]<br />
ken hat erdacht<br />
Gesegen dich got und kum schier <span style="color:#FF0000">h</span>ierwider<br />

<span style="color:#FF0000">N</span>u grüß dich zwei<br />
zweite zeile<br />

==Anmerkungen==
<references />
"""

ROWS = [
    {"text_titel": "A", "editionssigle": "B", "signatur_label": "Cgm 713", "blatt": "188r",
     "erster_vers": "Grüß dich got", "ueberschrift": "Der Segen"},
    {"text_titel": "B", "editionssigle": "B", "signatur_label": "Cgm 713", "blatt": "188v",
     "erster_vers": "Nu grüß dich zwei", "ueberschrift": ""},
]
SEITE_META = {"titel": "Weingrüße Cgm 713", "revid": 21352, "timestamp": "2026-01-01T00:00:00Z"}

fehler = []


def pruefe(name, bedingung, detail=""):
    if not bedingung:
        fehler.append(f"{name}: {detail}")
        print(f"FAIL {name} {detail}")
    else:
        print(f"ok   {name}")


def baue(seite=SEITE, rows=ROWS, sigle="B"):
    signatur, items, noten, info = conv.lies_transkription(seite)
    lex = {i: conv.lexe(it["raw"], noten, f"Zeile {it['lines'][0]}")
           for i, it in enumerate(items) if it["kind"] == "verse"}
    texte, faltungen, vorspann = conv.segmentiere(items, lex, rows, sigle)
    stat = {"w": 0, "l": 0, "head": 0, "pb": 0, "pb_im_wort": 0, "note": 0,
            "el": collections.Counter(), "span_dupliziert": collections.Counter()}
    tei, _, erwartet = conv.baue_tei("BRE_TEST", signatur, SEITE_META, items, lex, texte, stat,
                                     vorspann, "2026-01-01")
    return items, texte, tei, info, faltungen


items, texte, tei, info, _ = baue()
ns = {"t": conv.TEI_NS}
x = lambda p: tei.xpath(p, namespaces=ns)  # noqa: E731

pruefe("zwei Texte", len(texte) == 2 and len(x("//t:div[@type='section']")) == 2)
pruefe("Text A: Kopfzeile erkannt", len(texte[0]["heads"]) == 1)

# Lombarde im Wort: <w><hi rend="inkRed">Gr</hi>üß</w>, ein einziges Wort
w = x("//t:w[starts-with(@xml:id,'BRE_TEST_188r_2_0')]")
pruefe("Lombarde im Wort", len(w) == 1 and w[0].xpath("string(.)") == "Grüß"
       and len(w[0]) == 1 and w[0][0].get("rend") == "inkRed" and w[0][0].text == "Gr",
       etree_str := (conv.etree.tostring(w[0]).decode() if w else "kein Wort"))

# wortinterne Abkuerzung: v<expan>er</expan>stoppffen
v = [e for e in x("//t:w") if e.xpath("string(.)") == "verstoppffen"]
pruefe("wortinterne Abkuerzung", len(v) == 1 and v[0].find(conv.q("expan")) is not None
       and v[0].text == "v" and v[0][0].tail == "stoppffen")

# Worttrennung ueber Seitenwechsel: ein <w> mit <pb> darin, ein Vers
sch = [e for e in x("//t:w") if e.xpath("string(.)") == "schenken"]
pruefe("Worttrennung: ein Wort mit pb", len(sch) == 1 and sch[0].find(conv.q("pb")) is not None
       and sch[0].find(conv.q("pb")).get("n") == "188v")
pruefe("Worttrennung: ein Vers", info["fortsetzungen"] == 1
       and sch[0].getparent().xpath("string(.)") == "Seligseyderwirthderschenkenhaterdacht")
pruefe("Folgewort auf neuer Seite", sch[0].getparent().xpath("t:w[last()]/@xml:id", namespaces=ns)[0]
       == "BRE_TEST_188v_1_2")  # 'ken' ist Index 0 der neuen Zeile

# Schlussformel beginnt keinen neuen Text und bleibt in Text A
a = x("//t:div[@n='1']/t:l")
pruefe("Schlussformel in Text A", a and a[-1].xpath("string(.)").startswith("Gesegendichgot")
       and len(a) == 4, f"{len(a)} Verse in A")
pruefe("Text B: zwei Verse", len(x("//t:div[@n='2']/t:l")) == 2)

# Gegenprobe: jede Quellzeile genau einmal
pruefe("Zeilenbilanz", len(x("//t:l")) + len(x("//t:head")) + info["fortsetzungen"] == info["stuecke"])

# Unbekannte Eingabe ist ein harter Fehler
try:
    conv.lexe("a <span style=\"color:blue\">b</span>", [], "test")
    pruefe("unbekanntes Tag", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("unbekanntes Tag", True)
try:
    conv.lexe("a (b", [], "test")
    pruefe("offene Klammer", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("offene Klammer", True)

# Zeile vor dem ersten Textanfang ist ein harter Fehler
try:
    s2 = SEITE.replace("[188r]<br />\n", "[188r]<br />\nvorspann zeile<br />\n", 1)
    sig, it2, no2, _ = conv.lies_transkription(s2)
    lex2 = {i: conv.lexe(t["raw"], no2, "t") for i, t in enumerate(it2) if t["kind"] == "verse"}
    conv.segmentiere(it2, lex2, ROWS, "B")
    pruefe("Zeile vor Textanfang", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("Zeile vor Textanfang", True)

# Vorspann 1: Reihentitel (Zeuge S, Zeile aus bre_common.VORSPANN) -> <head> des aeusseren <div>
titel = conv.bc.VORSPANN["S"][1][0]
s_titel = SEITE.replace("[188r]<br />\n", f"[188r]<br />\n{titel}<ref>Holzschnitt</ref><br />\n", 1)
_, texte_s, tei_s, info_s, _ = baue(s_titel, ROWS, "S")
aussen = tei_s.xpath("//t:body/t:div", namespaces=ns)[0]
pruefe("Reihentitel: head im aeusseren div vor dem ersten Abschnitt",
       aussen[1].tag == conv.q("head") and "".join(aussen.xpath("t:head/t:w/text()", namespaces=ns)) == titel.replace(" ", "")
       and aussen.xpath("t:head/t:note", namespaces=ns)[0].text == "Holzschnitt"
       and len(tei_s.xpath("//t:div[@type='section']", namespaces=ns)) == 2,
       conv.etree.tostring(aussen).decode()[:300])
# Vorspann 2: unerwarteter Vorspann (Zeuge B hat keinen) und fehlender Vorspann (Zeuge S ohne Titel)
try:
    baue(s_titel, ROWS, "B")
    pruefe("unerwarteter Vorspann", False, "kein Fehler")
except conv.bc.HarterFehler as e:
    pruefe("unerwarteter Vorspann", "Vorspann weicht" in str(e), str(e)[:80])
try:
    baue(SEITE, ROWS, "S")
    pruefe("fehlender Vorspann", False, "kein Fehler")
except conv.bc.HarterFehler as e:
    pruefe("fehlender Vorspann", "Vorspann weicht" in str(e), str(e)[:80])
# Vorspann 3: Fragment (Zeuge R) -> eigener Abschnitt ohne head, mit editorial note, Zaehlung getrennt
frag = "\n".join(l + "<br />" for l in conv.bc.VORSPANN["R"][1])
s_frag = SEITE.replace("[188r]<br />\n", f"[188r]<br />\n{frag}\n", 1)
_, texte_r, tei_r, info_r, _ = baue(s_frag, ROWS, "R")
d1 = tei_r.xpath("//t:div[@type='section'][1]", namespaces=ns)[0]
pruefe("Fragment: eigener Abschnitt ohne head, mit Notiz",
       len(texte_r) == 2 and len(tei_r.xpath("//t:div[@type='section']", namespaces=ns)) == 3
       and not d1.xpath("t:head", namespaces=ns) and len(d1.xpath("t:l", namespaces=ns)) == 3
       and d1.xpath("t:note[@type='editorial']", namespaces=ns)[0].text
       == conv.bc.VORSPANN_NOTIZ["fragment"].format(werk="Weinsegen Allerliebster Trost"))
# R ist laut Hauptseite ein Fragment von Weinsegen Allerliebster Trost (#147, 2026-11-12)
pruefe("Fragment R: Werk laut Hauptseite statt 'keiner Einzeltextseite zugeordnet'",
       conv.bc.VORSPANN_WERK["R"] == "Weinsegen Allerliebster Trost"
       and "Weinsegen Allerliebster Trost" in d1.xpath("t:note", namespaces=ns)[0].text
       and "zugeordnet" not in conv.bc.VORSPANN_NOTIZ["fragment"]
       and any("Weinsegen Allerliebster Trost (Fragment)" in c.text for c in
               tei_r.xpath("//comment()")), str(tei_r.xpath("//comment()")))
# Fragment ohne Werkzuordnung ist ein harter Fehler
alt = dict(conv.bc.VORSPANN_WERK)
conv.bc.VORSPANN_WERK.clear()
try:
    baue(s_frag, ROWS, "R")
    pruefe("Fragment ohne VORSPANN_WERK", False, "kein Fehler")
except conv.bc.HarterFehler as e:
    pruefe("Fragment ohne VORSPANN_WERK", "Werkzuordnung" in str(e))
finally:
    conv.bc.VORSPANN_WERK.update(alt)

# Hauptseite: Liste je Zeuge, Uebersichtstabelle, Abgleich (Fixture: konstruierter Ausschnitt)
bh = conv.bh
HAUPT = """== Überlieferung ==

=== Handschriften ===
;B
:[[Weingrüße Cgm 713|X]]; Auf den Seiten 1r sind 2 Weingrüße aufgeführt:

#[[Weingruß Edels Getranck]]
#[[Weinsegen Edle Leibsalb]] (als Gruß ausgeführt)

;R
:Text:

#[[Weinsegen Allerliebster Trost]] (nur die letzten drei Verse)
#[[Weingruß Neczen Gumen]]

:In weitem Abstand:

#[[Biergruß Liebes Pir]]

;d<sup>6</sup>
:Text:

#[[Weingruß Edels Getranck]]
#([[Weingruß Allerliebster Trunck]])

;Darüber hinaus sind Weingrüße in einer Handschrift unbekannt.

=== Übersicht der Überlieferung ===
"""
hs = bh.parse(HAUPT)
pruefe("Hauptseite: Zeugen und Listen", list(hs) == ["B", "R", "d6"] and len(hs["B"]) == 2
       and [h["teil"] for h in hs["R"]] == [1, 1, 2], str({k: len(v) for k, v in hs.items()}))
pruefe("Hauptseite: Anmerkung und Klammer",
       hs["R"][0]["anmerkung"] == "(nur die letzten drei Verse)" and not hs["R"][0]["klammer"]
       and hs["d6"][1]["klammer"] and hs["B"][1]["anmerkung"] == "(als Gruß ausgeführt)")
pruefe("Abgleich: gleich", bh.abgleich("B", hs["B"], ["Weingruß Edels Getranck (Hans Rosenplüt)",
                                                      "Weinsegen Edle Leibsalb"], None) == [])
pruefe("Abgleich: R ohne Fragment = Abweichung nur_hauptseite",
       [x["art"] for x in bh.abgleich("R", hs["R"], ["Weingruß Neczen Gumen", "Biergruß Liebes Pir"], None)]
       == ["nur_hauptseite"])
pruefe("Abgleich: R mit Fragment = gleich",
       bh.abgleich("R", hs["R"], ["Weinsegen Allerliebster Trost", "Weingruß Neczen Gumen",
                                  "Biergruß Liebes Pir"], None) == [])
pruefe("Abgleich: Reihenfolge",
       [x["art"] for x in bh.abgleich("B", hs["B"], ["Weinsegen Edle Leibsalb",
                                                     "Weingruß Edels Getranck"], None)] == ["reihenfolge"])
pruefe("Abgleich: Klammertext als eigener Abschnitt",
       [x["art"] for x in bh.abgleich("d6", hs["d6"], ["Weingruß Edels Getranck",
                                                       "Weingruß Allerliebster Trunck"], None)]
       == ["klammer_aber_abschnitt"])
pruefe("Abgleich: Text nur in der Segmentierung",
       [x["art"] for x in bh.abgleich("B", hs["B"], ["Weingruß Edels Getranck", "Weinsegen Edle Leibsalb",
                                                     "Pseudo-Weingruß X"], None)] == ["nur_bisher"])
try:
    bh.parse(HAUPT.replace(";R\n", ";Q\n", 1))
    pruefe("Hauptseite: unbekannter Zeuge", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("Hauptseite: unbekannter Zeuge", True)
try:
    bh.parse(HAUPT.replace("#[[Weingruß Neczen Gumen]]", "# Weingruß Neczen Gumen ohne Link", 1))
    pruefe("Hauptseite: Listenzeile ohne Link", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("Hauptseite: Listenzeile ohne Link", True)
# Schluessel einer geprueften Abweichung tragen den Inhalt (Probe des Reviewers, Runde 1):
# die B2-Abweichung aus ABWEICHUNG_ERKLAERT ist erklaert, dieselbe Folge mit einer zusaetzlichen
# Vertauschung der letzten beiden Texte ist eine andere Abweichung und nicht erklaert.
fuell = [{"teil": 1, "titel": f"Weingruß F{i}", "anmerkung": "", "klammer": False} for i in range(14)]
nach = ["Weingruß Allerliebster Trunck", "Weinsegen Allerliebster Trost", "Biergruß Liebes Pir",
        "Biersegen Liebe Gerstenprü"]
h_b2 = fuell + [{"teil": 1, "titel": t, "anmerkung": "", "klammer": False} for t in nach]
u_b2 = [h["titel"] for h in fuell] + ["Weinsegen Allerliebster Trost"] + nach
ab_b2 = bh.abgleich("B2", h_b2, u_b2, None)
pruefe("Schluessel: B2-Abweichungen sind erklaert (Positivkontrolle)",
       len(ab_b2) == 2 and all(bh.schluessel("B2", x) in conv.bc.ABWEICHUNG_ERKLAERT for x in ab_b2),
       str([bh.schluessel("B2", x) for x in ab_b2]))
ab_b2_x = bh.abgleich("B2", h_b2, u_b2[:-2] + u_b2[-2:][::-1], None)
pruefe("Schluessel: zusaetzliche Vertauschung ist nicht erklaert",
       [x["art"] for x in ab_b2_x] == ["nur_bisher", "reihenfolge"]
       and bh.schluessel("B2", ab_b2_x[1]) not in conv.bc.ABWEICHUNG_ERKLAERT, str(ab_b2_x))
ab_zwei = bh.abgleich("B2", h_b2, u_b2 + ["Weinsegen Allerliebster Trost"], None)
pruefe("Schluessel: zweiter Fehlansatz (Anzahl) ist nicht erklaert",
       any(x["art"] == "nur_bisher" and x["bisher"] == "2x"
           and bh.schluessel("B2", x) not in conv.bc.ABWEICHUNG_ERKLAERT for x in ab_zwei), str(ab_zwei))
# d6: ein Klammertext der Hauptseite als eigener Abschnitt ist eine Abweichung und seit der
# Einarbeitung (bre_common.EINGEARBEITET) nicht mehr erklaert; die Fixture haelt nur die drei
# eingearbeiteten Klammertexte, die echte Hauptseite fuehrt fuer d6 sechs in Klammern
h_d6 = [{"teil": 1, "titel": "Weingruß Edels Getranck", "anmerkung": "", "klammer": False}] + [
    {"teil": 1, "titel": t, "anmerkung": "", "klammer": True}
    for t in ("Weingruß Allerliebster Trunck", "Weinsegen Allerliebster Trost", "Weinsegen Ein Kron")]
u_d6 = ["Weingruß Edels Getranck", "Weingruß Allerliebster Trunck", "Weinsegen Allerliebster Trost",
        "Weinsegen Ein Kron"]
ab_d6 = bh.abgleich("d6", h_d6, u_d6, None)
pruefe("Schluessel: Klammertext als eigener Abschnitt ist nicht erklaert (seit der Einarbeitung)",
       len(ab_d6) == 3 and not any(bh.schluessel("d6", x) in conv.bc.ABWEICHUNG_ERKLAERT for x in ab_d6),
       str([bh.schluessel("d6", x) for x in ab_d6]))
pruefe("EINGEARBEITET: die drei Texte von d6, gegen die Klammertexte der Fixture",
       {bh.norm_titel(t) for t in conv.bc.EINGEARBEITET["d6"]} == {h["titel"] for h in h_d6 if h["klammer"]}
       and bh.eingearbeitet_in("d6", "Weingruß Allerliebster Trunck (Hans Rosenplüt)")
       == "Weinsegen Edles Abkülen" and bh.eingearbeitet_in("d6", "Weingruß Edels Getranck") is None
       and bh.eingearbeitet_in("B", "Weinsegen Ein Kron") is None)
# nur_hauptseite traegt die Anzahl der fehlenden Vorkommen
h_zwei = [{"teil": 1, "titel": "Weingruß X", "anmerkung": "", "klammer": False}] * 2
pruefe("Schluessel: nur_hauptseite traegt die Anzahl",
       bh.abgleich("B", h_zwei, [], None)[0]["hauptseite"].startswith("2x, ")
       and bh.abgleich("B", h_zwei[:1], [], None)[0]["hauptseite"].startswith("1x, "))
MATRIX = HAUPT + """
{|
|-
|style="x"|
|style="x"|B
|-
|style="white-space: pre; vertical-align:top;"|[[Weingruß Edels Getranck]]
||1
|}
"""
try:
    bh.parse_matrix(MATRIX)
    pruefe("Uebersicht: Spaltenkoepfe muessen die Zeugenliste sein", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("Uebersicht: Spaltenkoepfe muessen die Zeugenliste sein", True)


def matrix_mit_koepfen(mit_link):
    """Uebersichtstabelle mit allen 21 Spaltenkoepfen, als Text oder (ab Revision 31248) als Link."""
    def sup(s):  # "B1" -> "B<sup>1</sup>", "d4" -> "d<sup>4</sup>", "B" bleibt
        return s[0] + "<sup>" + s[1:] + "</sup>" if len(s) == 2 and s[1].isdigit() else s
    koepfe = [f'|style="border-width: 1px 1px 5px 1px"|'
              + (f"[[Weingrüße {conv.bc.ZEUGEN[s][0]}|{sup(s)}]]" if mit_link else sup(s))
              for s in conv.bc.ZEUGEN]
    zeile = '|style="white-space: pre;"|[[Weingruß Edels Getranck]]\n||1' + "\n||" * (len(koepfe) - 1)
    return HAUPT + "\n{|\n|-\n|style=\"x\"|\n" + "\n".join(koepfe) + "\n|-\n" + zeile + "\n|}\n"


for mit_link in (False, True):
    try:
        m_koepfe = bh.parse_matrix(matrix_mit_koepfen(mit_link))
        pruefe(f"Uebersicht: Spaltenkoepfe {'als Link' if mit_link else 'als Text'} werden gelesen",
               list(m_koepfe) == ["Weingruß Edels Getranck"] and m_koepfe["Weingruß Edels Getranck"]
               == {"B": "1"}, str(m_koepfe))
    except conv.bc.HarterFehler as e:
        pruefe(f"Uebersicht: Spaltenkoepfe {'als Link' if mit_link else 'als Text'} werden gelesen",
               False, str(e)[:200])
m_echt = bh.parse_matrix(conv.bc.lade_seite(conv.bc.HAUPT_TITEL)["inhalt"])
pruefe("Uebersicht: die gepinnte Hauptseite (Revision 31248) laesst sich lesen, d4 fuehrt Edels vor Leibsalb",
       m_echt["Weingruß Edels Getranck"]["d4"] == "2" and m_echt["Weinsegen Edle Leibsalb"]["d4"] == "3",
       str(len(m_echt)))
pruefe("Uebersicht: Zellen", bh.matrix_folge(
    {"Weingruß A": {"W1": "A2<br />B4"}, "Weingruß B": {"W1": "(3)"}, "Weingruß C": {"W1": "B1*"}}, "W1")
       == [{"titel": "Weingruß B", "teil": "1", "anmerkung": "(3)", "klammer": True},
           {"titel": "Weingruß A", "teil": "A", "anmerkung": "A2", "klammer": False},
           {"titel": "Weingruß C", "teil": "B", "anmerkung": "B1*", "klammer": False},
           {"titel": "Weingruß A", "teil": "B", "anmerkung": "B4", "klammer": False}])

# Faltung nur im Vergleich: ů in der Transkription, u+U+0366 im ersten Vers; Ausgabe unveraendert
rows_f = [dict(ROWS[0], erster_vers="Gruͦß dich got"), ROWS[1]]
s_f = SEITE.replace("Gr</span>üß dich got", "Gr</span>ůß dich got")
_, _, tei_f, _, falt = baue(s_f, rows_f, "B")
pruefe("Faltung angewandt und gemeldet", len(falt) == 1 and "B Zeile" in falt[0] and "ů~uͦ" in falt[0], str(falt))
pruefe("Faltung nicht in der Ausgabe", "ů" in conv.etree.tostring(tei_f, encoding="unicode")
       and "uͦ" not in conv.etree.tostring(tei_f, encoding="unicode"))
try:
    baue(SEITE, [dict(ROWS[0], erster_vers="Gruͦß dich got"), ROWS[1]], "B")
    pruefe("ohne Treffer keine Faltung", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("ohne Treffer keine Faltung", True)

# A1: Zeilennummern 1-basiert gegen die Quelle (Fixture: "Grüß dich got" steht in Zeile 8)
zeilen_fix = SEITE.split("\n")
gruess = [it for it in items if it["kind"] == "verse" and it["raw"].endswith("üß dich got")]
pruefe("Quellzeilennummer 1-basiert", len(gruess) == 1 and gruess[0]["lines"][0] == 8
       and "üß dich got" in zeilen_fix[7], str([g["lines"] for g in gruess]))
try:
    baue(s_titel, ROWS, "B")
    pruefe("Zeilennummer in der Meldung", False, "kein Fehler")
except conv.bc.HarterFehler as e:
    pruefe("Zeilennummer in der Meldung", "Zeilen [7]" in str(e) and zeilen_fix[6].startswith("<span"), str(e)[:120])

# A2: fetter/roter Vorspann ohne Tabelleneintrag = harter Fehler (nicht <head> des ersten Textes)
for formatiert in ("'''Fetter Titel'''", '<span style="color:#FF0000">Roter Titel</span>'):
    s_fett = SEITE.replace("[188r]<br />\n", f"[188r]<br />\n{formatiert}<br />\n", 1).replace(
        '<span style="color:#FF0000">Der Segen</span><br />\n', "", 1)
    try:
        baue(s_fett, ROWS, "B")
        pruefe(f"Vorspann ohne Tabelle: {formatiert[:12]}", False, "kein Fehler")
    except conv.bc.HarterFehler as e:
        pruefe(f"Vorspann ohne Tabelle: {formatiert[:12]}", "Vorspann weicht" in str(e))

# B3b: Teil-Marker -> umschliessendes <div n="B"> ohne type, Abschnitt darin
s_teil = SEITE.replace('<span style="color:#FF0000">N</span>u grüß dich zwei',
                       '=== Teil B ===\n<span style="color:#FF0000">N</span>u grüß dich zwei')
_, _, tei_t, _, _ = baue(s_teil, ROWS, "B")
teil = tei_t.xpath("//t:body/t:div/t:div[@n='B']", namespaces=ns)
pruefe("Teil-Marker als div/@n", len(teil) == 1 and teil[0].get("type") is None
       and len(teil[0].xpath("t:div[@type='section']", namespaces=ns)) == 1
       and len(tei_t.xpath("//t:body/t:div/t:div[@type='section']", namespaces=ns)) == 1)

# Klammern ohne Buchstaben: (?) -> note nach dem Token, (...) -> gap zwischen den <w>, sonst Fehler
s_k = SEITE.replace("Mit her(r) v(er)stoppffen", "Mit her(?) st(...) v(er)stoppffen")
_, _, tei_k, _, _ = baue(s_k, ROWS, "B")
her = [e for e in tei_k.xpath("//t:w", namespaces=ns) if e.xpath("string(.)") == "her"]
pruefe("(?) als note nach dem Token", len(her) == 1 and her[0].getnext().tag == conv.q("note")
       and her[0].getnext().text == "Lesung unsicher" and her[0].getnext().get("type") == "transcription")
gap = tei_k.xpath("//t:gap", namespaces=ns)
st = [e for e in tei_k.xpath("//t:w", namespaces=ns) if e.xpath("string(.)") == "st"]
pruefe("(...) als gap zwischen den w", len(gap) == 1 and gap[0].get("reason") == "illegible"
       and gap[0].getparent().tag == conv.q("l") and st and st[0].getnext() is gap[0])
try:
    conv.lexe("a (12) b", [], "test")
    pruefe("Klammer ohne Buchstaben = Fehler", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("Klammer ohne Buchstaben = Fehler", True)

# Kopfregel zwischen Texten: ganz rote oder ganz fette Zeile vor Text B wird dessen <head>,
# auch ohne Eintrag in der Spalte ueberschrift (Text B hat dort keinen). Heute entscheidet die
# Regel keinen Kopf im Bestand; sie greift erst bei einer Rubrik, die die Synopse nicht fuehrt.
for formatiert in ('<span style="color:#FF0000">Wein segen</span>', "'''Wein segen'''"):
    s_kopf = SEITE.replace('<span style="color:#FF0000">N</span>u grüß dich zwei',
                           f'{formatiert}<br />\n<span style="color:#FF0000">N</span>u grüß dich zwei')
    _, texte_k, tei_kopf, info_k, _ = baue(s_kopf, ROWS, "B")
    kopf_b = tei_kopf.xpath("//t:div[@n='2']/t:head", namespaces=ns)
    pruefe(f"Kopfregel: {formatiert[:12]} wird head von Text B",
           len(texte_k[1]["heads"]) == 1 and len(kopf_b) == 1
           and kopf_b[0].xpath("string(.)") == "Weinsegen"
           and len(tei_kopf.xpath("//t:div[@n='1']/t:l", namespaces=ns)) == 4
           and len(tei_kopf.xpath("//t:l", namespaces=ns)) + len(tei_kopf.xpath("//t:head", namespaces=ns))
           + info_k["fortsetzungen"] == info_k["stuecke"],
           conv.etree.tostring(tei_kopf.xpath("//t:div[@n='2']", namespaces=ns)[0]).decode()[:200])
# Gegenprobe: nur teilweise rote Zeile (Lombarde) vor Text B bleibt Vers von Text A
s_teilrot = SEITE.replace('<span style="color:#FF0000">N</span>u grüß dich zwei',
                          '<span style="color:#FF0000">W</span>ein segen<br />\n'
                          '<span style="color:#FF0000">N</span>u grüß dich zwei')
_, texte_tr, tei_tr, _, _ = baue(s_teilrot, ROWS, "B")
pruefe("Kopfregel: Lombarde allein macht keinen head",
       not texte_tr[1]["heads"] and not tei_tr.xpath("//t:div[@n='2']/t:head", namespaces=ns)
       and len(tei_tr.xpath("//t:div[@n='1']/t:l", namespaces=ns)) == 5)

# Epoche: Teil B von D (17. Jh.) entfaellt in der Ausgabe, Segmentierung sieht den ganzen Zeugen
s_ab = SEITE.replace("[188r]<br />\n", "===A:===\n[188r]<br />\n", 1).replace(
    '<span style="color:#FF0000">N</span>u grüß dich zwei',
    '===B:===\n<span style="color:#FF0000">N</span>u grüß dich zwei')


def baue_mit_ausschluss(seite, sigle):
    signatur, its, noten, inf = conv.lies_transkription(seite)
    lx = {i: conv.lexe(it["raw"], noten, "t") for i, it in enumerate(its) if it["kind"] == "verse"}
    tx, _, vs = conv.segmentiere(its, lx, ROWS, sigle)
    its, tx, raus, grund = conv.schneide_teil_ab(sigle, its, tx, inf)
    st = {"w": 0, "l": 0, "head": 0, "pb": 0, "pb_im_wort": 0, "note": 0,
          "el": collections.Counter(), "span_dupliziert": collections.Counter()}
    t, _, _ = conv.baue_tei("BRE_TEST", signatur, SEITE_META, its, lx, tx, st, vs, "2026-01-01", grund)
    return t, tx, raus, inf


tei_d, tx_d, raus_d, inf_d = baue_mit_ausschluss(s_ab, "D")
pruefe("Ausschluss D Teil B: ein Text bleibt, einer entfaellt",
       len(tx_d) == 1 and len(raus_d) == 1 and raus_d[0]["row"]["text_titel"] == "B"
       and len(tei_d.xpath("//t:div[@type='section']", namespaces=ns)) == 1
       and not tei_d.xpath("//t:div[@n='B']", namespaces=ns)
       and "zweite" not in conv.etree.tostring(tei_d, encoding="unicode"))
pruefe("Ausschluss D Teil B: Zeilenbilanz geht auf",
       len(tei_d.xpath("//t:l", namespaces=ns)) + len(tei_d.xpath("//t:head", namespaces=ns))
       + inf_d["fortsetzungen"] == inf_d["stuecke"], str(inf_d))
pruefe("Ausschluss D Teil B: Grund im Header und als Kommentar",
       "17. Jahrhundert" in "".join(tei_d.xpath("//t:note[@type='fidelity']/text()", namespaces=ns))
       and any("17. Jahrhundert" in c.text for c in tei_d.xpath("//t:body//comment()", namespaces=ns)))
tei_b, tx_b, raus_b, _ = baue_mit_ausschluss(s_ab, "B")
pruefe("Ausschluss nur fuer D: B behaelt beide Teile", len(raus_b) == 0 and len(tx_b) == 2
       and len(tei_b.xpath("//t:div[@n='B']", namespaces=ns)) == 1)
try:
    baue_mit_ausschluss(SEITE, "D")
    pruefe("Ausschluss ohne Teil-Marker = Fehler", False, "kein Fehler")
except conv.bc.HarterFehler:
    pruefe("Ausschluss ohne Teil-Marker = Fehler", True)
# Satzzeichen (#66): eigenes <pc join="left">, Apostroph und Bindestrich bleiben im Wort
s_pc = SEITE.replace("Mit her(r) v(er)stoppffen", "Mit her(r), mach’ wagen-schmir. Der.X.")
_, _, tei_pc, info_pc, _ = baue(s_pc, ROWS, "B")
pcs = tei_pc.xpath("//t:pc", namespaces=ns)
woerter_pc = [e.xpath("string(.)") for e in tei_pc.xpath("//t:w", namespaces=ns)]
pruefe("Satzzeichen als pc", [p.text for p in pcs] == [",", ".", ".", "."]
       and all(p.get("join") == "left" for p in pcs)
       and "mach’" in woerter_pc and "wagen-schmir" in woerter_pc and "X" in woerter_pc
       and not any(c in w for w in woerter_pc for c in ",.;:!?"), str(woerter_pc))
pruefe("Satzzeichen: Zeilenbilanz", len(tei_pc.xpath("//t:l", namespaces=ns))
       + len(tei_pc.xpath("//t:head", namespaces=ns)) + info_pc["fortsetzungen"] == info_pc["stuecke"])
pruefe("keine offene Segmentierung mehr (Silvan 2026-11-26)", conv.bc.SEGMENTIERUNG_OFFEN == {})

# Normdaten im Header (23-normdaten.py, #147): Autorschaft aus den Texten der TEI-Datei, Header idempotent
spec_n = importlib.util.spec_from_file_location("norm", HIER / "23-normdaten.py")
norm = importlib.util.module_from_spec(spec_n)
spec_n.loader.exec_module(norm)
PERS, GEN = norm.lade_normdaten()
ROS = "Hans Rosenplüt"


def zeile(titel, ed, blatt="1r"):
    return {"text_titel": titel, "editionssigle": ed, "signatur_label": "Sig", "blatt": blatt}


NROWS = [zeile(f"Weingruß Eins ({ROS})", "B"), zeile(f"Weinsegen Zwei ({ROS})", "B", "2r"),
         zeile("Vorspruch Weingruß", "B", "3r"), zeile(f"Weinsegen Allerliebster Trost ({ROS})", "B", "4r"),
         zeile("Weingruß Drei", "N2", "6r")]


def mini(*kommentare, abschnitte=None, extra=None):
    """TEI mit Body, je Kommentar ein Text-Kommentar samt <div type="section">.
    extra: ein weiterer Kommentar ohne Abschnitt (keiner der Text-Kommentare)."""
    n = len(kommentare) if abschnitte is None else abschnitte
    cs = "".join(f"<!-- Text {i}: {k} -->" for i, k in enumerate(kommentare, 1))
    cs += f"<!-- {extra} -->" if extra else ""
    ds = "".join(f'<div type="section" n="{i}"/>' for i in range(1, n + 1))
    return conv.etree.fromstring(f'<TEI xmlns="{conv.TEI_NS}"><text><body><div>{cs}{ds}</div></body></text></TEI>')


def autoren(ed, *kommentare, rows=NROWS, **kw):
    return norm.autoren_des_zeugen(ed, mini(*kommentare, **kw), rows, PERS)


def wirft(f):
    try:
        f()
    except conv.bc.HarterFehler:
        return True
    return False


A1, A2 = f"Weingruß Eins ({ROS}) (Sig, 1r)", f"Weinsegen Zwei ({ROS}) (Sig, 2r)"
V1 = "Vorspruch Weingruß (Sig, 3r)"
pids, n_r, n, _ = autoren("B", A1, A2)
pruefe("Normdaten: Zeuge nur mit Rosenplüt-Texten bekommt nur person_907",
       pids == ["person_907"] and (n_r, n) == (2, 2), str((pids, n_r, n)))
pids, n_r, n, _ = autoren("B", V1)
pruefe("Normdaten: Zeuge ohne Rosenplüt-Text ist anonym", pids == ["person_anonym"] and (n_r, n) == (0, 1))
pids, n_r, n, _ = autoren("B", V1, A1)
pruefe("Normdaten: gemischter Zeuge trägt beide, Rosenplüt zuerst",
       pids == ["person_907", "person_anonym"] and (n_r, n) == (1, 2), str((pids, n_r, n)))
pids, n_r, n, _ = autoren("R", "Weinsegen Allerliebster Trost (Fragment)")
pruefe("Normdaten: Fragment erbt vom Werk, das es benennt", pids == ["person_907"] and (n_r, n) == (1, 1),
       str((pids, n_r, n)))
pids, n_r, n, _ = autoren("N2", "Vorspann (text_ohne_einzelseite)", "Weingruß Drei (Sig, 6r)")
pruefe("Normdaten: Vorspann ohne Werk ist anonym", pids == ["person_anonym"] and (n_r, n) == (0, 2),
       str((pids, n_r, n)))
pruefe("Normdaten: Text ohne Zeile in der Segmentierung ist ein harter Fehler",
       wirft(lambda: autoren("B", A1, "Weingruß Unbekannt (Sig, 9r)")))
pruefe("Normdaten: anderer Autorzusatz ist ein harter Fehler",
       wirft(lambda: autoren("B", "Weingruß Falsch (Hans Sachs) (Sig, 5r)",
                             rows=NROWS + [zeile("Weingruß Falsch (Hans Sachs)", "B", "5r")])))
pruefe("Normdaten: Fragment mit fremdem Werk ist ein harter Fehler",
       wirft(lambda: autoren("R", "Weingruß Eins (Fragment)")))
pruefe("Normdaten: unbekannter Kommentar im Body ist ein harter Fehler",
       wirft(lambda: autoren("B", A1, A2, extra="Irgendwas")))
pruefe("Normdaten: Kommentare und Abschnitte müssen übereinstimmen",
       wirft(lambda: autoren("B", A1, A2, abschnitte=3)))

# Werktitel: Kurzform der Aufbewahrung bei Handschriften, "Druck" bei Drucken
ZT = {"mhdbdb_sigle": "BRE_X", "typ": "Handschrift", "signatur": "Cgm 713",
      "aufbewahrung": "München, Bayerische Staatsbibliothek"}
pruefe("Normdaten: Werktitel einer Handschrift mit Kurzform",
       norm.werktitel_von(ZT) == "Weingrüße (München, BSB, Cgm 713)", norm.werktitel_von(ZT))
pruefe("Normdaten: Werktitel eines Drucks ohne Aufbewahrung",
       norm.werktitel_von({**ZT, "typ": "Druck", "signatur": "VD16 R 439"}) == "Weingrüße (Druck, VD16 R 439)")
pruefe("Normdaten: Handschrift mit unbekannter Aufbewahrung ist ein harter Fehler",
       wirft(lambda: norm.werktitel_von({**ZT, "aufbewahrung": "Irgendwo, Bibliothek"})))
pruefe("Normdaten: unbekannter Typ ist ein harter Fehler",
       wirft(lambda: norm.werktitel_von({**ZT, "typ": "Rolle"})))

# Header: setzen und ein zweites Mal setzen
_, _, tei_n, _, _ = baue(SEITE, ROWS, "B")
WT = "Weingrüße (Test, Cgm 713)"
vorher = conv.etree.tostring(tei_n)
g1 = norm.setze_header(tei_n, "BRE_TEST", WT, ["person_907", "person_anonym"], PERS, GEN, "2026-11-25")
nach1 = conv.etree.tostring(tei_n)
try:
    g2 = norm.setze_header(tei_n, "BRE_TEST", WT, ["person_907", "person_anonym"], PERS, GEN, "2026-12-31")
except conv.bc.HarterFehler as e:
    g2 = f"Fehler: {e}"
xn = lambda p: tei_n.xpath(p, namespaces=ns)  # noqa: E731
pruefe("Normdaten: Header setzt alle sieben Felder", len(g1) == 7, str(g1))
pruefe("Normdaten: Header idempotent, zweiter Lauf ändert kein Byte",
       g2 == [] and conv.etree.tostring(tei_n) == nach1 and nach1 != vorher, str(g2))
pruefe("Normdaten: msName behält seinen Wert, nur der title bekommt den Werktitel",
       xn("//t:msName/text()") == ["Test, Cgm 713, 188r-188v"] and xn("//t:titleStmt/t:title/text()") == [WT])
pruefe("Normdaten: msIdentifier und digitalIntermediary",
       xn("//t:msIdentifier/@corresp") == ["works.xml#work_BRE_TEST"]
       and xn("//t:bibl[@type='digitalIntermediary']/@corresp") == ["#BRE_TEST_BRE_TEST"])
pruefe("Normdaten: Gattung mit Glossen aus genres.xml",
       xn("//t:taxonomy[@xml:id='genres']/t:category/@xml:id") == ["genre_315cf46f"]
       and xn("//t:taxonomy/t:category/@corresp") == ["genres.xml#genre_315cf46f"]
       and xn("//t:taxonomy/t:category/t:gloss/text()") == ["Weingruß", "Wine Greeting"])
pruefe("Normdaten: Autoren in titleStmt und particDesc",
       xn("//t:titleStmt/t:author/@ref") == ["#person_907", "#person_anonym"]
       and xn("//t:particDesc//t:person/@xml:id") == ["person_907", "person_anonym"]
       and xn("//t:person[@xml:id='person_907']/t:idno/@type") == ["GND", "wikidata"])
pruefe("Normdaten: eine Änderungszeile, Sprachstufe unberührt",
       len([c for c in xn("//t:revisionDesc/t:change/text()") if c.startswith(norm.MARKE)]) == 1
       and xn("//t:revisionDesc/t:change[last()]/@when") == ["2026-11-25"]
       and xn("//t:language/@ident") == ["TBD"])
_, _, tei_r, _, _ = baue(SEITE, ROWS, "B")
norm.setze_header(tei_r, "BRE_TEST", WT, ["person_907"], PERS, GEN, "2026-11-25")
pruefe("Normdaten: Zeuge nur mit Rosenplüt hat im particDesc kein person_anonym",
       tei_r.xpath("//t:particDesc//t:person/@xml:id", namespaces=ns) == ["person_907"]
       and tei_r.xpath("//t:titleStmt/t:author/@ref", namespaces=ns) == ["#person_907"])
_, _, tei_f, _, _ = baue(SEITE, ROWS, "B")
tei_f.xpath("//t:msIdentifier", namespaces=ns)[0].set("corresp", "works.xml#work_ANDERS")
pruefe("Normdaten: unerwarteter Zustand im Header ist ein harter Fehler",
       wirft(lambda: norm.setze_header(tei_f, "BRE_TEST", WT, ["person_907"], PERS, GEN, "2026-11-25")))

# Sperre gegen das Ueberschreiben (Entscheidung 25.11.2026): 02 ersetzt eine vorhandene Zieldatei nur
# mit --ueberschreiben. Arbeitet am echten Wiki-Cache (temp/bre-wiki), schreibt aber nur in einen
# temporaeren Ausgabeordner, nie nach ingest/bre/.
import contextlib  # noqa: E402
import io  # noqa: E402
import tempfile  # noqa: E402

SPERRE_DATUM = "2026-11-25"
ZIEL_B = conv.bc.ZEUGEN["B"][1] + ".tei.xml"
ALT = b"<alt>Annotation</alt>"


def sperre_lauf(vorhanden, **kw):
    """konvertiere('B', ...) in einem frischen Ausgabeordner. Gibt (Ergebnis, Inhalt der Zieldatei)."""
    with tempfile.TemporaryDirectory() as td:
        aus = Path(td)
        if vorhanden:
            (aus / ZIEL_B).write_bytes(ALT)
        kw.setdefault("trocken", False)
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                conv.konvertiere("B", ausgabe_dir=aus, datum=SPERRE_DATUM, **kw)
            erg = "geschrieben"
        except conv.bc.HarterFehler as e:
            erg = f"fehler: {e}"
        ziel = aus / ZIEL_B
        # der Restore-Hinweis muss den vollen Pfad tragen, sonst trifft git restore nur aus ingest/bre
        if erg.startswith("fehler:") and f'git restore "{ziel}"' not in erg:
            erg = "fehler ohne vollen Pfad im Restore-Hinweis: " + erg
        return erg, (ziel.read_bytes() if ziel.exists() else None)


erg, inhalt = sperre_lauf(True)
pruefe("Sperre: Ziel existiert ohne Flag = harter Fehler, Datei unberuehrt",
       erg.startswith("fehler:") and "--ueberschreiben" in erg and "Phasen 1 bis 3" in erg
       and "Normdaten" in erg and inhalt == ALT, erg[:80])
erg, inhalt = sperre_lauf(True, ueberschreiben=True)
pruefe("Sperre: Ziel existiert, mit Flag wird geschrieben",
       erg == "geschrieben" and inhalt is not None and inhalt != ALT and b"<TEI" in inhalt, erg[:80])
erg, inhalt = sperre_lauf(False)
pruefe("Sperre: Ziel neu wird ohne Flag geschrieben",
       erg == "geschrieben" and inhalt is not None and b"<TEI" in inhalt, erg[:80])
erg, inhalt = sperre_lauf(True, trocken=True)
pruefe("Sperre: --trocken schreibt nie, auch nicht mit vorhandenem Ziel",
       erg == "geschrieben" and inhalt == ALT, erg[:80])
erg, inhalt = sperre_lauf(False, trocken=True)
pruefe("Sperre: --trocken legt keine Datei an", erg == "geschrieben" and inhalt is None, erg[:80])

# "alle": ist irgendein Ziel gesperrt, bricht main ab, bevor das erste geschrieben wird
def alle_lauf(offen):
    """02 --zeuge alle mit einem vorhandenen Ziel (W) und bre_common.SEGMENTIERUNG_OFFEN = offen.
    -> (Rueckgabe, Dateien im Ausgabeordner, Inhalt von W, Fehlermeldung)"""
    offen_alt = dict(conv.bc.SEGMENTIERUNG_OFFEN)
    conv.bc.SEGMENTIERUNG_OFFEN.clear()
    conv.bc.SEGMENTIERUNG_OFFEN.update(offen)
    argv_alt = sys.argv
    try:
        with tempfile.TemporaryDirectory() as td:
            aus = Path(td)
            vorhanden = conv.bc.ZEUGEN["W"][1] + ".tei.xml"
            (aus / vorhanden).write_bytes(ALT)
            sys.argv = ["02", "--zeuge", "alle", "--ausgabe-dir", str(aus), "--datum", SPERRE_DATUM]
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as se:
                rc = conv.main()
            return (rc, sorted(p.name for p in aus.iterdir()), (aus / vorhanden).read_bytes(),
                    se.getvalue(), vorhanden)
    finally:
        sys.argv = argv_alt
        conv.bc.SEGMENTIERUNG_OFFEN.clear()
        conv.bc.SEGMENTIERUNG_OFFEN.update(offen_alt)


rc_alle, dateien, inhalt_w, meldung, vorhanden = alle_lauf({})
pruefe("Sperre: alle bricht vor dem ersten Schreiben ab",
       rc_alle == 1 and dateien == [vorhanden] and inhalt_w == ALT, f"rc={rc_alle} {dateien}")
pruefe("Sperre: Nenner zaehlt alle 21 Ziele, wenn keine Segmentierung offen ist",
       "1 von 21 geprueften Zielen existieren schon (W)" in meldung
       and "Segmentierung offen" not in meldung, meldung[-300:])
# Offene Zeugen (Mechanismus fuer kuenftige Faelle): zaehlen nicht im Nenner, eigene Zeile
rc_offen, dateien, inhalt_w, meldung, vorhanden = alle_lauf(
    {"B2": "Probe", "d4": "Probe", "d6": "Probe"})
pruefe("Sperre: Nenner zaehlt nur gepruefte Ziele, offene Zeugen eigene Zeile",
       rc_offen == 1 and dateien == [vorhanden] and inhalt_w == ALT
       and "1 von 18 geprueften Zielen existieren schon (W)" in meldung
       and "nicht geprueft, Segmentierung offen: B2, d4, d6" in meldung, meldung[-300:])

# B2, d4, d6 nach Silvans Antwort (2026-11-26, #147): arbeitet am echten Wiki-Cache, schreibt nur in
# einen temporaeren Ordner.
def zeuge_baum(sigle):
    """-> (Baum, Konsolenausgabe) von konvertiere(sigle) in einem frischen Ausgabeordner."""
    with tempfile.TemporaryDirectory() as td:
        ausgabe = io.StringIO()
        with contextlib.redirect_stdout(ausgabe):
            conv.konvertiere(sigle, trocken=False, ausgabe_dir=Path(td), datum=SPERRE_DATUM)
        return conv.etree.parse(str(Path(td) / (conv.bc.ZEUGEN[sigle][1] + ".tei.xml"))), ausgabe.getvalue()


def sektionen(baum):
    return baum.xpath("//t:div[@type='section']", namespaces=ns)


baum_d6, aus_d6 = zeuge_baum("d6")
noten_d6 = baum_d6.xpath("//t:note[@type='editorial' and starts-with(., 'Ab hier ist')]", namespaces=ns)
eltern_d6 = {id(n.getparent()) for n in noten_d6}
abk = noten_d6[0].getparent() if noten_d6 else None
pruefe("d6: drei Texte eingearbeitet, neun eigene Abschnitte, keine Abweichung zur Hauptseite",
       len(sektionen(baum_d6)) == 9 and len(noten_d6) == 3 and len(eltern_d6) == 1
       and "keine Abweichung" in aus_d6 and "3 eingearbeitet" in aus_d6, aus_d6[:400])
pruefe("d6: die Notizen nennen den eingearbeiteten Text und den Zieltext",
       [n.text.split(" in den ")[0] for n in noten_d6]
       == ["Ab hier ist Weingruß Allerliebster Trunck", "Ab hier ist Weinsegen Allerliebster Trost",
           "Ab hier ist Weinsegen Ein Kron"]
       and all("Weinsegen Edles Abkülen eingearbeitet" in n.text for n in noten_d6))
zaehl_d6 = abk.xpath("t:l/@n", namespaces=ns) if abk is not None else []
pruefe("d6: <l>/@n laeuft im Zieltext ueber die eingearbeiteten Passagen weiter, ohne Wiederholung",
       zaehl_d6 == [str(i) for i in range(1, len(zaehl_d6) + 1)] and len(zaehl_d6) > 40, str(zaehl_d6[:6]))
schluss_d6 = baum_d6.xpath("//t:note[@type='editorial' and starts-with(., 'Hier enden')]", namespaces=ns)
folgende = schluss_d6[0].xpath("following-sibling::t:l[1]//t:w/text()", namespaces=ns) if schluss_d6 else []
pruefe("d6: eine Notiz grenzt ENDE und den Schlussreim von den eingearbeiteten Passagen ab",
       len(schluss_d6) == 1 and schluss_d6[0].getparent() is abk and folgende == ["ENDE"]
       and len(schluss_d6[0].xpath("following-sibling::t:l", namespaces=ns)) == 5
       and len(schluss_d6[0].xpath("preceding-sibling::t:note[starts-with(., 'Ab hier ist')]",
                                   namespaces=ns)) == 3, str(folgende))
baum_b2, aus_b2 = zeuge_baum("B2")
ansaetze = baum_b2.xpath("//t:note[@type='editorial' and starts-with(., 'Abgebrochener Ansatz')]",
                         namespaces=ns)
pruefe("B2: der Fehlansatz ist ein eigener Abschnitt mit Notiz, 19 Abschnitte, nur dieser trägt sie",
       len(sektionen(baum_b2)) == 19 and len(ansaetze) == 1
       and ansaetze[0].getparent().get("n") == "15" and "falscher Eintrag" in ansaetze[0].text
       and "Weinsegen Allerliebster Trost" in ansaetze[0].text, aus_b2[:300])
baum_d4, aus_d4 = zeuge_baum("d4")
pruefe("d4: Edels Getranck vor Edle Leibsalb, keine Abweichung zur Hauptseite (rev 31248)",
       len(sektionen(baum_d4)) == 4 and "keine Abweichung" in aus_d4 and "rev 31248" in aus_d4
       and aus_d4.index("Weingruß Edels Getranck") < aus_d4.index("Weinsegen Edle Leibsalb"), aus_d4[:300])


def eingearbeitet_fehler(sigle, belegung):
    """konvertiere(sigle, trocken) mit bre_common.EINGEARBEITET = belegung -> Fehlermeldung oder None."""
    alt = conv.bc.EINGEARBEITET
    conv.bc.EINGEARBEITET = belegung
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            conv.konvertiere(sigle, trocken=True, ausgabe_dir=Path(tempfile.gettempdir()), datum=SPERRE_DATUM)
        return None
    except conv.bc.HarterFehler as e:
        return str(e)
    finally:
        conv.bc.EINGEARBEITET = alt


f_vorher = eingearbeitet_fehler("d6", {"d6": {"Weinsegen Ein Kron": "Weingruß Lieber Wein"}})
pruefe("Eingearbeitet: Zieltext muss der vorangehende eigene Text sein",
       f_vorher is not None and "soll in" in f_vorher and "eingearbeitet" in f_vorher, str(f_vorher))
f_fremd = eingearbeitet_fehler("d6", {"d6": {"Weinsegen Gibt Es Nicht": "Weinsegen Edles Abkülen"}})
pruefe("Eingearbeitet: ein Text, den es in der Segmentierung nicht gibt, ist ein harter Fehler",
       f_fremd is not None and "Segmentierung nicht gibt" in f_fremd, str(f_fremd))

schluss_alt = conv.bc.SCHLUSS
conv.bc.SCHLUSS = {"BRE_D6": ("DIESE ZEILE GIBT ES NICHT", "x")}
try:
    with contextlib.redirect_stdout(io.StringIO()):
        conv.konvertiere("d6", trocken=True, ausgabe_dir=Path(tempfile.gettempdir()), datum=SPERRE_DATUM)
    f_schluss = None
except conv.bc.HarterFehler as e:
    f_schluss = str(e)
finally:
    conv.bc.SCHLUSS = schluss_alt
pruefe("Schluss: eine Schlusszeile, die es nicht gibt, ist ein harter Fehler",
       f_schluss is not None and "SCHLUSS" in f_schluss, str(f_schluss))

# Druckfahnen (Kickoff #147): kein Wortlaut aus Text, Uebersetzung oder Kommentar der Druckfassung
# im Repo. Quelle ist der Text der Hirzel-Druckfahnen (PDF, per pdftotext auf stdout gelesen, nie
# als Datei abgelegt; Silbentrennung am Zeilenende zusammengezogen) und, weil der Kickoff sie zum
# selben Material zaehlt, Silvans Word-Steckbriefe von 2022 (sources/weingruesse/docling/*.md).
# Gesucht wird jede Folge von DRUCK_N Woertern daraus, die nicht auch in der Wiki-Fassung
# (temp/bre-wiki, die lizenzierte Quelle, ohne Wiki-Markup) oder im Wortlaut der Zeugen steht, in
# allen Dateien unter ingest/bre und scripts/ingest/bre und in den Commit Messages seit origin/main.
# URLs fallen auf beiden Seiten weg, Folgen aus lauter Ein-Buchstaben-Woertern (Siglenlisten) auch.
# Ziffern zaehlen nicht als Wort: eine Jahreszahl allein ist kein Wortlaut. Die Quellen liegen nur
# im Main Worktree und werden nie kopiert; fehlt eine davon, pdftotext oder der Wiki-Cache, faellt
# der Test aus und sagt das (er besteht dann nicht stillschweigend).
import os  # noqa: E402
import re as _re  # noqa: E402
import subprocess  # noqa: E402

DRUCK_N = 6


def druck_woerter(text):
    # Diakritika (auch die uebergeschriebenen e/o der Handschriften) fallen auf beiden Seiten weg,
    # sonst zerlegen sie ein Wort und eine Wiki-Folge sieht aus wie eine der Druckfassung
    import unicodedata
    text = _re.sub(r"https?://\S+", " ", text)
    roh = unicodedata.normalize("NFKD", text.lower())
    return _re.findall(r"[^\W\d_]+", "".join(c for c in roh if not unicodedata.combining(c)))


def druck_ngramme(woerter):
    return {g for g in (tuple(woerter[i:i + DRUCK_N]) for i in range(len(woerter) - DRUCK_N + 1))
            if any(len(w) > 1 for w in g)}


def wiki_klartext(inhalt):
    # Markup weg, sonst zerlegt <span ...>N</span>u ein Wort und der Vers zaehlt nicht als Wiki-Text
    import html as _html
    t = _re.sub(r"<[^>]+>|'{2,}", "", _html.unescape(inhalt))
    return _re.sub(r"\[\[|\]\]|\{\{|\}\}|\|", " ", t)


def druck_quellen():
    """Text der Druckfahnen (PDF) und der Steckbriefe aus dem Main Worktree, oder None."""
    common = subprocess.run(["git", "-C", str(conv.bc.REPO), "rev-parse", "--path-format=absolute",
                             "--git-common-dir"], capture_output=True, text=True).stdout.strip()
    basis = [p for p in (conv.bc.REPO / "sources" / "weingruesse",
                         Path(common).parent / "sources" / "weingruesse")
             if (p / "docling").is_dir() and (p / "wagner-2023-weingruesse-druckfahnen.pdf").is_file()]
    if not basis:
        return None
    try:
        pdf = subprocess.run(["pdftotext", "-enc", "UTF-8",
                              str(basis[0] / "wagner-2023-weingruesse-druckfahnen.pdf"), "-"],
                             capture_output=True, check=True).stdout.decode("utf-8")
    except (OSError, subprocess.CalledProcessError):
        return None
    pdf = _re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", pdf)
    if len(pdf) < 100000:  # Plausibilitaet: der Textauszug hat rund 189 KB
        return None
    return [pdf] + [md.read_text(encoding="utf-8") for md in sorted((basis[0] / "docling").glob("*.md"))]


def druckfahnen_lecks(dateien, texte=()):
    """Liefert [(Datei, Wortfolge)] fuer jede Wortfolge der Druckfahnen, die nur dort steht."""
    quellen = druck_quellen()
    wiki = sorted(conv.bc.CACHE_DIR.glob("rev_*.json")) if conv.bc.CACHE_DIR.is_dir() else []
    if not quellen or not wiki:
        return None
    druck = set()
    for q in quellen:
        druck |= druck_ngramme(druck_woerter(q))
    erlaubt = set()
    import json as _json
    for j in wiki:
        inhalt = _json.loads(j.read_text(encoding="utf-8"))["inhalt"]
        erlaubt |= druck_ngramme(druck_woerter(inhalt)) | druck_ngramme(druck_woerter(wiki_klartext(inhalt)))
    from lxml import etree as _et
    for tei in sorted(conv.bc.INGEST_DIR.glob("BRE_*.tei.xml")):
        ws = _et.parse(str(tei)).getroot().iter("{http://www.tei-c.org/ns/1.0}w")
        erlaubt |= druck_ngramme(druck_woerter(" ".join("".join(w.itertext()) for w in ws)))
    verboten = druck - erlaubt
    treffer = []
    for d in dateien:
        text = d.read_text(encoding="utf-8", errors="replace")
        # TSV je Feld: eine Folge ueber die Spaltengrenze (Blatt 221v + Incipit) ist keine Stelle
        teile = _re.split(r"[\t\n]", text) if d.suffix == ".tsv" else [text]
        gefunden = set()
        for t in teile:
            gefunden |= druck_ngramme(druck_woerter(t)) & verboten
        treffer += [(str(d), " ".join(g)) for g in sorted(gefunden)]
    for name, text in texte:
        treffer += [(name, " ".join(g)) for g in sorted(druck_ngramme(druck_woerter(text)) & verboten)]
    return treffer


druck_dateien = [p for basis in (conv.bc.INGEST_DIR, HIER) for p in sorted(basis.rglob("*"))
                 if p.is_file() and p.suffix in {".tsv", ".md", ".py", ".xml", ".txt", ".json", ".html"}]
_basis = subprocess.run(["git", "-C", str(conv.bc.REPO), "merge-base", "HEAD", "origin/main"],
                       capture_output=True, text=True).stdout.strip()
_log = subprocess.run(["git", "-C", str(conv.bc.REPO), "log", f"{_basis}..HEAD", "--format=%H%x00%B%x01"],
                      capture_output=True, text=True, encoding="utf-8").stdout if _basis else ""
druck_texte = [(f"Commit {e.split(chr(0))[0][:9]}", e.split(chr(0))[1])
               for e in _log.split("\x01") if "\x00" in e]
# zusaetzliche Texte (PR-Body, Issue-Kommentar) vor dem Absenden: BRE_DRUCK_PRUEFE=<datei>[;<datei>]
for _p in filter(None, os.environ.get("BRE_DRUCK_PRUEFE", "").split(";")):
    druck_texte.append((_p, Path(_p).read_text(encoding="utf-8")))
lecks = druckfahnen_lecks(druck_dateien, druck_texte)
if lecks is None:
    pruefe("Druckfahnen: kein Wortlaut im Repo", False,
           "Druckfahnen-PDF, pdftotext, Steckbriefe (sources/weingruesse/docling) oder Wiki-Cache "
           "(temp/bre-wiki) fehlen, Pruefung nicht moeglich")
else:
    pruefe(f"Druckfahnen: kein Wortlaut im Repo ({len(druck_dateien)} Dateien, "
           f"{len(druck_texte)} weitere Texte, {DRUCK_N}-Wort-Folgen)",
           not lecks, "; ".join(f"{d}: {g}" for d, g in lecks[:10]))

if fehler:
    print(f"{len(fehler)} Test(s) fehlgeschlagen:")
    for f in fehler:
        print("  - " + f[:200])
    sys.exit(1)
print("alle Tests bestanden")
