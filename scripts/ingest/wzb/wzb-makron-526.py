#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#526 Punkt 5: die 8 unannotierten WZB-Tokens mit kombinierendem Makron (U+0304).

Das Makron ist in der WZB kein Laengenzeichen. Bei vn̄ und ī ist es ein
Kuerzungsstrich (vnd, in); bei flūte, Dorūmbe, fūrbas und vnd̄ steht es auf
einer Form, die auch ohne Strich vollstaendig ist. Verglichen wird deshalb mit
der Form ohne Makron, nur bei ī mit dem ausgeschriebenen in. Entschieden wird
jeder Fall am Vers, und zwar nur, wenn die Vergleichsform in der WZB selbst
schon so annotiert ist. Die Tafel unten nennt je Fall die
Vergleichsform; das Skript misst deren Annotation im TEI nach und bricht ab,
wenn sie das gewaehlte Lemma mit der gewaehlten Wortart nicht traegt.

Regeln:
  E  Die Vergleichsform traegt in der WZB ausnahmslos dieses Lemma und diese
     Wortart. Der Vers widerspricht nicht.
  V  Die Vergleichsform ist mehrdeutig, der Vers entscheidet (ī vor
     "einem topfe" ist die Praeposition, nicht das Pronomen).

Nicht annotiert: die beiden cap̄. Sie stehen in der lateinischen Kapitelrubrik
("X cap̄ GENE"), sind also kein mittelhochdeutsches Wort.

KEIN @corresp, KEIN @ana, wie im Lauf zu den Breve-Tokens
(wzb-breve-526.py): die Typfrage liegt in #370. GRA wird nie vergeben.

FOLGEN: @lemmaRef kommt neu hinzu, also Korpus-Index, API und Begriffshilfe
neu bauen; variants.xml und der Authority-Index bleiben unberuehrt.

Nicht idempotent: ein zweiter Lauf findet die Tokens annotiert vor und bricht
ab.

Usage:
    python scripts/ingest/wzb/wzb-makron-526.py \
        --out-dir ingest/pos-disambig/526-makron [--apply]
"""
import argparse
import csv
import gzip
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DATEI = REPO / "tei" / "WZB.tei.xml"
AUTH_INDEX = REPO / "data" / "authority-index.json.gz"

TAGS_19 = {"NOM", "NAM", "ADJ", "ADV", "DET", "POS", "PRO", "PRP", "NEG", "NUM",
           "CNJ", "SCNJ", "CCNJ", "IPA", "VRB", "VEX", "VEM", "INJ", "DIG"}

MAKRON = "̄"

# xml:id -> (Lemma, Wortart, Regel, Vergleichsform, Begruendung)
ENTSCHEIDUNGEN = {
    "WZB_10rb_36_1":  ("lemma_7152", "NOM", "E", "flute",
                       "noch der flūte, die Sintflut (vluot)"),
    "WZB_12va_13_5":  ("lemma_30703", "ADV", "E", "dorumbe",
                       "Dorūmbe bewegte sein geczelt, darumbe"),
    "WZB_15rb_28_2":  ("lemma_7293", "ADV", "E", "furbas",
                       "vnd dornach geet fūrbas, vürbaz"),
    "WZB_20va_16_6":  ("lemma_6467", "CCNJ", "E", "vn",
                       "die gruft vn̄ alle sein bŏvme, und"),
    "WZB_95va_8_2":   ("lemma_6467", "CCNJ", "E", "vnd",
                       "vnd̄ vmmelegte den mit reinem golde, und (vnd oder vnde, beide lemma_6467 CCNJ)"),
    "WZB_143vb_10_4": ("lemma_3028", "PRP", "V", "in",
                       "cochte das ī einem topfe, Praeposition vor Dativ"),
}

# xml:id -> Begruendung
NICHT_ANNOTIERT = {
    "WZB_9vb_37_2":  "cap̄ in der lateinischen Kapitelrubrik (X cap̄ GENE), kein mhd. Wort",
    "WZB_12rb_36_1": "cap̄ in der lateinischen Kapitelrubrik (XIII cap̄ GENE), kein mhd. Wort",
}

W_TEMPLATE = r'<w xml:id="{xid}">(?P<form>[^<]*)</w>'

CHANGE_VORLAGE = (
    '<change when="{datum}" who="#editor">#526 Punkt 5: {n} Tokens mit '
    'Makron (U+0304) nachannotiert (lemmaRef und pos), je am Vers und nur, wo '
    'die Vergleichsform (die Form ohne Makron, bei ī das ausgeschriebene in) in '
    'der WZB schon so annotiert ist. {r} Tokens '
    '(cap̄ in der lateinischen Kapitelrubrik) bleiben unannotiert. Kein corresp '
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


def messe_tei(text):
    """Unannotierte Makron-Tokens und die Annotation jeder Form in der WZB."""
    makron = {}
    annot = defaultdict(Counter)
    for m in re.finditer(r'<w xml:id="(?P<id>[^"]+)"(?P<attr>[^>]*)>(?P<form>[^<]*)</w>', text):
        form = m.group("form")
        lemma = re.search(r'lemmaRef="lexicon\.xml#([^"]+)"', m.group("attr"))
        pos = re.search(r'pos="([^"]+)"', m.group("attr"))
        if lemma:
            annot[nfc(form).lower()][(lemma.group(1), pos.group(1) if pos else "")] += 1
        elif MAKRON in unicodedata.normalize("NFD", form):
            makron[m.group("id")] = form
    return makron, annot


def main() -> int:
    # Windows-Konsole (cp1252) kann das Makron nicht ausgeben
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    text = DATEI.read_text(encoding="utf-8", newline="")
    makron, annot = messe_tei(text)

    tafel = set(ENTSCHEIDUNGEN) | set(NICHT_ANNOTIERT)
    if set(ENTSCHEIDUNGEN) & set(NICHT_ANNOTIERT):
        sys.exit("FEHLER: eine xml:id steht in beiden Tafeln.")
    if set(makron) != tafel:
        sys.exit("FEHLER: Tafel und Makron-Tokens im TEI decken sich nicht.\n"
                 "  ohne Entscheidung: %s\n  nicht (mehr) unannotiert im TEI: %s"
                 % (sorted(set(makron) - tafel) or "-", sorted(tafel - set(makron)) or "-"))

    lemma_pos = lade_lemma_pos()
    zeilen = []
    for xid in sorted(tafel):
        form = makron[xid]
        if xid in NICHT_ANNOTIERT:
            zeilen.append({"file": DATEI.name, "xml_id": xid, "form": form,
                           "action": "REVIEW", "neu_lemmaRef": "", "neu_pos": "",
                           "regel": "", "vergleichsform": "", "vergleich_belege": "",
                           "ziel_lemma_form": "", "begruendung": NICHT_ANNOTIERT[xid]})
            continue
        lemma, pos, regel, vergleich, grund = ENTSCHEIDUNGEN[xid]
        posAll, lemmaform = lemma_pos.get(lemma, ([], ""))
        # CCNJ/SCNJ sind die ausdifferenzierten CNJ (POS-TAGSET, K5); das
        # Lexikon fuehrt bei und weiter nur CNJ, die WZB annotiert CCNJ.
        erlaubt = set(posAll) | ({"CCNJ", "SCNJ"} if "CNJ" in posAll else set())
        if pos not in TAGS_19 or pos not in erlaubt:
            sys.exit("FEHLER: %s bekaeme %r, %s fuehrt %s" % (xid, pos, lemma, " ".join(posAll)))
        belege = annot.get(vergleich, Counter())
        treffer = belege.get((lemma, pos), 0)
        if treffer == 0:
            sys.exit("FEHLER: %s: Vergleichsform %r traegt in der WZB nie %s %s (%s)"
                     % (xid, vergleich, lemma, pos, dict(belege)))
        if regel == "E" and treffer != sum(belege.values()):
            sys.exit("FEHLER: %s: Regel E, aber %r ist in der WZB nicht ausnahmslos %s %s (%s)"
                     % (xid, vergleich, lemma, pos, dict(belege)))
        zeilen.append({"file": DATEI.name, "xml_id": xid, "form": form,
                       "action": "ANNOTATE", "neu_lemmaRef": "lexicon.xml#" + lemma,
                       "neu_pos": pos, "regel": regel, "vergleichsform": vergleich,
                       "vergleich_belege": "%d von %d" % (treffer, sum(belege.values())),
                       "ziel_lemma_form": lemmaform, "begruendung": grund})

    geschrieben = 0
    for z in zeilen:
        if z["action"] != "ANNOTATE":
            continue
        m = re.search(W_TEMPLATE.format(xid=re.escape(z["xml_id"])), text)
        if not m:
            sys.exit("FEHLER: <w xml:id=%s> nicht ohne Attribute gefunden." % z["xml_id"])
        neu = ('<w xml:id="%s" lemmaRef="%s" pos="%s">%s</w>'
               % (z["xml_id"], z["neu_lemmaRef"], z["neu_pos"], m.group("form")))
        text = text[:m.start()] + neu + text[m.end():]
        geschrieben += 1

    n_review = sum(1 for z in zeilen if z["action"] == "REVIEW")
    change = CHANGE_VORLAGE.format(datum="2026-10-07", n=geschrieben, r=n_review,
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
    with open(out / "diff-liste.csv", "w", encoding="utf-8-sig", newline="") as fh:
        wr = csv.DictWriter(fh, fieldnames=list(zeilen[0].keys()), delimiter=";")
        wr.writeheader()
        wr.writerows(zeilen)

    modus = "APPLY" if args.apply else "DRY-RUN"
    print("[%s] Makron-Tokens: %d" % (modus, len(zeilen)))
    print("  ANNOTATE: %d, REVIEW: %d" % (geschrieben, n_review))
    print("  Wortarten:", dict(Counter(z["neu_pos"] for z in zeilen if z["action"] == "ANNOTATE")))
    for z in zeilen:
        print("  %-16s %-8s %-8s %-18s %-4s %s" % (z["xml_id"], z["form"], z["action"],
              z["neu_lemmaRef"].replace("lexicon.xml#", ""), z["neu_pos"], z["vergleich_belege"]))
    print("  Artefakte:", out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
