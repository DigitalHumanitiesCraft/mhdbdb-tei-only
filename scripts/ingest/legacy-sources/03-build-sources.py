"""Kopiert die codierten Legacy-Ingest-Dateien aus dem Archiv nach `sources/linecode/`.

    python scripts/ingest/legacy-sources/03-build-sources.py <ARCHIV> <SCAN-CSV> <REPO>

<ARCHIV> ist `MHDBDB_Inhaltliches/Texte/` im Sharefolder-Backup, **nicht** der Unterordner
`ERLEDIGT/`. Das war anfangs anders und war falsch: vier codierte Dateien liegen in
`Neue Texte Klaus/`, also ausserhalb von ERLEDIGT. Wer die Wurzel enger setzt, uebersieht sie.

<SCAN-CSV> ist die Ausgabe von 01-scan-linecode.py. Der Lauf ist idempotent: gleicher Archivstand
erzeugt identische Dateien, ueberzaehlige Dateien aus einem frueheren Lauf werden entfernt.

Kopiert wird byte-identisch. Ordner- und Dateinamen werden auf ASCII-Kleinschreibung normalisiert,
der Originalpfad bleibt in der Manifest-Spalte `quelle` erhalten. Zusaetzlich wird je Datei eine
sha256 gefuehrt, damit die Kopie jederzeit gegen das Archiv geprueft werden kann.
"""
import csv
import hashlib
import re
import shutil
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

# Codierte Datei, die kein Plaintext ist und deshalb nicht von 01-scan-linecode.py kommt.
# RTF ist ein Textformat, das Git behandeln kann; die Word-Binaerformate bleiben draussen,
# siehe sources/INVENTAR-ARCHIV.md.
EXTRA = ["ERLEDIGT/Frauenlob_Bd2-codiert.rtf"]

# Werkzeuge der Legacy-Pipeline: kein Text, sondern das Mittel, mit dem die Linecodes entstanden
# sind. Landen ausserhalb von linecode/ und nicht im Manifest, weil sie keine Textquelle sind.
TOOLING = {
    "linecode Generator.dot": "legacy-tooling/linecode-generator.dot",
}

# Dublettengruppen: `CvK_KLD_codiert/<SIG>.txt` ist der sauberere Name gegenueber
# `Alte Texte/Carl von Kraus/<SIG> (1).txt` und gewinnt.
PREFER = "ERLEDIGT/CvK_KLD_codiert/"

# Byte-identische Arbeitskopien, die schon an anderer Stelle im Repo liegen. Werden bei jedem
# Lauf geprueft, damit die beiden Staende nicht auseinanderlaufen.
WORKING_COPIES = {
    "ERLEDIGT/FR2.txt": "scripts/ingest/frauenlob/source/FR2-linecode.txt",
    "ERLEDIGT/FR3.txt": "scripts/ingest/frauenlob/source/FR3-linecode.txt",
    "ERLEDIGT/WaltherHaupttext.txt": "ingest/wvv/WaltherHaupttext.txt",
    "ERLEDIGT/WaltherHaupttext1.txt": "ingest/wvv/WaltherHaupttext1.txt",
    "ERLEDIGT/WaltherHaupttext2.txt": "ingest/wvv/WaltherHaupttext2.txt",
    "ERLEDIGT/WaltherHaupttext3.txt": "ingest/wvv/WaltherHaupttext3.txt",
    "ERLEDIGT/WaltherHaupttext_cn.txt": "ingest/wvv/WaltherHaupttext_cn.txt",
    "ERLEDIGT/WaltherLeich.txt": "ingest/wvv/WaltherLeich.txt",
}

# Zuordnung der vier codierten Dateien ausserhalb von ERLEDIGT zu ihrem Korpustext. Ermittelt
# ueber den xml:id-Join (Linecode ohne fuehrende Nullen), nicht ueber den Dateinamen, weil die
# Namen dort nicht den Sigeln folgen. Treffer in Klammern.
SIGLE_OVERRIDE = {
    "Neue Texte Klaus/GTK2.txt": "GWTK",     # 400/400 Stems
    "Neue Texte Klaus/EFB.txt": "CEFB",      # 399/400
    "Neue Texte Klaus/CLV.txt": "CLV",       # 400/400
    "Neue Texte Klaus/Normal.txt": "VTC",    # Namenregister, 14/14 Sonden im Volltext
}


def slug(s):
    s = unicodedata.normalize("NFKD", s.replace("ß", "ss")).lower()
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"-{2,}", "-", re.sub(r"[^a-z0-9_-]+", "-", s)).strip("-")


def dest_path(rel):
    parts = list(Path(rel).parts)
    stem, dot, ext = parts.pop().rpartition(".")
    if not dot:
        stem, ext = ext, ""
    if ext.lower() == "bak":
        # *.bak ist repoweit gitignored -> Marker in den Stamm ziehen
        stem, ext = stem.replace(".txt", "") + "-bak", "txt"
    name = slug(stem) + (f".{ext.lower()}" if ext else "")
    return Path(*[slug(p) for p in parts]) / name


def resolve_duplicates(by_hash):
    """Je Inhalt genau eine kanonische Kopie, der Rest wird als Dublette vermerkt."""
    canonical, dup_of = {}, {}
    for group in by_hash.values():
        if len(group) == 1:
            canonical[group[0]] = True
            continue
        keep = next((g for g in group if g.startswith(PREFER)), None)
        # kuerzester Pfad als Fallback: "HVM.txt" gewinnt gegen "HVM(1).txt"
        keep = keep or min(group, key=lambda g: (len(g), g))
        canonical[keep] = True
        dup_of.update({g: keep for g in group if g != keep})
    return canonical, dup_of


def main(archive, scan_csv, repo):
    dest = repo / "sources" / "linecode"
    sigles = {p.name.split(".")[0].upper() for p in (repo / "tei").glob("*.tei.xml")}

    rows = [r for r in csv.DictReader(scan_csv.open(encoding="utf-8"))
            if r.get("coded_pct") and float(r["coded_pct"]) >= 50]
    meta = {r["path"]: r for r in rows}

    by_hash, digest = defaultdict(list), {}
    for rel in [r["path"] for r in rows] + EXTRA:
        digest[rel] = hashlib.sha256((archive / rel).read_bytes()).hexdigest()
        by_hash[digest[rel]].append(rel)
    canonical, dup_of = resolve_duplicates(by_hash)

    for rel, wc in WORKING_COPIES.items():
        p = repo / wc
        if p.exists() and hashlib.sha256(p.read_bytes()).hexdigest() != digest.get(rel):
            raise SystemExit(f"Arbeitskopie weicht vom Archiv ab: {wc}")

    dest.mkdir(parents=True, exist_ok=True)
    manifest, seen = [], {}
    for rel in sorted(canonical, key=str.lower):
        d = dest_path(rel)
        if d in seen:
            raise SystemExit(f"Namenskollision nach Slugify: {rel} vs {seen[d]} -> {d}")
        seen[d] = rel
        (dest / d).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(archive / rel, dest / d)
        if hashlib.sha256((dest / d).read_bytes()).hexdigest() != digest[rel]:
            raise SystemExit(f"Kopie weicht ab: {rel}")

        m = meta.get(rel, {})
        stem = re.sub(r"\.(txt|bak)$", "", Path(rel).name, flags=re.I)
        cand = re.sub(r"\s*\(\d+\)\s*$", "", re.sub(r"\.txt$", "", stem, flags=re.I)).upper()
        sigle = SIGLE_OVERRIDE.get(rel) or (cand if cand in sigles else "")
        manifest.append({
            "datei": str(d).replace("\\", "/"),
            "sigle": sigle,
            "quelle": rel,
            "bytes": (archive / rel).stat().st_size,
            "zeilen": m.get("lines", ""),
            "codierte_zeilen": m.get("coded_lines", ""),
            "codebreiten": m.get("code_widths", ""),
            "encoding_gelesen": m.get("encoding", ""),
            "sha256": digest[rel],
            "dubletten_im_archiv": " | ".join(sorted(g for g, k in dup_of.items() if k == rel)),
            "arbeitskopie_im_repo": WORKING_COPIES.get(rel, ""),
        })

    wanted = {dest / m["datei"] for m in manifest}
    stale = [p for p in dest.rglob("*") if p.is_file() and p not in wanted]
    for p in stale:
        p.unlink()

    for rel, target in TOOLING.items():
        out = repo / "sources" / target
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(archive / rel, out)
        sha = hashlib.sha256(out.read_bytes()).hexdigest()
        print(f"Werkzeug: {target}  sha256 {sha[:16]}  ({(archive / rel).stat().st_size // 1024} KB)")

    with (repo / "sources" / "linecode-manifest.csv").open("w", encoding="utf-8", newline="\n") as fh:
        w = csv.DictWriter(fh, fieldnames=list(manifest[0].keys()))
        w.writeheader()
        w.writerows(manifest)

    print(f"kopiert:                 {len(manifest)} Dateien, "
          f"{sum(m['bytes'] for m in manifest) / 1024 / 1024:.1f} MB")
    print(f"davon Sigle in tei/:     {sum(1 for m in manifest if m['sigle'])}")
    print(f"Dubletten entdoppelt:    {len(dup_of)}")
    if stale:
        print(f"entfernt (Altstand):     {len(stale)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
