"""Findet im Legacy-Archiv die Plaintext-Dateien, die den alten MHDBDB-Linecode tragen.

    python scripts/ingest/legacy-sources/01-scan-linecode.py <ARCHIV> <SCAN-CSV>

<ARCHIV> ist der lokale Pfad zu `MHDBDB_Inhaltliches/Texte/ERLEDIGT/` (nur bei KZW, siehe
`sources/INVENTAR-ERLEDIGT.md`). Ergebnis ist eine CSV, die 03-build-sources.py weiterverwendet.

Kriterium: mindestens die Haelfte der nichtleeren Zeilen beginnt mit einer Ziffernfolge von 9 bis
25 Stellen, gefolgt von Whitespace. Die tatsaechlich beobachteten Breiten sind 13, 17, 18, 19 und
20; die Untergrenze 9 ist absichtlich weiter gefasst, damit unbekannte Templates nicht durchfallen.
"""
import csv
import re
import sys
from pathlib import Path

CODE = re.compile(r"^\s*(\d{9,25})[ \t]")
ENCODINGS = ["utf-8-sig", "cp1252", "latin-1"]
FIELDS = ["path", "bytes", "encoding", "lines", "coded_lines", "coded_pct",
          "code_widths", "first_line"]


def read_text(p):
    raw = p.read_bytes()
    for enc in ENCODINGS:
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1", "replace"), "latin-1?"


def main(root, out):
    rows = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.suffix.lower() not in {".txt", ".bak"}:
            continue
        text, enc = read_text(p)
        lines = [l for l in text.splitlines() if l.strip()]
        if not lines:
            continue
        coded = [m.group(1) for l in lines if (m := CODE.match(l))]
        rows.append({
            "path": str(p.relative_to(root)).replace("\\", "/"),
            "bytes": p.stat().st_size,
            "encoding": enc,
            "lines": len(lines),
            "coded_lines": len(coded),
            "coded_pct": round(100 * len(coded) / len(lines), 1),
            "code_widths": ",".join(str(w) for w in sorted({len(c) for c in coded})),
            "first_line": lines[0][:90],
        })

    with out.open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: -r["coded_pct"]))

    coded_files = [r for r in rows if r["coded_pct"] >= 50]
    print(f"geprueft:        {len(rows)} Plaintext-Dateien")
    print(f"codiert (>=50%): {len(coded_files)}, "
          f"{sum(r['bytes'] for r in coded_files) / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]))
