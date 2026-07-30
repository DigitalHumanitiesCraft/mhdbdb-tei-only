"""Erzeugt das dateiweise Verzeichnis des Legacy-Archivs (`sources/archiv-inventar.csv`).

    python scripts/ingest/legacy-sources/04-inventory.py <ARCHIV> <REPO>

Liest nur Metadaten, keine Dateiinhalte. Aufgenommen wird alles ausser den FineReader-
Projektdateien: die sind zu 14.771 Stueck und 7.446 MB die Masse des Archivs (82 %), enthalten
aber keinen extrahierbaren Text und werden deshalb nur aggregiert gezaehlt.

Ausgabe auf stdout ist die Ordner- und Kategorientabelle fuer `sources/INVENTAR-ARCHIV.md`.
"""
import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ARTIFACT_EXT = {".frdat", ".aux", ".dat", ".opt", ".lock", ".hdr", ".frf", ".pac",
                ".ico", ".archive", ".ptn", ".loc", ".ini", ".amd", ".thmx"}
SCAN_EXT = {".tif", ".jpg", ".bmp", ".png"}


def category(ext):
    if ext in ARTIFACT_EXT:
        return "ocr-artefakt"
    if ext in SCAN_EXT:
        return "scan"
    if ext == ".pdf":
        return "pdf"
    if ext == ".zip":
        return "archiv"
    return "text"


def main(root, repo):
    rows = []
    per_folder = defaultdict(lambda: {"n": 0, "b": 0, "ext": Counter()})
    cat_n, cat_b = Counter(), Counter()

    for p in root.rglob("*"):
        if not p.is_file():
            continue
        rel = p.relative_to(root)
        ext = p.suffix.lower()
        cat = category(ext)
        size = p.stat().st_size
        cat_n[cat] += 1
        cat_b[cat] += size

        top = rel.parts[0] if len(rel.parts) > 1 else "(root)"
        f = per_folder[top]
        f["n"] += 1
        f["b"] += size
        f["ext"][ext or "(kein)"] += 1

        if cat == "ocr-artefakt":
            continue
        folder = str(rel.parent).replace("\\", "/")
        rows.append({
            "folder": "(root)" if folder == "." else folder,
            "file": p.name,
            "ext": ext,
            "kategorie": cat,
            "bytes": size,
            "geaendert": datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
                                 .date().isoformat(),
        })

    if not rows:
        raise SystemExit(f"Keine Dateien unter {root}. Archivpfad richtig getippt?")
    rows.sort(key=lambda r: (r["folder"].lower(), r["file"].lower()))
    out = repo / "sources" / "archiv-inventar.csv"
    with out.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    print(f"{out.name}: {len(rows)} Zeilen")
    print(f"Archiv gesamt: {sum(cat_n.values())} Dateien, "
          f"{sum(cat_b.values()) / 1024 / 1024 / 1024:.1f} GB\n")

    print("| Kategorie | Dateien | Groesse |")
    print("|---|---|---|")
    for c, n in cat_n.most_common():
        print(f"| {c} | {n} | {cat_b[c] / 1024 / 1024:.0f} MB |")

    print("\n| Ordner | Dateien | Groesse | Zusammensetzung |")
    print("|---|---|---|---|")
    for top, f in sorted(per_folder.items(), key=lambda kv: -kv[1]["b"]):
        ext = " ".join(f"{e}:{n}" for e, n in f["ext"].most_common(5))
        print(f"| `{top}` | {f['n']} | {f['b'] / 1024 / 1024:.0f} MB | {ext} |")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
