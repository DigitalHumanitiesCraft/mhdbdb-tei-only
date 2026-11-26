#!/usr/bin/env python3
"""Druckfahnen-Gate der Weingruesse (BRE, #147, #743), ohne die BRE-Suite.

Aufruf: python -P -E scripts/ingest/bre/druckfahnen-gate.py [--zaehlen]

Prueft, dass kein Wortlaut der Hirzel-Druckfassung (Druckfahnen-PDF, Steckbriefe) im Repo steht:
alle Dateien unter ingest/bre und scripts/ingest/bre, Commit Message und hinzugefuegte Zeilen
jedes Commits seit origin/main, dazu die Dateien aus BRE_DRUCK_PRUEFE=<datei>[;<datei>] (PR-Body,
Issue-Kommentar vor dem Absenden). Quellen und Scope: druck_quelle.py, Kern: scripts/audit/wortlaut_gate.py.
Ort der Quellen: BRE_DRUCK_QUELLEN=<ordner> (siehe druck_quelle.py).

Exit 0 kein Wortlaut, 1 Treffer, 2 Pruefung nicht moeglich.
--zaehlen gibt nur Zahlen aus (druck=, erlaubt=, verboten=) und kein Wort der Quellen.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import druck_quelle as dq  # noqa: E402
from wortlaut_gate import NichtMoeglich  # noqa: E402


def main(argv):
    try:
        if "--zaehlen" in argv:
            druck, erlaubt, verboten = dq.zaehlen()
            print(f"druck={druck} erlaubt={erlaubt} verboten={verboten}")
            return 0
        dateien, commits, weitere, treffer = dq.pruefung()
    except NichtMoeglich as e:
        print(f"Pruefung nicht moeglich: {e}")
        return 2
    zaehlung = (f"{dateien} Dateien, {commits} Commit-Texte, {weitere} weitere Texte, "
                f"{dq.N}-Wort-Folgen")
    if treffer:
        print(f"FAIL Druckfahnen: Wortlaut im Repo ({zaehlung}), {len(treffer)} Treffer")
        for name, folge in treffer[:10]:
            print(f"  {name}: {folge}")
        return 1
    print(f"ok   Druckfahnen: kein Wortlaut ({zaehlung})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
