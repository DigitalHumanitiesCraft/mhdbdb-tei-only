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

Dazu kommt eine werkspezifische Alias-Ergänzung auf unserer Seite:
  - scripts/ingest/naming/alias-overrides.json

lemma_normalization.json normalisiert werkübergreifend. Ein Alias, der nur in
einem Werk gilt, wäre dort semantisch falsch, deshalb liegt er hier statt in
Lindas Repo (Linda, #59-Kommentar 2026-07-28: „passt sehr gut"). Bisher genau
ein Eintrag: „Alexander" als Deckname des Paris im Trojanerkrieg.

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
        [--require-commit]   # CI: hart failen statt Build-Zeit-Fallback (#152)

Kein Versions-Kanal in corpus-loader.js: das Modul lädt den Index lazy per
fetch+pako ohne IndexedDB-Cache (klein genug), daher gibt es hier keinen
Cache-Invalidierungs-Bump wie bei corpus-/authority-index (#94).

Der Build ist deterministisch (generatedAt = Committer-Datum des Quell-
Commits, gzip ohne mtime): gleicher Quellstand → byte-identischer Output.
Darauf baut der wöchentliche Auto-Update-Workflow
.github/workflows/naming-index-update.yml (rebuild → git diff → PR).
"""

import argparse
import gzip
import json
import math
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_FILE = PROJECT_ROOT / "data" / "naming-index.json.gz"
OVERRIDES_FILE = Path(__file__).resolve().parent / "alias-overrides.json"

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


def load_overrides():
    """alias-overrides.json → {buch: {figur_lowercase: {alias, ...}}}.

    Schluessel unterhalb von "_readme" sind Buchnamen wie in BOOKS. Ein
    unbekannter Buch- oder Figurenname wuerde stumm wirkungslos bleiben,
    deshalb prueft build_index beide gegen die Daten.
    """
    raw = json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    return {
        book: {name.lower(): {a.lower() for a in entry["aliases"]}
               for name, entry in figures.items()}
        for book, figures in raw.items() if not book.startswith("_")
    }


def fetch(path, ref, source_dir):
    if source_dir:
        return (source_dir / path).read_text(encoding="utf-8")
    url = f"{RAW_BASE}/{ref}/{path}"
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode("utf-8")


def resolve_commit(ref, require=False):
    """Provenienz: Commit-SHA + Committer-Datum des Refs.

    Ohne require=True best effort (interaktiv/lokal). Mit require=True
    (CI, #152) harter Fehler: ein stiller Fallback auf Build-Zeit machte
    den Build nicht-deterministisch und verlor die Provenienz (leerer PR
    ohne source.commit).

    Nutzt GITHUB_TOKEN aus der Umgebung, wenn gesetzt: unauthentifizierte
    api.github.com-Calls von GitHub-Runnern teilen sich das IP-Rate-Limit
    und schlagen sporadisch mit 403 fehl — genau die Flakiness, die das
    harte Gate nicht haben darf.
    """
    url = f"https://api.github.com/repos/{REPO}/commits/{ref}"
    try:
        headers = {"Accept": "application/vnd.github+json"}
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return {"sha": data["sha"], "date": data["commit"]["committer"]["date"]}
    except Exception as exc:  # noqa: BLE001 — Provenienz optional, ausser require
        if require:
            sys.exit(f"FEHLER (--require-commit): Commit für Ref '{ref}' nicht "
                     f"auflösbar ({exc}). Ohne aufgelösten Commit wäre der Build "
                     f"nicht-deterministisch (generatedAt = Build-Zeit) und die "
                     f"Provenienz (source.commit) ginge verloren (#152).")
        print(f"   (Commit nicht auflösbar: {exc})")
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

    overrides = load_overrides()
    unbekannt = set(overrides) - set(BOOKS)
    if unbekannt:
        sys.exit(f"FEHLER: alias-overrides.json nennt unbekannte Werke: "
                 f"{sorted(unbekannt)}. Bekannt sind {sorted(BOOKS)}.")

    works = []
    totals = {"records": 0, "eig": 0, "ant": 0, "epi": 0}

    for book_name, sigle in BOOKS.items():
        raw = json.loads(fetch(f"data/{book_name}/categorization_{book_name}.json", ref, source_dir))
        buch_overrides = overrides.get(book_name, {})
        figures = {}
        skipped = 0
        for row in raw:
            if not filled(row.get("Benannte Figur")):
                skipped += 1
                continue
            figure_name = clean_figure_name(row["Benannte Figur"])
            aliases = alias_map.get(figure_name.lower(), set())
            extra = buch_overrides.get(figure_name.lower())
            if extra:
                aliases = aliases | extra
            record = build_record(row, figure_name, aliases)
            if record is None:
                skipped += 1
                continue
            figures.setdefault(figure_name, []).append(record)
            totals["records"] += 1
            for cat in ("eig", "ant", "epi"):
                totals[cat] += len(record.get(cat, []))

        # Ein vertippter Figurenname im Override bliebe sonst stumm wirkungslos:
        # der Eintrag stuende in der Datei, die Klassifikation liefe unveraendert.
        fehlend = sorted(set(buch_overrides) - {n.lower() for n in figures})
        if fehlend:
            sys.exit(f"FEHLER: alias-overrides.json nennt fuer {book_name} "
                     f"Figuren, die dort nicht vorkommen: {fehlend}")

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
    parser.add_argument("--require-commit", action="store_true",
                        help="Harter Fehler statt Build-Zeit-Fallback, wenn der "
                             "Quell-Commit nicht auflösbar ist (CI, #152)")
    args = parser.parse_args()
    if args.require_commit and args.source_dir:
        parser.error("--require-commit ist mit --source-dir nicht kombinierbar "
                     "(lokale Kopie hat keinen auflösbaren Quell-Commit)")

    print("=" * 60)
    print("MHDBDB Naming Index Builder (#59)")
    print("=" * 60)
    src = args.source_dir or f"GitHub {REPO}@{args.ref}"
    print(f"\nQuelle: {src}")

    commit = None
    if not args.source_dir:
        commit = resolve_commit(args.ref, require=args.require_commit)
        if commit:
            print(f"   Commit: {commit['sha']} ({commit['date']})")

    print("\nBaue Index...")
    # Fetch unter dem RESOLVIERTEN SHA, nicht unter dem beweglichen Ref:
    # zwischen resolve_commit und den raw-Fetches kann das Quell-Repo einen
    # Push erhalten (bzw. der raw-CDN cached Branch-Refs ~5 min) — dann
    # truege der Index source.commit=X bei Inhalt=Y, und das Freshness-Gate
    # (data-integrity.yml) meldet spaeter falschen Drift (Review PR #155).
    fetch_ref = commit["sha"] if commit else args.ref
    works, totals = build_index(fetch_ref, args.source_dir)

    # generatedAt = Committer-Datum des Quell-Commits, nicht Build-Zeit:
    # zwei Builds desselben Quellstands sind dadurch byte-identisch (#125-
    # Prinzip), was den git-diff-Check in naming-index-update.yml trägt.
    # Fallback Build-Zeit nur offline/--source-dir (dann kein Auto-Diff).
    generated_at = (commit or {}).get("date") or \
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    index = {
        "version": "1.0.0",
        "generatedAt": generated_at,
        "source": {**SOURCE_META, "ref": args.ref,
                   **({"commit": commit["sha"]} if commit else {})},
        "works": works,
    }

    print(f"\nGesamt: {totals['records']} Records | "
          f"Eigennamen-Lemmata: {totals['eig']} | "
          f"Antonomasien-Lemmata: {totals['ant']} | "
          f"Epitheta: {totals['epi']}")

    json_data = json.dumps(index, ensure_ascii=False, separators=(",", ":"))
    uncompressed = len(json_data.encode("utf-8"))
    OUTPUT_FILE.parent.mkdir(exist_ok=True)
    # mtime=0: kein Zeitstempel im gzip-Header, sonst wäre jeder Build
    # byte-verschieden und der Workflow-Diff immer dirty.
    with gzip.GzipFile(OUTPUT_FILE, mode="wb", mtime=0) as f:
        f.write(json_data.encode("utf-8"))
    compressed = OUTPUT_FILE.stat().st_size

    print(f"\nGespeichert: {OUTPUT_FILE}")
    print(f"   Unkomprimiert: {uncompressed / 1024:.0f} KB")
    print(f"   Komprimiert:   {compressed / 1024:.0f} KB")


if __name__ == "__main__":
    main()
