#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#369: den einen Fehltag korrigieren, der der Serie im Weg stand.

`SKT_502140_4` traegt `stât` als Substantiv (`lemma_5732` NOM), obwohl der Vers
'mîn gedanc an ir vil hôhe stât' das Verb verlangt. Der Beleg ist korpusweit der
einzige seines Variantentyps `type_218598`, und weil er die Schreibung `stât`
mit dem Substantiv-Lemma verbindet, konnte die Serie fuer dieses Paar keinen
Bestands-Typ ansetzen: die config.json laesst das Paar deshalb aus und schickt
NOM-Verdicts auf der Zirkumflex-Schreibung in den Review.

Mit der Korrektur verschwindet der Grund dafuer. Die Folge ist beabsichtigt und
zieht den Lifecycle nach: `type_218598` wird unbelegt, `extract-variants.py`
meldet ihn als `removed`, `variants.xml` und der Authority-Index aendern sich.
Ein Variantentyp, den nur ein Fehltag traegt, soll genau das tun.

`@ana` wird ersatzlos entfernt statt umgehaengt: die Sense-Referenz zeigt auf
einen Sinn des Substantivs und ist damit ebenfalls falsch, aber die Zuordnung
eines neuen Sinns ist kuratorisch (gleiche Regel wie in #189, #198, #216).

Idempotent: ein zweiter Lauf findet den Ausgangszustand nicht mehr und meldet
das, statt etwas zu tun.

Usage:
    python scripts/ingest/pos-disambig/fix-369-skt-fehltag.py [--apply]
"""
import argparse
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
DATEI = REPO / "tei" / "SKT.tei.xml"

ALT = ('<w xml:id="SKT_502140_4" lemmaRef="lexicon.xml#lemma_5732" pos="NOM" '
       'ana="lexicon.xml#lemma_5732_sense_8998" '
       'corresp="variants.xml#type_218598">stât</w>')
NEU = ('<w xml:id="SKT_502140_4" lemmaRef="lexicon.xml#lemma_5710" pos="VRB" '
       'corresp="variants.xml#type_20048">stât</w>')


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    text = DATEI.read_text(encoding="utf-8", newline="")
    n_alt, n_neu = text.count(ALT), text.count(NEU)

    if n_neu and not n_alt:
        print("Bereits korrigiert, nichts zu tun.")
        return 0
    if n_alt != 1:
        sys.exit("FEHLER: Ausgangszustand nicht eindeutig gefunden "
                 "(%d Treffer). Korpusstand vor dem Batch erwartet." % n_alt)

    print("SKT_502140_4: lemma_5732/NOM/type_218598 -> lemma_5710/VRB/type_20048")
    print("  @ana (lemma_5732_sense_8998) wird ersatzlos entfernt.")
    if args.apply:
        DATEI.write_text(text.replace(ALT, NEU, 1), encoding="utf-8",
                         newline="")
        print("  geschrieben.")
    else:
        print("  (--apply zum Schreiben)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
