#!/usr/bin/env python3
"""Sechs um einen Vers verschobene Strophengrenzen in fuenf HUG-Liedern korrigieren (#138).

Befund (chsteiner, 2026-07-28, #138): Abgleich von tei/HUG.tei.xml mit der
Ausgabe Hofmeister 2005 (Hugo von Montfort, Das poetische Werk, de Gruyter).
In fuenf Liedern (Nr. 26 mit zwei Grenzen) steht bei uns eine Strophengrenze einen Vers zu frueh oder zu
spaet; die Verszaehlung (l/@n) stimmt ueberall. KZW stimmte am 2026-07-28 dem
Vorschlag zu, die Grenzen zu korrigieren, "wenn ihr sie bestaetigt".
Bestaetigt am 2026-11-08 am Druck (S. 33 fuer Nr. 6, S. 61 fuer Nr. 18; die
beiden Faelle, die am 28.07. Zweifel trugen) und fuer alle fuenf ueber das
Reimschema der Nachbarstrophen (fuer Nr. 3, 26 und 28 war der Abgleich vom
28.07. schon eindeutig). Entscheidung, sie jetzt umzusetzen: chsteiner,
2026-11-08.

  Nr.  Grenze im Druck  bei uns vorher        Korrektur
  3    Str. 4 ab V. 13  Str. 4 ab V. 12       V. 12 an das Ende von Str. 3
  6    Str. 2 ab V. 17  Str. 2 ab V. 18       V. 17 an den Anfang von Str. 2
  18   Str. 2 ab V. 5   Str. 2 ab V. 4        V. 4 an das Ende von Str. 1
  26   Str. 9 ab V. 33  Str. 9 ab V. 32       V. 32 an das Ende von Str. 8
  26   Str. 10 ab V. 37 Str. 10 ab V. 36      V. 36 an das Ende von Str. 9
  28   Str. 178 ab V. 709 Str. 178 ab V. 710  V. 709 an den Anfang von Str. 178

Verschoben wird nur das Paar </lg><lg type="stanza" n="..."> um einen Vers;
keine <l>, kein <w>, kein @n aendert sich. Die Folge aller Elemente bleibt
gleich, nur die Elternschaft eines <l> wechselt. Damit liegt die Aenderung
in der Zeile "<div>, <lg>, <pb> ... no rebuild" des Data-Change-Lifecycle
(docs/DATA-MODEL.md); die Leseansicht zeigt die Strophen, darum dort ansehen.

Pruefung nach dem Umbau, am geparsten Baum: dieselbe Folge von (Tag, xml:id,
Text) ueber alle Elemente unter <body>, und je betroffenem Lied die
Verszahlen jeder Strophe wie erwartet.

Aufruf: python scripts/hug-strophengrenzen-138.py [--apply]
"""

import argparse
import re
import sys
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[1]
DATEI = ROOT / "tei" / "HUG.tei.xml"
T = "{http://www.tei-c.org/ns/1.0}"

# (Lied, Vers, Richtung): "hoch" = Vers ans Ende der vorigen Strophe,
# "runter" = Vers an den Anfang der naechsten Strophe
FAELLE = [
    (3, 12, "hoch"),
    (6, 17, "runter"),
    (18, 4, "hoch"),
    (26, 32, "hoch"),
    (26, 36, "hoch"),
    (28, 709, "runter"),
]

# erwartete Verse der beteiligten Strophen danach: (Lied, Strophe) -> (erster, letzter)
SOLL = {
    (3, 3): (9, 12), (3, 4): (13, 16),
    (6, 1): (1, 16), (6, 2): (17, 32),
    (18, 1): (1, 4), (18, 2): (5, 8),
    (26, 8): (29, 32), (26, 9): (33, 36), (26, 10): (37, 40),
    (28, 177): (705, 708), (28, 178): (709, 712),
}

CHANGE = ('<change when="2026-11-08" who="#editor">#138: sechs um einen Vers '
          'verschobene Strophengrenzen nach Hofmeister 2005 korrigiert (Nr. 3 Str. 4, '
          'Nr. 6 Str. 2, Nr. 18 Str. 2, Nr. 26 Str. 9 und 10, Nr. 28 Str. 178); '
          'nur lg-Grenzen, Verse und Verszaehlung unveraendert. Skript '
          'scripts/hug-strophengrenzen-138.py.</change>')

GRENZE = r'([ \t]*</lg>\r?\n[ \t]*<lg type="stanza" n="\d+">\r?\n)'


def lied_bereich(text, nr):
    m = re.search(r'<div type="song" n="%d"[ >]' % nr, text)
    if not m:
        sys.exit("FEHLER: Lied %d nicht gefunden." % nr)
    ende = text.find("</div>", m.end())
    if text.find('<div type="song"', m.end(), ende) != -1:
        sys.exit("FEHLER: Lied %d ist verschachtelt." % nr)
    return m.start(), ende


def l_block(text, start, ende, vers):
    m = list(re.finditer(r'[ \t]*<l n="%d">.*?</l>\r?\n' % vers, text[start:ende], re.S))
    if len(m) != 1:
        sys.exit("FEHLER: <l n=%d> %d-mal im Lied." % (vers, len(m)))
    return start + m[0].start(), start + m[0].end()


def umbauen(text, nr, vers, richtung):
    a, e = lied_bereich(text, nr)
    la, le = l_block(text, a, e, vers)
    if richtung == "hoch":
        # Grenze steht direkt vor dem Vers; sie wandert hinter ihn
        g = re.compile(GRENZE + r'$').search(text, a, la)
        if not g or g.end() != la:
            sys.exit("FEHLER: Lied %d V. %d beginnt keine Strophe." % (nr, vers))
        return text[:g.start()] + text[la:le] + g.group(1) + text[le:]
    # Grenze steht direkt hinter dem Vers; sie wandert vor ihn
    g = re.compile(GRENZE).match(text, le)
    if not g:
        sys.exit("FEHLER: Lied %d V. %d schliesst keine Strophe." % (nr, vers))
    return text[:la] + g.group(1) + text[la:le] + text[g.end():]


def folge(root):
    body = root.find(".//" + T + "body")
    return [(el.tag, el.get("{http://www.w3.org/XML/1998/namespace}id"), (el.text or "").strip())
            for el in body.iter() if isinstance(el.tag, str) and el.tag not in (T + "lg",)]


def strophen(root):
    out = {}
    for d in root.iter(T + "div"):
        if d.get("type") != "song":
            continue
        for lg in d.findall(T + "lg"):
            ns = [int(l.get("n")) for l in lg.findall(T + "l")]
            out[(int(d.get("n")), int(lg.get("n")))] = (ns[0], ns[-1], len(ns))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    text = DATEI.read_text(encoding="utf-8", newline="")
    alt = etree.fromstring(text.encode("utf-8"))
    vorher = strophen(alt)
    for nr, vers, richtung in FAELLE:
        text = umbauen(text, nr, vers, richtung)

    if CHANGE in text:
        sys.exit("FEHLER: der revisionDesc-Eintrag steht schon in der Datei.")
    ende = text.index("</revisionDesc>")
    letzte = text.rfind("<change ", 0, ende)
    zeilenanfang = text.rfind("\n", 0, letzte) + 1
    einzug = text[zeilenanfang:letzte]
    zeilenende = text.index("\n", letzte) + 1
    umbruch = "\r\n" if text[zeilenende - 2:zeilenende] == "\r\n" else "\n"
    text = text[:zeilenende] + einzug + CHANGE + umbruch + text[zeilenende:]

    neu = etree.fromstring(text.encode("utf-8"))
    if folge(alt) != folge(neu):
        sys.exit("FEHLER: die Folge der Elemente unter <body> hat sich geaendert.")
    nachher = strophen(neu)
    if set(vorher) != set(nachher):
        sys.exit("FEHLER: die Menge der Strophen hat sich geaendert.")
    for key, (lo, hi) in SOLL.items():
        if nachher[key][:2] != (lo, hi):
            sys.exit("FEHLER: Lied %d Str. %d hat V. %d-%d, erwartet %d-%d."
                     % (key + nachher[key][:2] + (lo, hi)))
    geaendert = sorted(k for k in vorher if vorher[k] != nachher[k])
    if geaendert != sorted(SOLL):
        sys.exit("FEHLER: geaenderte Strophen %s, erwartet %s." % (geaendert, sorted(SOLL)))

    for k in geaendert:
        print("Lied %d Str. %d: V. %d-%d (%d) -> V. %d-%d (%d)" % (k + vorher[k] + nachher[k]))
    if args.apply:
        DATEI.write_text(text, encoding="utf-8", newline="")
    print("%d Grenzen, %d Strophen geaendert  %s"
          % (len(FAELLE), len(geaendert), "geschrieben" if args.apply else "Trockenlauf"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
