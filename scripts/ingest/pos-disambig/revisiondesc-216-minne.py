#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#216: revisionDesc-Change-Eintrag je geaenderter Korpusdatei (POS-TAGSET §6.3.5).

Traegt in jede vom Batch beruehrte Datei genau einen <change>-Eintrag ein, mit
den Zahlen DIESER Datei (annotiert / zurueckgehalten). Muster: der #189-Eintrag
in GWTK.tei.xml.

Textuelle Ersetzung statt lxml-Serialisierung, damit der Rest der Datei
byte-identisch bleibt (lxml wuerde Zeilenenden und Attributreihenfolge im
ganzen Dokument neu schreiben). Eingefuegt wird vor dem schliessenden
</revisionDesc>, mit der Einrueckung des letzten vorhandenen <change>.

Idempotent: eine Datei, die den Marker '#216' in ihrem revisionDesc bereits
traegt, wird uebersprungen.

Usage:
    python scripts/ingest/pos-disambig/revisiondesc-216-minne.py \
        --diff-liste ingest/pos-disambig/216-minne/diff-liste.csv [--apply]
"""
import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / "tei"

DATUM = "2026-08-24"
MARKER = "#216"

VORLAGE = (
    '<change when="{datum}" who="#editor">#216 Serie 1 (minne): {n_annot} '
    "homographie-ambige Tokens der Form minne kontext-disambiguiert und neu "
    "annotiert (lemmaRef/pos/corresp zu minne NOM bzw. minnen VRB; LLM-Batch "
    "nach POS-TAGSET §6.3; Provenienz-Log: ingest/pos-disambig/216-minne/)."
    "{review_satz}</change>"
)
REVIEW_SATZ = (" {n_review} weitere Tokens der Form minne blieben bewusst "
               "unannotiert (Review).")

CLOSE_RE = re.compile(r"([ \t]*)</revisionDesc>")
LAST_CHANGE_RE = re.compile(r"([ \t]*)<change[ >]")
EIGENE_ZEILE_RE = re.compile(r"[ \t]*<change [^>]*>#216 Serie 1 \(minne\).*?</change>\n")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--diff-liste", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    annot = Counter()
    review = Counter()
    with open(REPO / args.diff_liste, encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f, delimiter=";"):
            if r["action"] == "ANNOTATE":
                annot[r["file"]] += 1
            else:
                review[r["file"]] += 1

    # Nur Dateien, die tatsaechlich Annotationen bekommen haben.
    dateien = sorted(f for f in annot if annot[f] > 0)
    stat = Counter()
    for fname in dateien:
        fp = TEI_DIR / fname
        text = fp.read_text(encoding="utf-8", newline="")

        # Ein frueher geschriebener eigener Eintrag wird ersetzt, nicht
        # ergaenzt: das Skript darf zweimal laufen, ohne zwei Zeilen zu hinter-
        # lassen. Fremde <change>-Eintraege bleiben unberuehrt.
        if MARKER in text.split("</teiHeader>", 1)[0]:
            text, n_weg = EIGENE_ZEILE_RE.subn("", text, count=1)
            stat["ersetzt"] += n_weg

        kopf = text.split("</teiHeader>", 1)[0]
        if "</revisionDesc>" not in kopf:
            sys.exit(f"FEHLER: {fname}: kein <revisionDesc> im teiHeader")

        m_close = None
        for m_close in CLOSE_RE.finditer(text[:len(kopf)]):
            pass
        if m_close is None:
            sys.exit(f"FEHLER: {fname}: </revisionDesc> nicht gefunden")

        einrueckung = None
        for m in LAST_CHANGE_RE.finditer(text[:m_close.start()]):
            einrueckung = m.group(1)
        if einrueckung is None:
            einrueckung = m_close.group(1) + "  "

        n_rev = review.get(fname, 0)
        eintrag = VORLAGE.format(
            datum=DATUM, n_annot=annot[fname],
            review_satz=REVIEW_SATZ.format(n_review=n_rev) if n_rev else "")
        neu = (text[:m_close.start()] + einrueckung + eintrag + "\n"
               + text[m_close.start():])
        stat["ergaenzt"] += 1
        if args.apply:
            fp.write_text(neu, encoding="utf-8", newline="")

    modus = "APPLY" if args.apply else "DRY-RUN"
    print(f"[{modus}] Dateien mit Annotationen: {len(dateien)} | {dict(stat)}")
    if not args.apply:
        print("(--apply zum Schreiben)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
