"""apk_common.py: gemeinsame Konstanten der Hesler-Apokalypse (APK, #262).

Gegenstueck zu scripts/ingest/bre/bre_common.py, auf einen Text verkleinert. Die Phasenskripte
10 bis 21 sind aus BRE uebertragen und erwarten dieselbe Schnittstelle (REPO, INGEST_DIR,
HarterFehler, ausgabe_utf8, ZEUGEN).
"""
import hashlib
import io
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
INGEST_DIR = REPO / "ingest" / "apk"
SIGLE = "APK"
AUSGABE = INGEST_DIR / f"{SIGLE}.tei.xml"

# Ein Text, ein "Zeuge": die Phasenskripte fuehren eine Spalte zeuge, hier immer APK.
ZEUGEN = {SIGLE: ("Danziger Handschrift (Helm 1907)", SIGLE)}
SEGMENTIERUNG_OFFEN = set()

# Die Rohdatei liegt gitignoriert unter sources/hesler-apokalypse/ (sources/README.md) und
# darf nicht ins Repository (Kickoff apk-262, #262). Ein Worktree unter .claude/worktrees/
# hat sie nicht, dort wird der Main Worktree mitgesucht.
ROH_REL = Path("sources") / "hesler-apokalypse" / "apk_free.xml"
ROH_BYTES = 1565852
ROH_SHA256 = "6d8ebb253ef1e277ae3a051108af51a5ed73299cc67ec51031099c198e86e7da"


class HarterFehler(Exception):
    pass


def ausgabe_utf8():
    if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
    if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)


def rohdatei(pfad=None):
    """-> (Pfad, Bytes) der Rohdatei, nach Groesse und SHA-256 geprueft (harter Fehler sonst)."""
    kandidaten = [Path(pfad)] if pfad else [REPO / ROH_REL]
    if not pfad and REPO.parent.name == "worktrees" and REPO.parents[1].name == ".claude":
        kandidaten.append(REPO.parents[2] / ROH_REL)
    for k in kandidaten:
        if k.exists():
            daten = k.read_bytes()
            if len(daten) != ROH_BYTES:
                raise HarterFehler(f"{k}: {len(daten)} Bytes, erwartet {ROH_BYTES}")
            sha = hashlib.sha256(daten).hexdigest()
            if sha != ROH_SHA256:
                raise HarterFehler(f"{k}: SHA-256 {sha}, erwartet {ROH_SHA256}")
            return k, daten
    raise HarterFehler("Rohdatei nicht gefunden: " + ", ".join(str(k) for k in kandidaten)
                       + " (Kopie im DHCraft-Drive, sources/INVENTAR-ARCHIV.md)")
