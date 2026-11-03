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
     "erster_vers": "Grüß dich got", "ueberschrift": ""},
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
       and d1.xpath("t:note[@type='editorial']", namespaces=ns)[0].text == conv.bc.VORSPANN_NOTIZ["fragment"])

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

if fehler:
    print(f"{len(fehler)} Test(s) fehlgeschlagen")
    sys.exit(1)
print("alle Tests bestanden")
