#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#367: die 40 Belege von 'der/die waeren minne' vom Verb aufs Adjektiv umhaengen.

Anders als die Serien 1 und 2 (#216, #369) ist das keine Erstannotation, sondern
eine Umannotation: die 40 Tokens tragen bereits lemmaRef, pos und corresp. Die
generischen Skripte der Serien greifen deshalb nicht, ihr W_TEMPLATE matcht
absichtlich nur unannotierte <w>. Muster hier ist fix-369-skt-fehltag.py:
exakte Zeichenkette rein, exakte Zeichenkette raus.

  lemma_7505 (wesen, VRB)  ->  lemma_7338 (waer, ADJ)

Entschieden von KZW am 2026-08-25 in #367: alle 40 sind dieselbe Fuegung aus
kasusmarkiertem Artikel, flektiertem 'waer' und 'minne'; vor dem Zielwort steht
31 mal 'der', 8 mal 'die', einmal 'diu', kein einziges 'daz'. Die Verblesart
vom Typ 'daz waren brueder' ist damit in keinem der 40 Faelle moeglich.

Variantentypen, und das ist der eine Punkt, den KZW ausdruecklich benannt hat:
fuer 'waeren' (CHH) und 'woren' (FR3) wird je eine NEUE Nummer gepraegt, statt
die bestehende mitwandern zu lassen. Sonst haenge dieselbe Nummer an zwei
Lemmata, und extract-variants.py schlaegt sie der haeufigeren Seite zu, also
weiter dem Verb (Aufloesungsregel im Docstring von extract-variants.py).

@ana wird nicht gesetzt: keines der 40 Tokens traegt heute eines, die Frage
stellt sich also gar nicht (kuratorisch wie in #189, #198, #216, #369).

Nicht idempotent, und das mit Absicht: das Skript verlangt den Korpusstand VOR
dem Batch und prueft je Token, dass die alte Zeichenkette genau einmal dasteht.
Ein Replay auf dem Ergebnis meldet den Ausgangszustand als nicht gefunden.

Usage:
    python scripts/ingest/pos-disambig/fix-367-waeren.py \
        --config ingest/pos-disambig/367-waeren/config.json \
        --faelle ingest/pos-disambig/367-waeren/faelle.csv \
        --out-dir ingest/pos-disambig/367-waeren [--apply]
"""
import argparse
import csv
import json
import sys
import unicodedata
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / "tei"


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def norm(s):
    return unicodedata.normalize("NFC", s or "").strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--faelle", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(pfad(args.config).read_text(encoding="utf-8"))
    ziel_lemma = cfg["ziel_lemma"]
    ziel_pos = cfg["ziel_pos"]
    quell_lemma = cfg["quell_lemma"]
    quell_pos = cfg["quell_pos"]
    corresp_neu = cfg["corresp_neu"]

    with open(pfad(args.faelle), encoding="utf-8-sig", newline="") as fh:
        faelle = list(csv.DictReader(fh, delimiter=";"))
    if not faelle:
        sys.exit("FEHLER: faelle.csv ist leer")

    unentschieden = [f["xml_id"] for f in faelle
                     if f.get("entscheidung", "").strip() != ziel_pos]
    if unentschieden:
        sys.exit("FEHLER: %d Faelle ohne Entscheidung %r: %s"
                 % (len(unentschieden), ziel_pos, ", ".join(unentschieden[:5])))

    je_datei = {}
    for f in faelle:
        je_datei.setdefault(f["file"], []).append(f)

    zeilen = []
    stats = Counter()
    for fname in sorted(je_datei):
        fp = TEI_DIR / fname
        # newline="" beim Lesen UND Schreiben: Zeilenenden bleiben byte-identisch.
        # WZB mischt CRLF und LF, und ein zeilenweiser Rewrite vereinheitlicht
        # das still (gemessen an #315); die uebrigen Dateien sind reines LF.
        text = fp.read_text(encoding="utf-8", newline="")
        geaendert = False
        for f in je_datei[fname]:
            xid = f["xml_id"]
            form = norm(f["form"])
            schluessel = form.lower()
            if schluessel not in corresp_neu:
                sys.exit("FEHLER: %s: kein Zieltyp fuer Schreibung %r "
                         "(config.corresp_neu)" % (xid, form))
            neu_typ = corresp_neu[schluessel]

            alt = ('<w xml:id="%s" lemmaRef="lexicon.xml#%s" pos="%s" '
                   'corresp="%s">%s</w>'
                   % (xid, quell_lemma, quell_pos, f["corresp"], form))
            neu = ('<w xml:id="%s" lemmaRef="lexicon.xml#%s" pos="%s" '
                   'corresp="variants.xml#%s">%s</w>'
                   % (xid, ziel_lemma, ziel_pos, neu_typ, form))

            n = text.count(alt)
            if n != 1:
                sys.exit("FEHLER: %s: Ausgangszustand von %s %s gefunden "
                         "(erwartet genau 1). Korpusstand vor dem Batch "
                         "erwartet.\n  gesucht: %s"
                         % (fname, xid, n, alt))
            text = text.replace(alt, neu, 1)
            geaendert = True
            stats["ANNOTATE"] += 1

            zeilen.append({
                "file": fname, "xml_id": xid, "form": form,
                "vers": f.get("vers_n", ""),
                "action": "ANNOTATE", "review_grund": "",
                "geaendert": "ja",
                "alt_pos": quell_pos, "neu_pos": ziel_pos,
                "alt_lemmaRef": "lexicon.xml#" + quell_lemma,
                "neu_lemmaRef": "lexicon.xml#" + ziel_lemma,
                "alt_corresp": f["corresp"],
                "neu_corresp": "variants.xml#" + neu_typ,
                "typ_neu_gepraegt": "ja" if neu_typ in cfg.get("neue_typen", []) else "nein",
                "verdict_lemma": ziel_lemma, "verdict_pos": ziel_pos,
                "confidence": "high",
                "begruendung": f.get("anmerkung", ""),
                "kontext": " / ".join(x for x in (f.get("vorvers"), f.get("vers"),
                                                  f.get("folgevers")) if x),
            })
        if geaendert and args.apply:
            fp.write_text(text, encoding="utf-8", newline="")
            stats["dateien_geaendert"] += 1

    out = pfad(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    spalten = list(zeilen[0].keys())
    with open(out / "diff-liste.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=spalten, delimiter=";")
        w.writeheader()
        w.writerows(zeilen)

    modus = "APPLY" if args.apply else "DRY-RUN"
    print("[%s] %d Faelle: %s" % (modus, len(zeilen), dict(stats)))
    print("  Dateien:", len(je_datei))
    print("  Schreibungen:", dict(Counter(z["form"] for z in zeilen)))
    print("  Zieltypen:", dict(Counter(z["neu_corresp"] for z in zeilen)))
    print("  davon neu gepraegt:",
          dict(Counter(z["neu_corresp"] for z in zeilen
                       if z["typ_neu_gepraegt"] == "ja")))
    print("  geschrieben:", out / "diff-liste.csv")
    if not args.apply:
        print("  (--apply schreibt ins Korpus)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
