#!/usr/bin/env python3
"""Tests fuer 02-convert-wiki-to-mhdbdb.py (BRE, #147), pytest-frei.

Aufruf: python -P -E scripts/ingest/bre/test_bre.py
Kein Netz, kein Cache: Mini-Fixture (Ausschnitt aus Cgm 713, Revision 21352).
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

if fehler:
    print(f"{len(fehler)} Test(s) fehlgeschlagen")
    sys.exit(1)
print("alle Tests bestanden")
