"""Prueft Word- und RTF-Dateien im Legacy-Archiv auf eingebettete Linecodes.

    python scripts/ingest/legacy-sources/02-scan-binaries.py <ARCHIV>

Diagnose, kein Schreibzugriff. Beantwortet die Frage: gibt es Korpustexte, deren codierte Fassung
nur im Word-Binaerformat existiert? Ergebnis steht in `sources/INVENTAR-ERLEDIGT.md`.

Gezaehlt werden Ziffernfolgen im Rohbytestrom, die wie ein Linecode aussehen (mindestens vier
fuehrende Nullen). Aussagekraeftig ist die Dichte, nicht die absolute Zahl: Seitenzahlen und
RTF-Steuerwerte erzeugen einen Grundrauschen-Pegel um 0,5 Treffer je KB, echte codierte Dateien
liegen bei 4 bis 13.
"""
import sys
from pathlib import Path

import re

CODE = re.compile(rb"(?<![0-9])0{4,}[0-9]{5,15}(?![0-9])")
EXTS = {".rtf", ".doc", ".docx", ".dot", ".wbk", ".xml", ".htm", ".part"}
MIN_HITS = 20


def main(root):
    print(f"{'Treffer':>8} {'MB':>6} {'/KB':>5}  Pfad")
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue
        size = p.stat().st_size
        hits = len(CODE.findall(p.read_bytes()))
        if hits < MIN_HITS:
            continue
        print(f"{hits:8} {size / 1024 / 1024:6.2f} {hits / (size / 1024):5.1f}  "
              f"{str(p.relative_to(root))}")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
