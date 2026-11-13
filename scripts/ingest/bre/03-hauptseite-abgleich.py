#!/usr/bin/env python3
"""03-hauptseite-abgleich.py: gleicht die Werkzuordnung je Zeuge mit der Hauptseite ab (#147).

Massgeblich ist der Abschnitt "Überlieferung" der Hauptseite "Kategorie:Quelle Weingruß"
(gepinnte Revision aus revisionen.tsv); die Synopsen der Einzeltextseiten sind ergaenzend.
Je Zeuge werden die Texte der Transkription (Segmentierung ueber die Synopsen, ohne
Vorspann) mit der Liste der Hauptseite verglichen: Titel, Menge, Reihenfolge. Der Vorspann
(bre_common.VORSPANN) zaehlt nur dort als Text, wo er ein Text eines Zeugen ist
("fragment", "text_ohne_einzelseite" mit Werk laut bre_common.VORSPANN_WERK).

Ausgabe: Tabelle der Abweichungen auf stdout und ingest/bre/hauptseite-abgleich.tsv
(Zeuge, Art, Text, bisher, laut Hauptseite). Exit 0 auch bei Abweichungen: der Abgleich ist
ein Befund. In 02-convert-wiki-to-mhdbdb.py bricht jede nicht erklaerte Abweichung
(bre_common.ABWEICHUNG_ERKLAERT) den Lauf ab.

Aufruf: python -P -E scripts/ingest/bre/03-hauptseite-abgleich.py [--zeuge B] [--ohne-datei]
"""
import argparse
import importlib.util
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bre_common as bc  # noqa: E402
import bre_hauptseite as bh  # noqa: E402

AUSGABE = bc.INGEST_DIR / "hauptseite-abgleich.tsv"


def lade_02():
    pfad = Path(__file__).resolve().parent / "02-convert-wiki-to-mhdbdb.py"
    spec = importlib.util.spec_from_file_location("convert02", pfad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def texte_der_transkription(c02, sigle):
    """-> (Titel der Texte in Reihenfolge der Transkription, Vorspann-Art oder None)."""
    seite = bc.lade_seite(bc.transkriptions_titel(sigle))
    _, items, noten, _ = c02.lies_transkription(seite["inhalt"])
    lex = {i: c02.lexe(it["raw"], noten, f"{seite['titel']} Zeile {it['lines'][0]}")
           for i, it in enumerate(items) if it["kind"] == "verse"}
    texte, _, vorspann = c02.segmentiere(items, lex, c02.lade_segmentierung(sigle), sigle)
    titel = [t["row"]["text_titel"] for t in texte]
    art = vorspann["art"] if vorspann else None
    werk = bc.VORSPANN_WERK.get(sigle)
    if art in ("fragment", "text_ohne_einzelseite") and werk:
        # Der Vorspann ist hier ein Text des Zeugen und steht vor dem ersten Synopsen-Text
        titel = [werk] + titel
    return titel, art


def abgleich_zeuge(c02, haupt, sigle):
    titel, art = texte_der_transkription(c02, sigle)
    return bh.abgleich(sigle, haupt[sigle], titel, art), titel


def main():
    bc.ausgabe_utf8()
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--zeuge", default="alle")
    ap.add_argument("--ohne-datei", action="store_true", help="hauptseite-abgleich.tsv nicht schreiben")
    a = ap.parse_args()
    try:
        seite, haupt = bh.lade_hauptseite()
        c02 = lade_02()
        zeugen = list(bc.ZEUGEN) if a.zeuge == "alle" else [a.zeuge]
        zeilen, n_ok = [], 0
        for s in zeugen:
            abw, titel = abgleich_zeuge(c02, haupt, s)
            for x in abw:
                grund = bc.ABWEICHUNG_ERKLAERT.get((s, x["art"], x["titel"]), "NICHT GEPRUEFT")
                zeilen.append((s, x["art"], x["titel"], x["bisher"], x["hauptseite"], grund))
            n_ok += not abw
            print(f"{s:3s} {len(titel):2d} Texte bisher, {len(haupt[s]):2d} laut Hauptseite: "
                  f"{'gleich' if not abw else str(len(abw)) + ' Abweichung(en)'}")
        print(f"Hauptseite rev {seite['revid']} ({seite['timestamp']}): {n_ok} von {len(zeugen)} "
              f"Zeugen ohne Abweichung")
        if zeilen:
            print("\nzeuge\tart\ttext\tbisher\tlaut Hauptseite\tbefund")
            for z in zeilen:
                print("\t".join(z))
        if not a.ohne_datei and a.zeuge == "alle":
            kopf = "zeuge\tart\ttext\tbisher\thauptseite\tbefund\n"
            AUSGABE.write_text(kopf + "".join("\t".join(z) + "\n" for z in zeilen),
                               encoding="utf-8", newline="\n")
            print(f"geschrieben: {AUSGABE} ({len(zeilen)} Zeilen)")
        return 2 if any(z[5] == "NICHT GEPRUEFT" for z in zeilen) else 0
    except bc.HarterFehler as e:
        print(f"FEHLER: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
