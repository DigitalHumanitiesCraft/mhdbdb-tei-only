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

# Lizenzsperre, durchgesetzt und nicht nur dokumentiert. `FnhdC/` ist das Bonner
# Fruehneuhochdeutschkorpus von korpora.org: "Eine Weiterverbreitung ist nicht gestattet."
# Die zwei Einzeldateien stammen ebenfalls daraus, ohne es im Namen zu zeigen (Durandus.txt
# ist das FNHD-Quellenverzeichnis, BuchAltvaeter.txt ist FnhdC-Text 121). Aktuell passiert
# keine davon die 50-%-Schwelle; die Liste haelt das auch dann, wenn sich das aendert.
EXCLUDE_PREFIXES = ("FnhdC/",)
EXCLUDE_FILES = ("Neue Texte Klaus/Durandus.txt", "Neue Texte Klaus/BuchAltväter.txt")

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
#
# ACHTUNG, der Vergleich ist bewusst zeilenendungs-tolerant. Diese sechs Pfade liegen
# LF-normalisiert im Git-Index, weil fuer sie kein `-text` gilt (sie kamen mit #110 und #236
# ins Repo, vor sources/.gitattributes). Die Archivkopien in sources/linecode/ tragen CRLF.
# Ein byte-weiser Vergleich waere also auf jedem LF-Checkout rot, obwohl inhaltlich nichts
# abweicht. Die Zusage lautet deshalb "inhaltsgleich", nicht "byte-identisch".
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

# Zuordnung ueber den xml:id-Join (Linecode ohne fuehrende Nullen gegen die Token-@xml:id im
# Korpus), nicht ueber den Dateinamen: die Namen folgen hier nicht den Sigeln. Eingetragen ist
# nur, was der Join entscheidet, mit Trefferquote als Kommentar.
#
# NICHT eingetragen sind die Faelle, in denen der Join nichts beweist, weil die Stems trivial
# klein sind und damit in jedem Korpustext vorkommen: crone*.txt, waltherhaupttext*.txt,
# tannh_i..xvi, akkon.txt, osw1-doc.txt, sfl1.txt, kolner-fechtbuch-1.txt, hug1.txt,
# ac3-new.txt, tann.txt. Dort liefert der Join drei bis fuenf gleichwertige Kandidaten.
# Ein Join ueber Schluessel, die trivial klein sind, matcht ueberall und beweist nichts.
SIGLE_OVERRIDE = {
    # ausserhalb von ERLEDIGT
    "Neue Texte Klaus/GTK2.txt": "GWTK",     # 400/400 Stems
    "Neue Texte Klaus/EFB.txt": "CEFB",      # 399/400
    "Neue Texte Klaus/CLV.txt": "CLV",       # 400/400
    "Neue Texte Klaus/Normal.txt": "VTC",    # Namenregister, siehe INHALTSTYP
    # Dateinamen, die von der Sigle abweichen
    "ERLEDIGT/Vita_Caroli_dt_gesamt_linecode_mit_tags.txt": "VTC",   # 599/599
    "ERLEDIGT/Vita_Caroli_dt_gesamt_linecode_TEST.txt": "VTC",       # 591/600
    "ERLEDIGT/VTC_neu.txt": "VTC",                                   # 599/599
    "ERLEDIGT/PUC_korr_12_3_2013.txt": "PUC",                        # 600/600
    "ERLEDIGT/Alte Texte/KVM2.txt": "KVM",                           # 35/36
    "ERLEDIGT/Alte Texte/OVG8 insert.txt": "OVG",                    # 96/96
    # der Dateiname sagt KBL5, der Join sagt KBL4. Der Join gewinnt.
    "ERLEDIGT/Kochrezepttextsammlungen/fertig codiert/KBL5.txt": "KBL4",  # 600/600
    # 600/600 plus Dateiname plus Ordner; zweitbester Kandidat NEI mit 593 ist der
    # Vorgaengertext, nicht dieselbe Datei
    "ERLEDIGT/Neidhart-c/NEIC_exportiert.txt": "NEIC",
    "ERLEDIGT/Neidhart-c/NEIC_Quelle-cod.txt": "NEIC",
    "ERLEDIGT/Neidhart-c/NEIC_Quelle-cod_1010.txt": "NEIC",
    "ERLEDIGT/Tannhäuser/TA_komplett.txt": "TA",                     # 600/600
    "ERLEDIGT/Tannhäuser/TA_komplett.txt.bak": "TA",                 # 600/600
}

# Dateien, die zwar zu einer Sigle gehoeren, aber keine Textquelle sind. Ohne diese Spalte
# behauptet die Sigle eine Volltextquelle, die es nicht ist.
INHALTSTYP = {
    "Neue Texte Klaus/Normal.txt": "namenregister",
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


def content_digest(data):
    """sha256 ueber den Inhalt mit auf LF normalisierten Zeilenenden."""
    return hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()


def check_working_copies(repo, digest, archive):
    """Warnt, wenn eine Arbeitskopie im Repo vom Archivstand abweicht."""
    for rel, wc in WORKING_COPIES.items():
        p = repo / wc
        if rel not in digest:
            print(f"  HINWEIS: {rel} ist nicht (mehr) im Archivauszug, {wc} ungeprueft")
            continue
        if not p.exists():
            print(f"  HINWEIS: Arbeitskopie fehlt im Repo: {wc}")
            continue
        want = content_digest((archive / rel).read_bytes())
        if content_digest(p.read_bytes()) != want:
            raise SystemExit(
                f"Arbeitskopie weicht inhaltlich vom Archiv ab: {wc}\n"
                f"  (Vergleich ist zeilenendungs-tolerant, es ist also ein echter Unterschied)"
            )


def main(archive, scan_csv, repo):
    dest = repo / "sources" / "linecode"
    sigles = {p.name.split(".")[0].upper() for p in (repo / "tei").glob("*.tei.xml")}

    rows = [r for r in csv.DictReader(scan_csv.open(encoding="utf-8"))
            if r.get("coded_pct") and float(r["coded_pct"]) >= 50]
    if not rows:
        raise SystemExit(f"Keine codierten Dateien in {scan_csv}. Archivpfad richtig getippt?")
    meta = {r["path"]: r for r in rows}

    kandidaten = []
    for rel in [r["path"] for r in rows] + EXTRA:
        if rel.startswith(EXCLUDE_PREFIXES) or rel in EXCLUDE_FILES:
            print(f"  uebersprungen (Lizenzsperre): {rel}")
            continue
        kandidaten.append(rel)

    by_hash, digest = defaultdict(list), {}
    for rel in kandidaten:
        digest[rel] = hashlib.sha256((archive / rel).read_bytes()).hexdigest()
        by_hash[digest[rel]].append(rel)
    canonical, dup_of = resolve_duplicates(by_hash)

    check_working_copies(repo, digest, archive)

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
            "inhaltstyp": INHALTSTYP.get(rel, "volltext" if sigle else ""),
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
        print(f"  entfernt (Altstand): {p.relative_to(dest)}")
        p.unlink()
    for p in sorted((q for q in dest.rglob("*") if q.is_dir()), reverse=True):
        if not any(p.iterdir()):
            print(f"  entfernt (leerer Ordner): {p.relative_to(dest)}")
            p.rmdir()

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

    mit_sigle = sum(1 for m in manifest if m["sigle"])
    print(f"kopiert:                 {len(manifest)} Dateien, "
          f"{sum(m['bytes'] for m in manifest) / 1024 / 1024:.1f} MB")
    print(f"davon Sigle in tei/:     {mit_sigle} Dateien, "
          f"{len({m['sigle'] for m in manifest if m['sigle']})} distinkte Sigeln")
    print(f"ohne Sigle-Zuordnung:    {len(manifest) - mit_sigle}")
    print(f"Dubletten entdoppelt:    {len(dup_of)}")


if __name__ == "__main__":
    main(Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]))
