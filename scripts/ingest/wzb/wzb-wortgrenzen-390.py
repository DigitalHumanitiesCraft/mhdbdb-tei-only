#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#390: 16 ueber den Kolumnen- oder Seitenwechsel zerrissene Woerter zusammenfuehren.

In tei/WZB.tei.xml steht bei diesen Woertern zwischen den beiden Haelften ein
laufender Kolumnentitel als <w> (GENE, ESIS, EXO, DUS, LEUITICUS, ERI,
NOMIUS, DEUTRO), dazu <pb>/<cb>/<lb> und in einem Fall eine Kapitelzahl.
Gelesen wurde daraus "geschep ESIS fet" statt "geschepfet".

ENTSCHEIDUNGEN
--------------
- Kodierung (chsteiner, 2026-09-02, #390): zerrissene Woerter werden
  zusammengefuehrt, ohne Markierung (kein @part, kein <lb break="no"/>).
- Philologische Durchsicht (Klaus M. Schmidt, 2026-10-09, uebertragen von
  @wachauer am 2026-10-12 in #390): diese 16 ausdruecklich als
  "Zu einem Wort zusammenfuehren" bestaetigt, mit der hier gesetzten Wortform.
- Nicht hier: Nui|czig (Klaus schreibt "Nuinczig", das ist eine andere Form
  als die Zusammensetzung der Haelften und braucht eine eigene Entscheidung),
  ma|che (nur Entwurf, Bestaetigungsklick fehlt), die drei "andere Antwort"
  (c|egiptische, rrym|chende, xl|czeuknusses) und ouslegers|nOch (zwei
  Woerter). Ebenso nicht die Kodierung der Kolumnentitel und Kapitelzahlen
  (<fw>, <milestone>): braucht eine Schemaerweiterung, eigenes Paket.

WIE ZUSAMMENGEFUEHRT WIRD
-------------------------
Das zusammengefuehrte Wort steht dort, wo seine erste Haelfte stand, und
behaelt deren xml:id. Die zweite Haelfte (<w> ohne @lemmaRef) wird entfernt,
ihre xml:id entfaellt. Alles dazwischen, also die Umbrueche und der
Kolumnentitel, bleibt unveraendert und in derselben Reihenfolge stehen, nur
eben nach dem Wort statt mitten darin. Zwei Ausnahmen:
- bei isra|hel steht nach der ersten Haelfte ein Trennstrich als <pc>, der
  mit der Trennung wegfaellt;
- ein <pc join="left">, das direkt auf die zweite Haelfte folgte (Komma oder
  Punkt nach dem Wort, bei toech|tern, toech|ter, wis|sen, erwer|fen), wandert
  mit dem Wort und steht danach direkt hinter ihm, mit seiner xml:id. Bliebe
  es stehen, haengte die Leseansicht es an den Kolumnentitel ("EXO,").

Warum diese und keine andere Form: <lb>/<pb>/<cb> in das <w> zu ziehen
ginge nur ohne den Kolumnentitel, und der ist selbst ein <w>, das im Schema
nicht in einem <w> stehen darf; das Wort an die Stelle der zweiten Haelfte zu
setzen, wuerde die xml:id-Systematik (Blatt_Spalte_Zeile_Index) der ersten
Zeile brechen, in der das Wort beginnt. Die gewaehlte Form aendert nichts an
der Positionszaehlung: beide Haelften tragen kein @lemmaRef, und gezaehlt
werden nur <w> mit @lemmaRef.

Die Wortform ist die Verkettung der beiden Haelften so, wie sie in der Datei
stehen (bei toechter/toechtern also o plus U+0306 zerlegt, wie ueberall in
der WZB); geprueft wird sie in NFC gegen Klaus' Wortform.

Aufruf: python scripts/ingest/wzb/wzb-wortgrenzen-390.py [--apply]
Ohne --apply: Trockenlauf, prueft alles und schreibt das Protokoll in
ingest/wzb/390-wortgrenzen/. Nach dem Anwenden bricht jeder weitere Lauf an
der Formpruefung ab; das Protokoll im Repository ist dann der letzte Stand.
"""

import argparse
import csv
import re
import sys
import unicodedata
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
DATEI = ROOT / "tei" / "WZB.tei.xml"
LOG = ROOT / "ingest" / "wzb" / "390-wortgrenzen"

TEI = "{http://www.tei-c.org/ns/1.0}"
XID = "{http://www.w3.org/XML/1998/namespace}id"

# (Wortform nach Klaus, erste Haelfte, zweite Haelfte, Trennstrich-<pc> oder None)
TAFEL = [
    ("geschepfet", "WZB_13ra_35_6",  "WZB_13rb_2_0",  None),
    ("zukunftig",  "WZB_23va_32_6",  "WZB_23vb_2_0",  None),
    ("tŏchtern",   "WZB_26vb_34_5",  "WZB_27ra_2_0",  None),
    ("tŏchter",    "WZB_54vb_23_3",  "WZB_55ra_2_0",  None),
    ("czouberei",  "WZB_59va_20_2",  "WZB_59vb_2_0",  None),
    ("wissen",     "WZB_68ra_33_3",  "WZB_68rb_2_0",  None),
    ("erwerfen",   "WZB_76ra_37_4",  "WZB_76rb_2_0",  None),
    ("eines",      "WZB_87va_22_4",  "WZB_87vb_2_0",  None),
    ("opferten",   "WZB_88va_21_5",  "WZB_88vb_2_0",  None),
    ("machte",     "WZB_95va_37_4",  "WZB_95vb_2_0",  None),
    ("veistikeit", "WZB_104vb_36_8", "WZB_105ra_2_0", None),
    ("israhel",    "WZB_106vb_22_4", "WZB_107ra_2_0", "WZB_106vb_22_5"),
    ("Wenne",      "WZB_149ra_34_6", "WZB_149rb_2_0", None),
    ("vorkoufen",  "WZB_198ra_36_7", "WZB_198rb_2_0", None),
    ("besagunge",  "WZB_205ra_37_3", "WZB_205rb_2_0", None),
    ("horende",    "WZB_209rb_20_5", "WZB_209va_2_0", None),
]

ERLAUBT_DAZWISCHEN = {"lb", "pb", "cb", "w", "pc"}

CHANGE = ('<change when="2026-10-12" who="#editor">#390: {n} ueber den Kolumnen- oder '
          'Seitenwechsel zerrissene Woerter zusammengefuehrt (Kodierungsentscheidung '
          'vom 2026-09-02: ohne Markierung; Wortformen bestaetigt von Klaus M. Schmidt, '
          '2026-10-09). Das Wort steht an der Stelle und unter der xml:id seiner ersten '
          'Haelfte, die zweite Haelfte entfaellt, Umbrueche und Kolumnentitel bleiben '
          'dahinter stehen; ein direkt folgendes Komma oder ein Punkt (pc join=left) '
          'wandert mit dem Wort, bei israhel entfaellt der Trennstrich. Tafel in '
          'scripts/ingest/wzb/wzb-wortgrenzen-390.py.</change>')


def nackt(tag):
    return tag.replace(TEI, "") if isinstance(tag, str) else "?"


def strukturpruefung(tafel):
    """Prueft am geparsten Baum, dass zwischen den Haelften nur Umbrueche,
    unannotierte Kolumnentitel und (bei israhel) der Trennstrich stehen."""
    root = etree.parse(str(DATEI)).getroot()
    elemente = [e for e in root.iter() if isinstance(e.tag, str)]
    index = {e: i for i, e in enumerate(elemente)}
    nach_id = {e.get(XID): e for e in elemente if e.get(XID)}
    dazwischen = {}
    mitwandernd = {}
    for form, a, b, strich in tafel:
        ea, eb = nach_id.get(a), nach_id.get(b)
        if ea is None or eb is None:
            sys.exit("FEHLER: %s oder %s fehlt." % (a, b))
        for e in (ea, eb):
            if nackt(e.tag) != "w" or len(e) or e.get("lemmaRef"):
                sys.exit("FEHLER: %s ist kein unannotiertes, kinderloses <w>." % e.get(XID))
        if ea.getparent() is not eb.getparent():
            sys.exit("FEHLER: %s und %s haben verschiedene Eltern." % (a, b))
        teile = []
        for e in elemente[index[ea] + 1:index[eb]]:
            name = nackt(e.tag)
            if name not in ERLAUBT_DAZWISCHEN or e.getparent() is not ea.getparent():
                sys.exit("FEHLER: %s: unerwartetes <%s> zwischen den Haelften." % (form, name))
            if name == "w":
                text = (e.text or "").strip()
                if e.get("lemmaRef") or not text or text != text.upper():
                    sys.exit("FEHLER: %s: <w> %r zwischen den Haelften ist kein Kolumnentitel." % (form, text))
                teile.append(text)
            elif name == "pc":
                text = (e.text or "").strip()
                if e.get(XID) == strich:
                    if text != "-":
                        sys.exit("FEHLER: %s: Trennstrich %s traegt %r." % (form, strich, text))
                    teile.append("[-]")
                elif text == ".":
                    teile.append(".")
                else:
                    sys.exit("FEHLER: %s: unerwartetes <pc> %r." % (form, text))
            else:
                teile.append("<%s n=%s/>" % (name, e.get("n")))
        mit = []
        nachbar = eb.getnext()
        while nachbar is not None and nackt(nachbar.tag) == "pc" and nachbar.get("join") == "left":
            mit.append(nachbar.get(XID))
            nachbar = nachbar.getnext()
        mitwandernd[a] = mit
        if strich and "[-]" not in teile:
            sys.exit("FEHLER: %s: Trennstrich %s steht nicht zwischen den Haelften." % (form, strich))
        dazwischen[a] = " ".join(teile)
    return dazwischen, mitwandernd


def zeile_finden(text, element_re, xid):
    m = re.search(element_re, text)
    if not m:
        sys.exit("FEHLER: %s nicht gefunden." % xid)
    anfang = text.rfind("\n", 0, m.start()) + 1
    ende = text.index("\n", m.end()) + 1
    if text[anfang:m.start()].strip() or text[m.end():ende].strip():
        sys.exit("FEHLER: %s steht nicht allein auf seiner Zeile." % xid)
    return anfang, ende, m.group(0)


def zeile_entfernen(text, element_re, xid):
    anfang, ende, _ = zeile_finden(text, element_re, xid)
    return text[:anfang] + text[ende:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if len(TAFEL) != 16 or len({a for _, a, _, _ in TAFEL}) != 16:
        sys.exit("FEHLER: die Tafel deckt nicht genau 16 Woerter ab.")

    dazwischen, mitwandernd = strukturpruefung(TAFEL)
    text = DATEI.read_text(encoding="utf-8", newline="")
    zeilen = []
    for form, a, b, strich in TAFEL:
        ma = re.search(r'<w xml:id="%s">(?P<t>[^<]*)</w>' % re.escape(a), text)
        mb = re.search(r'<w xml:id="%s">(?P<t>[^<]*)</w>' % re.escape(b), text)
        if not ma or not mb:
            sys.exit("FEHLER: %s/%s nicht als unannotiertes <w> gefunden." % (a, b))
        h1, h2 = ma.group("t"), mb.group("t")
        wort = h1 + h2
        if unicodedata.normalize("NFC", wort) != unicodedata.normalize("NFC", form):
            sys.exit("FEHLER: %s + %s ergibt %r, erwartet %r." % (a, b, wort, form))
        text = text[:ma.start()] + '<w xml:id="%s">%s</w>' % (a, wort) + text[ma.end():]
        text = zeile_entfernen(text, r'<w xml:id="%s">[^<]*</w>' % re.escape(b), b)
        if strich:
            text = zeile_entfernen(text, r'<pc xml:id="%s" join="left">-</pc>' % re.escape(strich), strich)
        # mitwandernde Interpunktion: Zeile ausschneiden, hinter das Wort setzen
        for pid in reversed(mitwandernd[a]):
            pc_re = r'<pc xml:id="%s" join="left">[^<]*</pc>' % re.escape(pid)
            anfang, ende, element = zeile_finden(text, pc_re, pid)
            text = text[:anfang] + text[ende:]
            wa, we, _ = zeile_finden(text, r'<w xml:id="%s">[^<]*</w>' % re.escape(a), a)
            einzug = text[wa:text.index("<", wa)]
            umbruch = "\r\n" if text[we - 2:we] == "\r\n" else "\n"
            text = text[:we] + einzug + element + umbruch + text[we:]
        zeilen.append(dict(xml_id=a, form=wort, haelfte_1=h1, haelfte_2=h2,
                           xml_id_entfernt=" ".join(x for x in (b, strich) if x),
                           dazwischen=dazwischen[a],
                           pc_mitgewandert=" ".join(mitwandernd[a]), action="MERGE"))

    change = CHANGE.format(n=len(TAFEL))
    if change in text:
        sys.exit("FEHLER: der revisionDesc-Eintrag steht schon in der Datei.")
    ende = text.index("</revisionDesc>")
    letzte = text.rfind("<change ", 0, ende)
    zeilenanfang = text.rfind("\n", 0, letzte) + 1
    einzug = text[zeilenanfang:letzte]
    zeilenende = text.index("\n", letzte) + 1
    umbruch = "\r\n" if text[zeilenende - 2:zeilenende] == "\r\n" else "\n"
    text = text[:zeilenende] + einzug + change + umbruch + text[zeilenende:]

    etree.fromstring(text.encode("utf-8"))  # wohlgeformt?

    if args.apply:
        DATEI.write_text(text, encoding="utf-8", newline="")

    LOG.mkdir(parents=True, exist_ok=True)
    with open(LOG / "diff-liste.csv", "w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(zeilen[0]), delimiter=";")
        wr.writeheader()
        wr.writerows(zeilen)

    print("zusammengefuehrt: %d  %s" % (len(zeilen), "geschrieben" if args.apply else "Trockenlauf"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
