"""01-fetch-and-build-index.py

Holt Linda Beutel-Thurows kuratierte Naming-analysis-Daten von GitHub und
baut daraus den vorgebauten Index `data/naming-index.json.gz` für das
Playground-Modul "Erweiterte Figurenbezeichnungen" (Issue #59).

Quelle: https://github.com/lindabeutel/Naming-analysis (CC BY-NC-SA 4.0)
  - data/<Buch>/categorization_<Buch>.json   (primäre Datenquelle, 4 Werke;
    Linda 2026-03-04: buchspezifische Dateien verwenden, NICHT die globale
    lemma_categories.json — Kategorien sind kontextabhängig)
  - data/lemma_normalization.json            (kanonischer Name → Varianten;
    Alias-Quelle für die Eigenname-Klassifikation)

Datenmodell der categorization-Records (Excel-Erbe, pandas-Export):
  - Genau eines von drei Feld-Mustern trägt die Nennphrase:
      "Erzähler" befüllt                          → Erzähler nennt
      "Bezeichnung" + "Nennende Figur" befüllt    → Figurenrede
      "Eigennennung" befüllt                      → Selbstnennung
  - "Bezeichnung 1-4": Einzellemmata der Nennung. Eigenname, wenn das Lemma
    den Figurennamen trifft (case-insensitiv exakt oder Alias aus
    lemma_normalization.json — repliziert Lindas match_name_to_lemma aus
    naming_analysis/shared.py), sonst Antonomasie.
  - "Epitheta 1-5": bereits als Epitheta kategorisiert (Linda 2026-03-05).
  - "Vers": Float; Dezimalstellen sind echte Editions-Verszählungen (z.B.
    17.02 im Eneasroman). Die Zählung folgt Lindas Editionsgrundlagen und
    weicht teils von der MHDBDB-TEI-Zählung ab (nur ROL weitgehend
    deckungsgleich) — deshalb baut das Modul KEINE Reader-Deep-Links.

Bekannte Quirks, die dieses Skript bereinigt:
  - Literale NaN-Tokens im JSON (pandas) — JS JSON.parse würde scheitern.
  - NBSP (\\xa0) statt Leerzeichen in den Rolandslied-Werten (~1.029 Werte).
  - Figurennamen mit Unterstrichen im Rolandslied ("Gott_(christlich)").

Verwendung:
    python scripts/ingest/naming/01-fetch-and-build-index.py
        [--ref master] [--source-dir <lokale Kopie statt GitHub-Fetch>]

Kein Versions-Kanal in corpus-loader.js: das Modul lädt den Index lazy per
fetch+pako ohne IndexedDB-Cache (klein genug), daher gibt es hier keinen
Cache-Invalidierungs-Bump wie bei corpus-/authority-index (#94).
"""

import argparse
import gzip
import json
import math
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_FILE = PROJECT_ROOT / "data" / "naming-index.json.gz"

REPO = "lindabeutel/Naming-analysis"
RAW_BASE = "https://raw.githubusercontent.com/" + REPO

# Lindas Buchnamen → MHDBDB-Sigles (Cross-Reference verifiziert in #59,
# Kommentar 2026-05-16: alle 4 existieren im Korpus)
BOOKS = {
    "Iwein": "IW",
    "Eneasroman": "ENE",
    "Rolandslied": "ROL",
    "Trojanerkrieg": "TRO",
}

BEZEICHNUNG_COLS = ["Bezeichnung 1", "Bezeichnung 2", "Bezeichnung 3", "Bezeichnung 4"]
EPITHETA_COLS = ["Epitheta 1", "Epitheta 2", "Epitheta 3", "Epitheta 4", "Epitheta 5"]

SOURCE_META = {
    "repo": "https://github.com/" + REPO,
    "doi": "10.5281/zenodo.18770138",
    "citation": "Beutel-Thurow, L. (2026). Naming-analysis (v0.1.0-beta).",
    "license": "CC BY-NC-SA 4.0",
}


def filled(value):
    """True wenn das Feld inhaltlich befüllt ist (NaN/None/'' zählen nicht)."""
    if value is None:
        return False
    if isinstance(value, float) and math.isnan(value):
        return False
    return str(value).strip() != ""


def clean(value):
    """NBSP → Leerzeichen, Whitespace kollabieren, strip."""
    s = str(value).replace("\xa0", " ")
    return " ".join(s.split())


def clean_figure_name(raw):
    """Anzeigename: Rolandslied-Unterstriche zu Leerzeichen."""
    return clean(raw).replace("_", " ")


def serialize_verse(value):
    """Float-Vers kompakt: 803.0 → '803', 17.02 → '17.02'."""
    if isinstance(value, float):
        if value.is_integer():
            return str(int(value))
        return repr(value)
    return clean(value)


def matches_figure_name(figure_name, lemma, aliases):
    """Lindas match_name_to_lemma (shared.py): case-insensitiv exakt oder Alias."""
    norm_lemma = lemma.lower().strip()
    if norm_lemma == figure_name.lower().strip():
        return True
    return norm_lemma in aliases


def fetch(path, ref, source_dir):
    if source_dir:
        return (source_dir / path).read_text(encoding="utf-8")
    url = f"{RAW_BASE}/{ref}/{path}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def resolve_commit_sha(ref):
    """Provenienz: aufgelöste Commit-SHA des Refs (best effort)."""
    url = f"https://api.github.com/repos/{REPO}/commits/{ref}"
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/vnd.github.sha"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.read().decode("ascii").strip()
    except Exception as exc:  # noqa: BLE001 — Provenienz ist optional
        print(f"   (Commit-SHA nicht auflösbar: {exc})")
        return None


def build_record(row, figure_name, aliases):
    """Ein categorization-Record → kompakter Index-Record (oder None)."""
    if filled(row.get("Bezeichnung")) and filled(row.get("Nennende Figur")):
        who, by = "fig", clean(row["Nennende Figur"])
        phrase = clean(row["Bezeichnung"])
    elif filled(row.get("Erzähler")):
        who, by = "erz", None
        phrase = clean(row["Erzähler"])
    elif filled(row.get("Eigennennung")):
        who, by = "self", None
        phrase = clean(row["Eigennennung"])
    elif filled(row.get("Bezeichnung")):
        # Figurenrede ohne erfasste nennende Figur (3x im Iwein)
        who, by = "fig", None
        phrase = clean(row["Bezeichnung"])
    else:
        return None

    eig, ant = [], []
    for col in BEZEICHNUNG_COLS:
        val = row.get(col)
        if not filled(val):
            continue
        lemma = clean(val)
        (eig if matches_figure_name(figure_name, lemma, aliases) else ant).append(lemma)

    epi = [clean(row[col]) for col in EPITHETA_COLS if filled(row.get(col))]

    record = {"v": serialize_verse(row.get("Vers")), "ph": phrase, "who": who}
    if by:
        record["by"] = by
    if eig:
        record["eig"] = eig
    if ant:
        record["ant"] = ant
    if epi:
        record["epi"] = epi
    return record


def build_index(ref, source_dir):
    normalization = json.loads(fetch("data/lemma_normalization.json", ref, source_dir))
    # Alias-Lookup: kanonischer Name (lowercase) → Set lowercased Varianten
    alias_map = {
        clean_figure_name(k).lower(): {clean(v).lower() for v in variants}
        for k, variants in normalization.items()
    }

    works = []
    totals = {"records": 0, "eig": 0, "ant": 0, "epi": 0}

    for book_name, sigle in BOOKS.items():
        raw = json.loads(fetch(f"data/{book_name}/categorization_{book_name}.json", ref, source_dir))
        figures = {}
        skipped = 0
        for row in raw:
            if not filled(row.get("Benannte Figur")):
                skipped += 1
                continue
            figure_name = clean_figure_name(row["Benannte Figur"])
            aliases = alias_map.get(figure_name.lower(), set())
            record = build_record(row, figure_name, aliases)
            if record is None:
                skipped += 1
                continue
            figures.setdefault(figure_name, []).append(record)
            totals["records"] += 1
            for cat in ("eig", "ant", "epi"):
                totals[cat] += len(record.get(cat, []))

        works.append({
            "sigle": sigle,
            "bookName": book_name,
            "figures": {name: figures[name] for name in sorted(figures, key=str.lower)},
        })
        print(f"   {sigle:4s} ({book_name}): {sum(len(v) for v in figures.values())} Records, "
              f"{len(figures)} Figuren, {skipped} übersprungen")

    return works, totals


def main():
    parser = argparse.ArgumentParser(
        description="Naming-analysis-Daten fetchen und data/naming-index.json.gz bauen (#59)")
    parser.add_argument("--ref", default="master",
                        help="Git-Ref im Quell-Repo (Default: master)")
    parser.add_argument("--source-dir", type=Path, default=None,
                        help="Lokale Repo-Kopie statt GitHub-Fetch (offline/reproduzierbar)")
    args = parser.parse_args()

    print("=" * 60)
    print("MHDBDB Naming Index Builder (#59)")
    print("=" * 60)
    src = args.source_dir or f"GitHub {REPO}@{args.ref}"
    print(f"\nQuelle: {src}")

    commit = None
    if not args.source_dir:
        commit = resolve_commit_sha(args.ref)
        if commit:
            print(f"   Commit: {commit}")

    print("\nBaue Index...")
    works, totals = build_index(args.ref, args.source_dir)

    index = {
        "version": "1.0.0",
        "generatedAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source": {**SOURCE_META, "ref": args.ref, **({"commit": commit} if commit else {})},
        "works": works,
    }

    print(f"\nGesamt: {totals['records']} Records | "
          f"Eigennamen-Lemmata: {totals['eig']} | "
          f"Antonomasien-Lemmata: {totals['ant']} | "
          f"Epitheta: {totals['epi']}")

    json_data = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
    uncompressed = len(json_data.encode("utf-8"))
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    with gzip.open(OUTPUT_FILE, "wt", encoding="utf-8") as f:
        f.write(json_data)
    compressed = OUTPUT_FILE.stat().st_size

    print(f"\nGespeichert: {OUTPUT_FILE}")
    print(f"   Unkomprimiert: {uncompressed / 1024:.0f} KB")
    print(f"   Komprimiert:   {compressed / 1024:.0f} KB")


if __name__ == "__main__":
    main()
