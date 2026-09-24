#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#235 Punkt 1, Nachtrag: die 34 Split-Tokens lemmatisieren.

f3dcf2a86 hat 17 WZB-<w> mit literalem Backslash-u0020 in je zwei <w> zerlegt
(Entscheidung von Julia Hintersteiner am 2026-08-26, "Alle diese Tokens in
zwei splitten"). Entschieden war damit das Aufteilen, nicht die
Lemmatisierung: alle 34 Tokens stehen seither ohne @lemmaRef da.

HERKUNFT DER TAFEL
------------------
Ein Vorschlag fuer 28 der 34 lag auf dem nie gemergten Zweig
claude/235-315-wzb-tokens-lead-editor (26d907129, 2026-08-21). Er ist hier
nicht uebernommen, sondern Zeile fuer Zeile neu gemessen worden, an zwei
Dingen:

  1. der Belegverteilung derselben (MHG-normalisierten) Form, in der WZB und
     im ganzen Korpus;
  2. dem Vers, und wo er nicht reichte, der Vulgata-Stelle, die die WZB
     uebersetzt.

Ergebnis: 27 der 28 halten, eine nicht (WZB_116va_14_6b, siehe REVIEW unten).
Dazu kommen die drei "in", die der Zweig offen liess: der Vers entscheidet sie
eindeutig als Praeposition. Und vier Zuordnungen, die der Zweig ohne @pos
gesetzt hatte, weil die Belegverteilung nicht einstimmig war, bekommen hier
eine, weil der Vers es ist (ir vor seit, vor mit Pronomen, einem vor Nomen).

Kein @ana (die Sense-Zuordnung ist kuratorisch, Regel wie #189/#198/#216/#369)
und kein @corresp (braeuchte neu gepraegte Typnummern, und neue Typen sind
genehmigungspflichtig; Lage wie bei den 52.097 WZB-Tokens aus #370).

Die zwei sie-Lemmata (lemma_5454 und lemma_56116) sind im Lexikon nicht
geschieden. Die WZB legt sie, ire und iren zu 2.400 von 2.407 Belegen auf
lemma_5454 (1.963 + 260 + 177 von 1.963 + 267 + 177); die Tafel folgt dieser Hauspraxis und entscheidet die Frage nicht.

Aufruf: python scripts/ingest/wzb/wzb-split-token-lemmata.py [--apply]
Ohne --apply wird nur das Provenienz-Log geschrieben.
"""

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATEI = ROOT / "tei" / "WZB.tei.xml"
LOG = ROOT / "ingest" / "wzb" / "235-split-tokens"

# xml:id -> (Form, Lemma, pos, Beleg). Beleg: Belegverteilung der Form in der
# WZB (Lemma/pos: Anzahl) und, wo sie nicht einstimmig ist, der Vers.
ANNOTIEREN = {
    "WZB_55rb_23_13":   ("et",      "lemma_78608", "ADV",  "WZB 16/16 lemma_78608 ADV; das et cetera zwei Tokens davor traegt dasselbe"),
    "WZB_55rb_23_13b":  ("cetera",  "lemma_33125", "ADJ",  "WZB 15/15 lemma_33125 ADJ"),
    "WZB_69va_2_2":     ("in",      "lemma_3028",  "PRP",  "in seiner mitte (Ex 14,29 per medium): Rektion"),
    "WZB_69va_2_2b":    ("seiner",  "lemma_1517",  "POS",  "WZB 214/214 lemma_1517 POS"),
    "WZB_119rb_13_4":   ("in",      "lemma_3028",  "PRP",  "noch in trovme gelouben (Lev 19,26): Rektion"),
    "WZB_119rb_13_4b":  ("trovme",  "lemma_6239",  "NOM",  "WZB 12/12 lemma_6239 NOM"),
    "WZB_119va_21_2":   ("wenne",   "lemma_7385",  "SCNJ", "WZB 841/841 lemma_7385 SCNJ"),
    "WZB_119va_21_2b":  ("ir",      "lemma_56117", "PRO",  "WZB lemma_56117 693 PRO/468 POS; ir seit: Subjekt"),
    "WZB_124rb_8_4":    ("herren",  "lemma_2684",  "NOM",  "WZB 888/888 lemma_2684 NOM"),
    "WZB_124rb_8_4b":   ("gote",    "lemma_2465",  "NOM",  "WZB 128/128 lemma_2465 NOM"),
    "WZB_127rb_20_1":   ("vor",     "lemma_7194",  "PRP",  "WZB 577 PRP/86 ADV; vallen vor euch (Lev 26,8 coram vobis)"),
    "WZB_127rb_20_1b":  ("euch",    "lemma_56117", "PRO",  "WZB 569/569 lemma_56117 PRO"),
    "WZB_135va_15_0":   ("vor",     "lemma_7194",  "PRP",  "WZB 577 PRP/86 ADV; opfer vor sie (Lev 5,11 pro peccato)"),
    "WZB_135va_15_0b":  ("sie",     "lemma_5454",  "PRO",  "WZB 1963/1963 lemma_5454 PRO"),
    "WZB_143vb_10_4b":  ("einem",   "lemma_1331",  "DET",  "WZB 199 DET/14 NUM; einem topfe: Artikel"),
    "WZB_154rb_14_4":   ("Herre",   "lemma_2684",  "NOM",  "WZB 1033/1033 lemma_2684 NOM"),
    "WZB_154rb_14_4b":  ("got",     "lemma_2465",  "NOM",  "WZB 532/532 lemma_2465 NOM"),
    "WZB_158va_11_5":   ("er",      "lemma_1517",  "PRO",  "WZB 590/590 lemma_1517 PRO"),
    "WZB_158va_11_5b":  ("gabe",    "lemma_1839",  "NOM",  "WZB 46/46 lemma_1839 NOM"),
    "WZB_162vb_9_1":    ("zu",      "lemma_7770",  "PRP",  "WZB 2568/2568 lemma_7770 PRP"),
    "WZB_162vb_9_1b":   ("iren",    "lemma_5454",  "POS",  "WZB 177/177 lemma_5454 POS"),
    "WZB_165vb_33_1":   ("zu",      "lemma_7770",  "PRP",  "WZB 2568/2568 lemma_7770 PRP"),
    "WZB_165vb_33_1b":  ("den",     "lemma_1119",  "DET",  "WZB 2087/2087 lemma_1119 DET"),
    "WZB_179ra_5_5":    ("her",     "lemma_1517",  "PRO",  "WZB 1497/1497 lemma_1517 PRO; also tu her allen reichen (Dtn 3,21 sic faciet)"),
    "WZB_179ra_5_5b":   ("allen",   "lemma_106",   "ADJ",  "WZB 173/173 lemma_106 ADJ"),
    "WZB_219va_16_0":   ("ire",     "lemma_5454",  "POS",  "WZB 260 lemma_5454/7 lemma_56116, alle POS"),
    "WZB_219va_16_0b":  ("teil",    "lemma_6041",  "NOM",  "WZB 105/105 lemma_6041 NOM"),
    "WZB_222ra_19_2":   ("vorwar",  "lemma_8989",  "ADV",  "WZB 97/97 lemma_8989 ADV; Jos 8,26 Iosue vero"),
    "WZB_222ra_19_2b":  ("czoch",   "lemma_7861",  "VRB",  "WZB 99/99 lemma_7861 VRB"),
    "WZB_227ra_19_1":   ("in",      "lemma_3028",  "PRP",  "in salacha (Jos 12,5 in Salecha): Rektion"),
}

# Bleiben byte-identisch stehen und gehen als Frage an KZW.
REVIEW = {
    "WZB_116va_14_6":   ("Gen",     "Lev 16,26 Ille vero, qui dimiserit caprum emissarium: 'Gen er vor war, der do hat gelasen den ous gesanten czigen pok'. Gen er steht fuer ille (jener), nicht fuer gegen + er. Welches Lemma, und ist der Split hier richtig?"),
    "WZB_116va_14_6b":  ("er",      "Wie WZB_116va_14_6. Der Zweig vom 21.08. hatte lemma_1517 PRO gesetzt, das traegt nur, wenn Gen und er zwei Woerter sind."),
    # Zerlegt gespeichert (i + U+0304), nicht als praekomponiertes U+012B.
    "WZB_143vb_10_4":   ("ī", "Num 11,8 coquentes in olla: 'cochte das ī einem topfe'. i mit Nasalstrich fuer in, also lemma_3028 PRP. Gehoert zu den offenen Makron-Tokens aus #235 Punkt 3, deshalb nicht hier entschieden."),
    "WZB_227ra_19_1b":  ("salacha", "Jos 12,5 Salecha, Ortsname. Kein Lemma im Lexikon (0 Belege der Form im Korpus); braucht einen Namenseintrag."),
}

W_RE = r'<w xml:id="{xid}">(?P<form>[^<]*)</w>'

CHANGE = ('<change when="2026-09-24" who="#editor">#235 Punkt 1, Nachtrag: {n} der 34 '
          'Tokens aus dem Split von f3dcf2a86 lemmatisiert (lemmaRef und pos), nach '
          'Belegverteilung der Form in der WZB und am Vers. {r} bleiben unannotiert '
          'und gehen an KZW. Kein @ana, kein @corresp. Tafel in '
          'scripts/ingest/wzb/wzb-split-token-lemmata.py.</change>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    if len(ANNOTIEREN) + len(REVIEW) != 34 or set(ANNOTIEREN) & set(REVIEW):
        sys.exit("FEHLER: die Tafel deckt nicht genau die 34 Split-Tokens ab.")

    text = DATEI.read_text(encoding="utf-8", newline="")
    zeilen = []
    for xid, (form, lemma, pos, beleg) in ANNOTIEREN.items():
        m = re.search(W_RE.format(xid=re.escape(xid)), text)
        if not m:
            sys.exit("FEHLER: <w xml:id=%s> nicht unannotiert gefunden." % xid)
        if m.group("form") != form:
            sys.exit("FEHLER: %s: Tokentext %r != %r" % (xid, m.group("form"), form))
        neu = '<w xml:id="%s" lemmaRef="lexicon.xml#%s" pos="%s">%s</w>' % (xid, lemma, pos, form)
        text = text[:m.start()] + neu + text[m.end():]
        zeilen.append(dict(xml_id=xid, form=form, action="ANNOTATE", lemmaRef=lemma, pos=pos, beleg=beleg))
    for xid, (form, frage) in REVIEW.items():
        m = re.search(W_RE.format(xid=re.escape(xid)), text)
        if not m or m.group("form") != form:
            sys.exit("FEHLER: Review-Token %s nicht unannotiert mit Form %r gefunden." % (xid, form))
        zeilen.append(dict(xml_id=xid, form=form, action="REVIEW", lemmaRef="", pos="", beleg=frage))

    change = CHANGE.format(n=len(ANNOTIEREN), r=len(REVIEW))
    if change in text:
        sys.exit("FEHLER: der revisionDesc-Eintrag steht schon in der Datei.")
    ende = text.index("</revisionDesc>")
    letzte = text.rfind("<change ", 0, ende)
    zeilenanfang = text.rfind("\n", 0, letzte) + 1
    einzug = text[zeilenanfang:letzte]
    zeilenende = text.index("\n", letzte) + 1
    umbruch = "\r\n" if text[zeilenende - 2:zeilenende] == "\r\n" else "\n"
    text = text[:zeilenende] + einzug + change + umbruch + text[zeilenende:]

    if args.apply:
        DATEI.write_text(text, encoding="utf-8", newline="")

    LOG.mkdir(parents=True, exist_ok=True)
    for name, auswahl in (("diff-liste.csv", zeilen),
                          ("review-faelle.csv", [z for z in zeilen if z["action"] == "REVIEW"])):
        with open(LOG / name, "w", encoding="utf-8-sig", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=list(zeilen[0]), delimiter=";")
            wr.writeheader()
            wr.writerows(auswahl)

    print("annotiert: %d (von 34)  review: %d  %s" % (
        len(ANNOTIEREN), len(REVIEW), "geschrieben" if args.apply else "Trockenlauf"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
