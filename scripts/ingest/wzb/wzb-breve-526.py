#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#526: der Rest des Breve-Backfills aus #235 Punkt 3, Punkte 1 und 2.

wzb-breve-backfill.py findet am 2026-10-06 noch 134 Breve-Kandidaten auf o/u.
Dieses Skript entscheidet die 25 davon, die ohne Lexikonarbeit entscheidbar
sind, Fall fuer Fall mit einer offenliegenden Entscheidungstafel, nach dem
Muster von wzb-breve-wortart.py (#389):

  1   mechanisch eindeutig (der Backfill wuerde ihn selbst annotieren)
  13  lemma-mehrdeutig: die normalisierte Form trifft mehrere Lemmata, die
      Wahl faellt am Vers
  11  pos-mehrdeutig: ein Lemma, mehrere Wortarten. NEUN davon hat #389 schon
      am Vers entschieden und bewusst zurueckgehalten (fuenf mit mittlerer
      Konfidenz, vier mit unpassendem Ziel-Lemma). Diese Entscheidungen
      werden hier NICHT neu getroffen, sondern unveraendert uebernommen; sie
      stehen in wzb-breve-wortart.py mit Begruendung. Neu sind nur zwei.

Die 109 Lexikonluecken (Punkt 3 des Tickets), die 48 w/n-Tokens (Punkt 4) und
die 8 Makron-Tokens (Punkt 5) fasst dieses Skript nicht an.

REGELN wie in #389 (R1 bis R9). Neu ist L: die Wahl zwischen den gemessenen
Kandidatenlemmata. Gewaehlt wird nur unter den Kandidaten, die der Matcher
geliefert hat. Ist das richtige Lemma keiner davon, geht der Fall in den
Rueckhalt, denn ein anderes Lemma zu setzen als das gemessene ist eine
philologische Entscheidung und gehoert zu KZW (Begruendung in #389).

Annotiert wird nur bei hoher Konfidenz (Regel aus #369). GRA wird nie
vergeben (POS-TAGSET 3 und 6.3d). KEIN @corresp, KEIN @ana, Begruendung wie
in wzb-breve-wortart.py.

FOLGEN: @lemmaRef kommt neu hinzu, also Korpus-Index, API und Begriffshilfe
neu bauen; variants.xml und der Authority-Index bleiben unberuehrt.

Nicht idempotent: ein zweiter Lauf findet die Tokens annotiert vor und bricht
ab.

Usage:
    python scripts/ingest/wzb/wzb-breve-526.py \
        --quelle ingest/wzb/526-breve/diff-liste.csv \
        --out-dir ingest/pos-disambig/526-breve-rest [--apply]
"""
import argparse
import csv
import gzip
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DATEI = REPO / "tei" / "WZB.tei.xml"
AUTH_INDEX = REPO / "data" / "authority-index.json.gz"

TAGS_19 = {"NOM", "NAM", "ADJ", "ADV", "DET", "POS", "PRO", "PRP", "NEG", "NUM",
           "CNJ", "SCNJ", "CCNJ", "IPA", "VRB", "VEX", "VEM", "INJ", "DIG"}

REGELN = {
    "R1": "Adjektiv mit Bezugsnomen in der Phrase oder als Praedikat",
    "R2": "Substantivierung: besetzt die Nominalstelle selbst",
    "R4": "Vollverb",
    "R9": "Substantiv",
    "M": "mechanisch eindeutig (ein Lemma, eine Wortart)",
}

# xml:id -> (lemma, pos, regel, konfidenz, kurzbegruendung am Text)
ENTSCHEIDUNGEN = {
    # --- Punkt 1: der mechanische Fall -----------------------------------------
    "WZB_148va_17_2":  ("lemma_784",  "NOM", "M",  "hoch",   "wider vnd lemmer vnd pŏcke"),
    # --- pos-mehrdeutig, neu seit #389 -----------------------------------------
    "WZB_179ra_13_2":  ("lemma_2534", "NOM", "R2", "hoch",   "zv czeigen deine grŏse vnd deine gar starcke hant"),
    "WZB_179ra_31_0":  ("lemma_4449", "NOM", "R9", "hoch",   "gegen zuden vnd gegen ŏsten, nach Praeposition"),
    # --- lemma-mehrdeutig: Wahl unter den gemessenen Kandidaten ----------------
    "WZB_53ra_28_0":   ("lemma_6223", "VRB", "R4", "hoch",   "vnd trŏste sie vnd sprach, troesten statt trôst"),
    "WZB_55va_10_6":   ("lemma_3837", "VRB", "R4", "hoch",   "Lŏse deine schuh, Imperativ, lœsen statt lôs"),
    "WZB_91vb_19_2":   ("lemma_3837", "VRB", "R4", "hoch",   "erst geburt deiner svne lŏse, lœsen statt lôs"),
    "WZB_78rb_6_4":    ("lemma_5786", "VRB", "R4", "hoch",   "svnder stŏre sie vnd zu brich, Imperativ, stœren statt Name"),
    "WZB_116rb_16_2":  ("lemma_7704", "ADJ", "R1", "hoch",   "in eine wŭste erde, wüeste statt wiʒʒen"),
    "WZB_152va_16_3":  ("lemma_5864", "ADJ", "R1", "hoch",   "in einem sŭzen ruche, süeʒe statt süezen"),
    "WZB_158va_14_5":  ("lemma_7283", "VRB", "R4", "hoch",   "do fŭrt er in zu, vüeren statt vurt"),
    "WZB_181va_37_0":  ("lemma_5034", "NOM", "R9", "hoch",   "das ist rŭ deines herren gotes, ruowe statt riuwe"),
    "WZB_182vb_27_6":  ("lemma_2942", "VRB", "R4", "hoch",   "so hŭte dich vleissiclich, hüeten"),
    "WZB_211va_28_3":  ("lemma_4400", "NOM", "R9", "hoch",   "beschirmen euch in ewern nŏten, nôt statt noeten"),
    "WZB_217ra_17_0":  ("lemma_7298", "VRB", "R4", "hoch",   "so das si in vŏrchten als sie vorchten, vürhten statt vorhte"),
    "WZB_150vb_15_2":  ("lemma_6118", "NOM", "R9", "mittel", "geheiligt in den tŏden der svnder"),
}

ALTERNATIVE = {
    "WZB_150vb_15_2": "lemma_6133 tœten NOM, wenn 'in den tŏden' als "
                      "substantivierter Infinitiv (das Toeten) gelesen wird "
                      "statt als Tod; der Vers allein entscheidet es nicht.",
}

# xml:id -> (kuerzel, begruendung)
RUECKHALT = {
    "WZB_181vb_9_3": (
        "Z4",
        "'Und dein knecht rŭ vnd dein mait' (requiescat) ist das Verb ruowen. "
        "Gemessen sind nur riuwe (lemma_4937) und ruowe NOM (lemma_5034); das "
        "Verblemma lemma_5035 ruowen NOM VRB gibt es, es ist aber kein "
        "Kandidat. Ein anderes Lemma zu setzen als das gemessene entscheidet "
        "KZW."),
}
# Die neun, die #389 am Vers entschieden und zurueckgehalten hat. Sie werden
# hier nur durchgereicht; die Begruendung steht in wzb-breve-wortart.py
# (ALTERNATIVE bzw. RUECKHALT).
AUS_389 = {
    "WZB_28rb_34_12": "#389 Konfidenz mittel (ADV vs. ADJ)",
    "WZB_183ra_36_2": "#389 Konfidenz mittel (ADJ vs. NOM)",
    "WZB_119rb_6_1":  "#389 Konfidenz mittel (ADJ vs. ADV)",
    "WZB_202rb_8_2":  "#389 Konfidenz mittel (NOM vs. ADJ)",
    "WZB_98vb_8_5":   "#389 Konfidenz mittel (ADV vs. PRP)",
    "WZB_11rb_21_2":  "#389 Z1: Verb grôzen (lemma_2535), kein Kandidat",
    "WZB_213ra_5_0":  "#389 Z2: hort (lemma_2908), nicht hœren",
    "WZB_26vb_34_5":  "#389 Z3: tŏch|ter, durch Blattmarker zerrissen (#390)",
    "WZB_54vb_23_3":  "#389 Z3: tŏch|ter, durch Blattmarker zerrissen (#390)",
}

W_TEMPLATE = r'<w xml:id="{xid}"(?: pos="(?P<oldpos>[A-Z]+)")?>(?P<form>[^<]*)</w>'

CHANGE_VORLAGE = (
    '<change when="{datum}" who="#editor">#526 (Rest von #235 Punkt 3): {n} '
    'Breve-Tokens nachannotiert (lemmaRef und pos): der eine mechanisch '
    'eindeutige Fall, die Wahl unter mehreren gemessenen Lemmata am Vers und '
    'zwei neue Faelle mit mehrdeutiger Wortart, nach den offengelegten Regeln '
    'im Skript. Annotiert nur bei hoher Konfidenz, GRA nie. {r} der {g} '
    'Faelle bleiben unannotiert, davon {a} unveraendert aus #389. Kein corresp '
    'und kein ana. Provenienz-Log: {log}.</change>'
)


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def repo_relativ(p):
    p = pfad(p).resolve()
    try:
        return p.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        sys.exit("FEHLER: %s liegt ausserhalb des Repositoriums." % p)


def nfc(s):
    return unicodedata.normalize("NFC", s or "")


def lade_lemma_pos():
    idx = json.load(gzip.open(AUTH_INDEX, "rt", encoding="utf-8"))
    aus = {}
    for l in idx["lemmata"]:
        pa = l.get("posAll") or ([l["pos"]] if l.get("pos") else [])
        aus[l["id"]] = ([p for p in pa if p], l.get("lemma", ""))
    return aus


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--quelle", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    with pfad(args.quelle).open(encoding="utf-8-sig") as fh:
        alle = list(csv.DictReader(fh, delimiter=";"))
    faelle = [r for r in alle if r["action"] == "ANNOTATE"
              or r["review_grund"] in ("lemma-mehrdeutig", "pos-mehrdeutig")]

    ids_csv = {r["xml_id"] for r in faelle}
    tafeln = (set(ENTSCHEIDUNGEN), set(RUECKHALT), set(AUS_389))
    ids_tafel = set().union(*tafeln)
    if ids_csv != ids_tafel:
        sys.exit("FEHLER: Tafel und Faelle decken sich nicht.\n"
                 "  ohne Entscheidung: %s\n  nicht in der Quelle: %s"
                 % (sorted(ids_csv - ids_tafel) or "-",
                    sorted(ids_tafel - ids_csv) or "-"))
    if sum(len(t) for t in tafeln) != len(ids_tafel):
        sys.exit("FEHLER: eine xml:id steht in mehr als einer Tafel.")

    lemma_pos = lade_lemma_pos()
    zeilen = []
    for r in sorted(faelle, key=lambda r: r["xml_id"]):
        xid = r["xml_id"]
        kandidaten = (r["lemma_kandidaten"] or "").split()
        basis = {"file": DATEI.name, "xml_id": xid, "form": r["form"],
                 "normalisiert": r["normalisiert"],
                 "quelle_grund": r["review_grund"] or r["action"],
                 "lemma_kandidaten": " ".join(kandidaten),
                 "vers": r["vers"], "umfeld": r["umfeld"]}
        if xid in ENTSCHEIDUNGEN:
            lemma, pos, regel, konf, grund = ENTSCHEIDUNGEN[xid]
            posAll, lemmaform = lemma_pos.get(lemma, ([], ""))
            if lemma not in kandidaten:
                sys.exit("FEHLER: %s: %s ist kein gemessener Kandidat (%s). "
                         "Ein solcher Fall gehoert in den Rueckhalt."
                         % (xid, lemma, " ".join(kandidaten)))
            if pos not in TAGS_19 or pos not in posAll:
                sys.exit("FEHLER: %s bekaeme %r, %s fuehrt %s"
                         % (xid, pos, lemma, " ".join(posAll)))
            if konf != "hoch":
                if xid not in ALTERNATIVE:
                    sys.exit("FEHLER: %s: Konfidenz %r ohne ALTERNATIVE." % (xid, konf))
                zeilen.append(dict(basis, action="REVIEW",
                                   review_grund="konfidenz-" + konf,
                                   neu_lemmaRef="", neu_pos="", regel=regel,
                                   begruendung="Vorschlag %s %s nach %s (%s); dagegen: %s"
                                   % (lemma, pos, regel, grund, ALTERNATIVE[xid]),
                                   konfidenz=konf, ziel_lemma_form=lemmaform))
                continue
            zeilen.append(dict(basis, action="ANNOTATE", review_grund="",
                               neu_lemmaRef="lexicon.xml#" + lemma, neu_pos=pos,
                               regel=regel, begruendung=REGELN[regel] + ": " + grund,
                               konfidenz=konf, ziel_lemma_form=lemmaform))
        elif xid in RUECKHALT:
            kuerzel, text = RUECKHALT[xid]
            zeilen.append(dict(basis, action="REVIEW",
                               review_grund="ziel-lemma-passt-nicht/" + kuerzel,
                               neu_lemmaRef="", neu_pos="", regel=kuerzel,
                               begruendung=text, konfidenz="", ziel_lemma_form=""))
        else:
            zeilen.append(dict(basis, action="REVIEW", review_grund="aus-389",
                               neu_lemmaRef="", neu_pos="", regel="",
                               begruendung=AUS_389[xid], konfidenz="",
                               ziel_lemma_form=""))

    text = DATEI.read_text(encoding="utf-8", newline="")
    geschrieben = 0
    for z in zeilen:
        if z["action"] != "ANNOTATE":
            continue
        m = re.search(W_TEMPLATE.format(xid=re.escape(z["xml_id"])), text)
        if not m:
            sys.exit("FEHLER: <w xml:id=%s> nicht unannotiert gefunden." % z["xml_id"])
        if nfc(m.group("form")).strip() != nfc(z["form"]):
            sys.exit("FEHLER: %s: Tokentext %r != erwartete Form %r"
                     % (z["xml_id"], m.group("form"), z["form"]))
        if m.group("oldpos"):
            sys.exit("FEHLER: %s traegt bereits pos=%r" % (z["xml_id"], m.group("oldpos")))
        neu = ('<w xml:id="%s" lemmaRef="%s" pos="%s">%s</w>'
               % (z["xml_id"], z["neu_lemmaRef"], z["neu_pos"], m.group("form")))
        text = text[:m.start()] + neu + text[m.end():]
        geschrieben += 1

    n_review = sum(1 for z in zeilen if z["action"] == "REVIEW")
    change = CHANGE_VORLAGE.format(datum="2026-10-06", n=geschrieben, r=n_review,
                                   g=len(zeilen), a=len(AUS_389),
                                   log=repo_relativ(args.out_dir))
    if change in text:
        sys.exit("FEHLER: der revisionDesc-Eintrag steht schon in der Datei.")
    if "</revisionDesc>" not in text:
        sys.exit("FEHLER: kein </revisionDesc> in %s" % DATEI.name)
    letzte = text.rfind("<change ", 0, text.index("</revisionDesc>"))
    if letzte < 0:
        sys.exit("FEHLER: kein vorhandener <change> in %s" % DATEI.name)
    zeilenanfang = text.rfind("\n", 0, letzte) + 1
    einzug = text[zeilenanfang:letzte]
    zeilenende = text.index("\n", letzte) + 1
    umbruch = "\r\n" if text[zeilenende - 2:zeilenende] == "\r\n" else "\n"
    text = text[:zeilenende] + einzug + change + umbruch + text[zeilenende:]

    if args.apply:
        DATEI.write_text(text, encoding="utf-8", newline="")

    out = pfad(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    spalten = list(zeilen[0].keys())
    for name, auswahl in (("diff-liste.csv", zeilen),
                          ("review-faelle.csv",
                           [z for z in zeilen if z["action"] == "REVIEW"])):
        with open(out / name, "w", encoding="utf-8-sig", newline="") as fh:
            wr = csv.DictWriter(fh, fieldnames=spalten, delimiter=";")
            wr.writeheader()
            wr.writerows(auswahl)

    modus = "APPLY" if args.apply else "DRY-RUN"
    print("[%s] Faelle: %d" % (modus, len(zeilen)))
    print("  ANNOTATE: %d, REVIEW: %d (%d + %d + %d)" % (
        geschrieben, n_review,
        sum(1 for z in zeilen if z["review_grund"].startswith("konfidenz-")),
        len(RUECKHALT), len(AUS_389)))
    print("  Wortarten:", dict(Counter(z["neu_pos"] for z in zeilen if z["action"] == "ANNOTATE")))
    print("  Regeln:", dict(Counter(z["regel"] for z in zeilen if z["action"] == "ANNOTATE")))
    print("  Artefakte:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
