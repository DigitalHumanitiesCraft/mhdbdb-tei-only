#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""revisionDesc-Change-Eintrag je geaenderter Korpusdatei (POS-TAGSET §6.3.5).

Verallgemeinerung von revisiondesc-216-minne.py (Serie 1). Was dort als
Konstante im Code stand (Datum, Markertext, Wortlaut des Eintrags), kommt hier
aus dem Block "revisiondesc" der config.json der Serie.

Der Wortlaut selbst ist seit #367 ueberschreibbar: setzt der Block einen
Schluessel "vorlage", wird der statt VORLAGE genommen. Die Voreinstellung
beschreibt eine Erstannotation aus einem LLM-Batch, und das ist keine Formalie,
sondern eine Aussage, die in 300 Korpus-Headern stehenbleibt. Eine Serie, die
etwas anderes tut, sagt etwas anderes.

Getragen wird je Datei genau ein <change> mit den Zahlen DIESER Datei
(annotiert / zurueckgehalten). Muster: der #189-Eintrag in GWTK.tei.xml.

Textuelle Ersetzung statt lxml-Serialisierung, damit der Rest der Datei
byte-identisch bleibt (lxml wuerde Zeilenenden und Attributreihenfolge im
ganzen Dokument neu schreiben). Eingefuegt wird vor dem schliessenden
</revisionDesc>, mit der Einrueckung des letzten vorhandenen <change>.

Idempotent: ein frueher geschriebener eigener Eintrag wird ersetzt, nicht
ergaenzt. Erkannt wird er am Titel aus der config, nicht an der Ticketnummer
allein: eine Datei kann Eintraege mehrerer Serien tragen.

Usage:
    python scripts/ingest/pos-disambig/revisiondesc-homograph.py \
        --config ingest/pos-disambig/369-stat/config.json \
        --diff-liste ingest/pos-disambig/369-stat/diff-liste.csv [--apply]
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / "tei"

# Voreinstellung fuer eine Erstannotation aus einem LLM-Batch (Serien #216,
# #369). Eine Serie, auf die das nicht zutrifft, setzt "vorlage" im
# revisiondesc-Block ihrer config.json: #367 etwa ist eine Umannotation bereits
# annotierter Tokens auf eine Einzelentscheidung von KZW hin, und "LLM-Batch"
# waere dort eine falsche Angabe im Korpus selbst. Platzhalter sind dieselben.
VORLAGE = (
    '<change when="{datum}" who="#editor">{titel}: {n_annot} '
    "homographie-ambige Tokens der Form {form} kontext-disambiguiert und neu "
    "annotiert (lemmaRef/pos/corresp zu {ziele}; LLM-Batch nach POS-TAGSET "
    "§6.3; Provenienz-Log: {log}).{review_satz}</change>"
)
REVIEW_SATZ = (" {n_review} weitere Tokens der Form {form} blieben bewusst "
               "unannotiert (Review).")

CLOSE_RE = re.compile(r"([ \t]*)</revisionDesc>")
LAST_CHANGE_RE = re.compile(r"([ \t]*)<change[ >]")


def pfad(p):
    p = Path(p)
    return p if p.is_absolute() else REPO / p


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--diff-liste", required=True)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    cfg = json.loads(pfad(args.config).read_text(encoding="utf-8"))
    rd = cfg.get("revisiondesc")
    if not rd:
        sys.exit("FEHLER: config.json hat keinen Block 'revisiondesc'")
    fehlt = [k for k in ("datum", "titel", "form", "ziele", "log")
             if k not in rd]
    if fehlt:
        sys.exit("FEHLER: revisiondesc fehlt: %s" % ", ".join(fehlt))

    vorlage = rd.get("vorlage", VORLAGE)
    # Eine eigene Vorlage muss dieselben Platzhalter tragen, sonst schlaegt
    # format() erst mitten im Lauf fehl, wenn schon Dateien geschrieben sind.
    for platzhalter in ("{datum}", "{titel}", "{n_annot}", "{log}"):
        if platzhalter not in vorlage:
            sys.exit("FEHLER: revisiondesc.vorlage ohne Platzhalter %s"
                     % platzhalter)

    # \r?\n, nicht \n: seit die Einfuegung unten das Zeilenende der Umgebung
    # nimmt, terminiert der eigene Eintrag in der CRLF-Datei WZB mit \r\n. Eine
    # Regex auf \n faende ihn nie, der Kopf-Check darueber schon, und ein
    # zweiter --apply-Lauf haenge einen zweiten Eintrag an statt zu ersetzen
    # (gemessen 2026-08-31: subn 0 gegen WZB, 1 gegen die LF-Datei ABG).
    eigene_zeile_re = re.compile(
        r"[ \t]*<change [^>]*>" + re.escape(rd["titel"]) + r":.*?</change>\r?\n")

    annot = Counter()
    review = Counter()
    with open(pfad(args.diff_liste), encoding="utf-8-sig", newline="") as f:
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

        if rd["titel"] in text.split("</teiHeader>", 1)[0]:
            text, n_weg = eigene_zeile_re.subn("", text, count=1)
            stat["ersetzt"] += n_weg

        kopf = text.split("</teiHeader>", 1)[0]
        if "</revisionDesc>" not in kopf:
            sys.exit("FEHLER: %s: kein <revisionDesc> im teiHeader" % fname)

        m_close = None
        for m_close in CLOSE_RE.finditer(text[:len(kopf)]):
            pass
        if m_close is None:
            sys.exit("FEHLER: %s: </revisionDesc> nicht gefunden" % fname)

        einrueckung = None
        for m in LAST_CHANGE_RE.finditer(text[:m_close.start()]):
            einrueckung = m.group(1)
        if einrueckung is None:
            einrueckung = m_close.group(1) + "  "

        n_rev = review.get(fname, 0)
        # {n_wort} traegt den Numerus, damit ein Eintrag ueber genau ein Token
        # nicht "1 Tokens" sagt. Die Voreinstellung nutzt den Platzhalter nicht
        # (str.format ignoriert ueberzaehlige Argumente), eigene Vorlagen koennen.
        eintrag = vorlage.format(
            datum=rd["datum"], titel=rd["titel"], form=rd["form"],
            ziele=rd["ziele"], log=rd["log"], n_annot=annot[fname],
            n_wort="Token" if annot[fname] == 1 else "Tokens",
            review_satz=(REVIEW_SATZ.format(n_review=n_rev, form=rd["form"])
                         if n_rev else ""))
        # Zeilenende der Einfuegung aus der Umgebung nehmen, nicht "\n" setzen:
        # WZB.tei.xml ist eine CRLF-Datei, eine hart gesetzte LF-Zeile mischt
        # sich still hinein (gemessen 2026-08-31: 17 -> 18 reine LF-Zeilen).
        # Bei den reinen LF-Dateien aendert das nichts.
        zeilenende = "\r\n" if text[:m_close.start()].rstrip(" \t").endswith("\r\n") else "\n"
        neu = (text[:m_close.start()] + einrueckung + eintrag + zeilenende
               + text[m_close.start():])
        stat["ergaenzt"] += 1
        if args.apply:
            fp.write_text(neu, encoding="utf-8", newline="")

    modus = "APPLY" if args.apply else "DRY-RUN"
    print("[%s] Dateien mit Annotationen: %d | %s"
          % (modus, len(dateien), dict(stat)))
    if not args.apply:
        print("(--apply zum Schreiben)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
