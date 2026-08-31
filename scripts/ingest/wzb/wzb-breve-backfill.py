#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#235 Punkt 3: Breve-Backfill in der Wenzelsbibel.

Die WZB schreibt Umlaute mit Breve. Seit #224/PR #227 loesen die Normalizer
o-Breve auf 'oe' und u-Breve auf 'ue' auf (ADR-016), aber die Tokens, an denen
der Matcher beim Ingest wegen des Breve stehengeblieben war, sind nie
nachannotiert worden. Dieses Skript holt das nach.

Der Lauf war bis zum 2026-08-26 blockiert, nicht technisch, sondern editorisch:
ADR-016 hatte offen gelassen, ob das Breve auf 'w' und 'n' ueberhaupt ein
Umlautzeichen ist. Julia Hintersteiner hat als WZB-Editorin geantwortet, es sei
boehmische Schreibkonvention der damaligen Schreibstuben (ADR-017, umgesetzt in
f3dcf2a86). Damit duerfen die o/u-Breve-Kandidaten als EINE Klasse laufen.

Zaehlvorschrift der Kandidaten, wie im Issue-Kommentar vom 31.07.: NFD-
Zerlegung, dann 'o' oder 'u' (auch gross) gefolgt von U+0306, und @lemmaRef
fehlt. Die NFD-Zerlegung ist nicht optional: nur ein Zehntel der Breve liegt
praekomponiert als 'ŏ'/'ŭ' vor, ein grep auf das Einzelzeichen findet den Rest
nicht und wiegt in Sicherheit.

ANNOTIERT wird nur, wo beides mechanisch eindeutig ist:
  - die normalisierte Schreibung trifft in variants.xml genau EIN Lemma
  - dieses Lemma traegt genau EINE Wortart (posAll)
Alles andere bleibt byte-identisch stehen und geht in review-faelle.csv, mit
dem Grund in der Spalte review_grund:
  lemma-mehrdeutig   mehrere Lemmata fuer dieselbe normalisierte Form
  lemma-kein-treffer variants.xml kennt die Form nicht (Lexikonluecke, nicht
                     Breve-Problem: 'ŏpfeltragendes', 'gevŏggeln', 'bŏvme')
  pos-mehrdeutig     das Lemma traegt mehrere Wortarten, die Wahl braucht
                     Kontext und damit eine Disambiguierung wie in #216/#369

Kein @corresp. Das ist eine bewusste Entscheidung und keine Nachlaessigkeit:
fuer jede der Schreibungen muesste unter dem Ziel-Lemma eine NEUE Typnummer
gepraegt werden (gemessen 113 distinkte Paare), und neue Typen zu praegen war in
diesem Projekt bisher immer genehmigungspflichtig (#216 und #369 haben es
ausdruecklich verweigert, #367 hat fuer zwei Nummern KZWs Zustimmung eingeholt).
Die annotierten Tokens landen damit in derselben Lage wie die 52.097 anderen
WZB-Tokens mit @lemmaRef ohne @corresp, die als #370 ein eigenes Ticket haben.

@ana wird ebenfalls nicht gesetzt, die Sense-Zuordnung ist kuratorisch (wie
#189, #198, #216, #369).

Nicht idempotent: ein zweiter Lauf findet die annotierten Tokens nicht mehr als
Kandidaten, meldet also weniger. Ein Replay setzt den Stand vor dem Lauf voraus.

Usage:
    python scripts/ingest/wzb/wzb-breve-backfill.py \
        --out-dir ingest/wzb/235-breve [--apply]
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
sys.path.insert(0, str(REPO / "scripts"))
from mhg_normalizer import normalize_mhg  # noqa: E402
from lxml import etree  # noqa: E402

TEI_NS = "http://www.tei-c.org/ns/1.0"
W_TAG = "{" + TEI_NS + "}w"
L_TAG = "{" + TEI_NS + "}l"
XML_ID = "{http://www.w3.org/XML/1998/namespace}id"

DATEI = REPO / "tei" / "WZB.tei.xml"
VARIANTS = REPO / "authority-files" / "variants.xml"
AUTH_INDEX = REPO / "data" / "authority-index.json.gz"

BREVE = "̆"
BASEN = set("oOuU")

# xml:id zuerst, dann optional pos="...", kein weiteres Attribut. Trifft
# absichtlich nur unannotierte <w> (Muster aus apply-homograph.py).
W_TEMPLATE = r'<w xml:id="{xid}"(?: pos="(?P<oldpos>[A-Z]+)")?>(?P<form>[^<]*)</w>'


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def nfc(s):
    return unicodedata.normalize("NFC", s or "")


def hat_ou_breve(text):
    zerlegt = unicodedata.normalize("NFD", text)
    return any(c == BREVE and i > 0 and zerlegt[i - 1] in BASEN
               for i, c in enumerate(zerlegt))


def lade_form_lemmata():
    """normalisierte Form -> Menge der Lemmata, aus variants.xml."""
    tree = etree.parse(str(VARIANTS))
    treffer = defaultdict(set)
    for entry in tree.iter("{" + TEI_NS + "}entry"):
        ref = entry.get("corresp") or entry.get("lemmaRef") or ""
        lemma = ref.split("#")[-1] if ref else None
        if not lemma:
            continue
        for f in entry.iter("{" + TEI_NS + "}form"):
            if f.text:
                treffer[normalize_mhg(f.text.strip())].add(lemma)
    return treffer


def lade_lemma_pos():
    """lemma_id -> Liste der Wortarten, aus dem Authority-Index."""
    idx = json.load(gzip.open(AUTH_INDEX, "rt", encoding="utf-8"))
    aus = {}
    for l in idx["lemmata"]:
        pa = l.get("posAll") or ([l["pos"]] if l.get("pos") else [])
        aus[l["id"]] = ([p for p in pa if p], l.get("lemma", ""))
    return aus


def vers_text(el, mark_id=None):
    if el is None:
        return ""
    teile = []
    for w in el.iter(W_TAG):
        t = nfc("".join(w.itertext())).strip()
        teile.append("**%s**" % t if w.get(XML_ID) == mark_id else t)
    return " ".join(teile)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    form_lemmata = lade_form_lemmata()
    lemma_pos = lade_lemma_pos()

    tree = etree.parse(str(DATEI))
    alle_l = list(tree.iter(L_TAG))
    l_position = {el: i for i, el in enumerate(alle_l)}
    alle_w = list(tree.iter(W_TAG))
    w_position = {el: i for i, el in enumerate(alle_w)}

    zeilen = []
    stats = Counter()
    for w in tree.iter(W_TAG):
        if w.get("lemmaRef"):
            continue
        form = nfc("".join(w.itertext())).strip()
        if not hat_ou_breve(form):
            continue

        xid = w.get(XML_ID)
        normalisiert = normalize_mhg(form)
        kandidaten = sorted(form_lemmata.get(normalisiert, set()))

        lemma = pos = ""
        if not kandidaten:
            aktion, grund = "REVIEW", "lemma-kein-treffer"
        elif len(kandidaten) > 1:
            aktion, grund = "REVIEW", "lemma-mehrdeutig"
        else:
            lemma = kandidaten[0]
            pos_liste = lemma_pos.get(lemma, ([], ""))[0]
            if len(pos_liste) == 1:
                aktion, grund, pos = "ANNOTATE", "", pos_liste[0]
            else:
                aktion, grund = "REVIEW", "pos-mehrdeutig"
        stats[aktion] += 1
        if grund:
            stats[grund] += 1

        vers = w.getparent()
        while vers is not None and vers.tag != L_TAG:
            vers = vers.getparent()
        vor = nach = None
        if vers is not None and vers in l_position:
            j = l_position[vers]
            vor = alle_l[j - 1] if j > 0 else None
            nach = alle_l[j + 1] if j + 1 < len(alle_l) else None

        # Fenster aus acht Nachbartokens, immer. Die WZB ist ueberwiegend in
        # <l> gegliedert, aber nicht durchgehend: ohne diesen Fallback bliebe
        # das Review-Artefakt an den Stellen ohne Vers leer, und genau dort
        # muesste jemand doch wieder ins TEI schauen (gemessen 2 von 289).
        i_w = w_position[w]
        umfeld = " ".join(
            ("**%s**" % nfc("".join(x.itertext())).strip())
            if x is w else nfc("".join(x.itertext())).strip()
            for x in alle_w[max(0, i_w - 4):i_w + 5])

        zeilen.append({
            # Spalte 'file' ist die Schnittstelle zu revisiondesc-homograph.py:
            # das Skript zaehlt seine Eintraege je Datei daraus. Hier ist es
            # immer dieselbe, die Spalte muss trotzdem dastehen.
            "file": DATEI.name,
            "xml_id": xid,
            "form": form,
            "normalisiert": normalisiert,
            "action": aktion,
            "review_grund": grund,
            "neu_lemmaRef": ("lexicon.xml#" + lemma) if aktion == "ANNOTATE" else "",
            "neu_pos": pos,
            "ziel_lemma_form": lemma_pos.get(lemma, ([], ""))[1] if lemma else "",
            "lemma_kandidaten": " ".join(kandidaten),
            "lemma_pos_alle": " ".join(lemma_pos.get(lemma, ([], ""))[0]) if lemma else "",
            "vers_n": vers.get("n") if vers is not None else "",
            "vorvers": vers_text(vor),
            "vers": vers_text(vers, xid),
            "folgevers": vers_text(nach),
            "umfeld": umfeld,
        })

    if not zeilen:
        sys.exit("FEHLER: keine Kandidaten gefunden, Zaehlvorschrift pruefen.")

    # Schreiben: exakte Textersetzung am unannotierten <w>-Tag, newline=""
    # bei Lesen und Schreiben. WZB mischt 235.973 CRLF- mit 17 reinen
    # LF-Zeilen (die 17 stammen aus dem Token-Split in f3dcf2a86); ein
    # zeilenweiser Rewrite wuerde die still vereinheitlichen.
    text = DATEI.read_text(encoding="utf-8", newline="")
    geschrieben = 0
    for z in zeilen:
        if z["action"] != "ANNOTATE":
            continue
        m = re.search(W_TEMPLATE.format(xid=re.escape(z["xml_id"])), text)
        if not m:
            sys.exit("FEHLER: <w xml:id=%s> nicht unannotiert gefunden"
                     % z["xml_id"])
        if nfc(m.group("form")).strip() != z["form"]:
            sys.exit("FEHLER: %s: Tokentext %r != erwartete Form %r"
                     % (z["xml_id"], m.group("form"), z["form"]))
        if m.group("oldpos"):
            sys.exit("FEHLER: %s traegt bereits pos=%r, das war nicht erwartet"
                     % (z["xml_id"], m.group("oldpos")))
        neu = ('<w xml:id="%s" lemmaRef="%s" pos="%s">%s</w>'
               % (z["xml_id"], z["neu_lemmaRef"], z["neu_pos"], m.group("form")))
        text = text[:m.start()] + neu + text[m.end():]
        geschrieben += 1

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
    print("[%s] Kandidaten: %d" % (modus, len(zeilen)))
    print("  ANNOTATE: %d, REVIEW: %d" % (stats["ANNOTATE"], stats["REVIEW"]))
    print("  Review-Gruende:", {k: v for k, v in stats.items()
                                if k not in ("ANNOTATE", "REVIEW")})
    print("  Wortarten der Annotationen:",
          dict(Counter(z["neu_pos"] for z in zeilen if z["action"] == "ANNOTATE")))
    print("  Ersetzungen im Text: %d" % geschrieben)
    print("  Artefakte:", out)
    if not args.apply:
        print("  (--apply schreibt ins Korpus)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
