#!/usr/bin/env python3
"""FR1/FR2/FR3: editorische Eingriffe aus <normalization> nach <editorialDecl> (Issue #236, G).

`<normalization>` ist TEI-semantisch fuer Normalisierungspraxis zustaendig. Bisher
steckten dort auch Scope-Aussagen (welcher Band, was aufgenommen wurde) und die
eigentlichen Eingriffe der MHDBDB in die Edition — die Umkehrung der beiden Anhaenge
und die Korrektur des Zaehlfehlers in XII,204. Genau diese Eingriffe sind der Grund,
warum der MHDBDB-E-Text nicht mit der Druckedition identisch ist; sie gehoeren nicht
ins Kleingedruckte eines Normalisierungsblocks.

Dieses Skript sortiert um:
  * Scope und Eingriffe  -> `<editorialDecl>` als eigene `<p>`
  * echte Normalisierung -> bleibt in `<normalization>`

Ausserdem wird der in allen drei Headern woertlich stehende, verstuemmelte Satz
„wobei I-XIII Leichs und XI Lieder sind" (aus `docs/data/linecode-templates.csv`
uebernommen) durch eine korrekte Fassung ersetzt, und der Umbau aus #236 selbst
dokumentiert.

Hinweis: Das Issue schlaegt fuer die Scope-Aussagen `<samplingDecl>` vor. Das laesst
`schema/mhdbdb.rnc` in `encodingDesc` nicht zu (erlaubt sind nur projectDesc,
editorialDecl, classDecl). Nach „Daten vor Schema" wird das Schema nicht aufgeweicht;
die Aussagen stehen als `<p>` in `<editorialDecl>`, wo sie inhaltlich ebenfalls
richtig sitzen.

Idempotent.

    python scripts/ingest/frauenlob/05-editorial-decl.py [--dry-run]
"""
import sys
from pathlib import Path

# Windows-Konsole schreibt sonst cp1252 und stirbt an "ä"/"–".
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from lxml import etree
except ImportError:
    sys.exit("ERROR: lxml not installed")

# Schreibt und stellt die Prolog-Umbrueche wieder her, die
# tree.write(xml_declaration=True) verschluckt (siehe _tei_io.py).
from _tei_io import write_tei

REPO = Path(__file__).resolve().parents[3]
TEI_NS = "http://www.tei-c.org/ns/1.0"

# Der korrigierte Scope-Satz. Ersetzt die verstuemmelte Legacy-Fassung.
SCOPE_GA = (
    "Band 1 der Göttinger Frauenlob-Ausgabe (Stackmann/Bertau 1981) besteht aus "
    "14 Teilen (I–XIV): I–III sind Leichs (Marienleich, Kreuzleich, Minneleich), "
    "IV–XIII Sangspruchtöne, XIV die Lieder. In der MHDBDB sind die Teile I–XIII "
    "als FR1 aufgenommen und Teil XIV als FR2. Die frühere Angabe, FR1 enthalte "
    "nur die Leichs, war unzutreffend: auf 973 Leich-Verse kommen dort 5.654 "
    "Sangspruch-Verse."
)

# Satzanfaenge, an denen die umzuhaengenden Absaetze erkannt werden. Der Textinhalt
# wird unveraendert uebernommen, nur der Sitz im Header aendert sich.
MOVE_PREFIXES = (
    "Band 1 der großen Göttinger Frauenlob-Edition",
    "Bei FR3 handelt es sich um den erst im Jahr 2000",
    "Es hat den Anschein, als ob den Herausgebern",
    "Auf den letzten regulären Ton",
)

RESTRUCTURE_NOTE = {
    "FR3": (
        "Eingriffe der MHDBDB in die Textgestalt (2026-07, Issue #236): Die "
        "Parallelüberlieferungen des Supplementbands waren beim ersten Ingest zu "
        "gleichrangigen Tönen verflacht worden, wodurch 28 (Ton, Strophe)-Paare "
        "mehrfach belegt und keine Stelle eindeutig zitierbar war. Sie sind aus der "
        "Legacy-Quelle rekonstruiert und stehen nun als <div type=\"parallel\"> unter "
        "der jeweiligen Strophe; 1.563 der 9.595 Verse sind damit als "
        "Parallelüberlieferung erkennbar. Die römischen Ordnungszahlen der Töne "
        "standen als gewöhnliche, teils lemmatisierte Wörter im Textfluss und sind "
        "durch <head>-Elemente mit GA-Nummer und Tonnamen ersetzt."
    ),
    "FR1": (
        "Eingriffe der MHDBDB in die Textgestalt (2026-07, Issue #236): Die römischen "
        "Ordnungszahlen der Töne standen als gewöhnliche, teils lemmatisierte Wörter "
        "im Textfluss und sind durch <head>-Elemente mit GA-Nummer und Tonnamen ersetzt."
    ),
    "FR2": (
        "Eingriffe der MHDBDB in die Textgestalt (2026-07, Issue #236): Die GA-Ebene XIV "
        "existierte nur als loses Wort im Textfluss und ist nun in <head> und in "
        "div/@n (\"XIV,1\" bis \"XIV,7\") explizit."
    ),
}

DIVERGENCE_NOTE = (
    "Der E-Text der MHDBDB ist daher an den hier genannten Stellen nicht mit der "
    "Druckedition identisch. Für Zitate ist die gedruckte Ausgabe maßgeblich."
)


def q(tag):
    return f"{{{TEI_NS}}}{tag}"


def make_p(text, indent):
    p = etree.Element(q("p"))
    p.set("{http://www.w3.org/XML/1998/namespace}lang", "de")
    p.text = text
    p.tail = "\n" + " " * indent
    return p


def process(sigle, dry_run):
    path = REPO / "tei" / f"{sigle}.tei.xml"
    tree = etree.parse(str(path))
    ed = tree.find(f".//{q('editorialDecl')}")
    norm = ed.find(q("normalization"))
    print(f"=== {sigle} ===")

    if norm is None:
        print("   kein <normalization> — uebersprungen\n")
        return 0

    existing_texts = {(p.text or "").strip() for p in ed.findall(q("p"))}
    if RESTRUCTURE_NOTE[sigle] in existing_texts:
        print("   bereits umgehaengt — nichts zu tun\n")
        return 0

    moved = []
    for p in list(norm.findall(q("p"))):
        text = (p.text or "").strip()
        if not text.startswith(MOVE_PREFIXES):
            continue
        # Die verstuemmelte Legacy-Fassung wird beim Umhaengen korrigiert.
        if text.startswith("Band 1 der großen Göttinger Frauenlob-Edition"):
            text = SCOPE_GA
            print("   Legacy-Satz „…I-XIII Leichs und XI Lieder…\" korrigiert")
        norm.remove(p)
        moved.append(text)

    # Reihenfolge: Scope zuerst, dann die Eingriffe, dann der Divergenz-Hinweis.
    new_texts = moved + [RESTRUCTURE_NOTE[sigle], DIVERGENCE_NOTE]
    insert_at = list(ed).index(norm)
    for offset, text in enumerate(new_texts):
        ed.insert(insert_at + offset, make_p(text, 8))

    remaining = [(p.text or "")[:60] for p in norm.findall(q("p"))]
    print(f"   nach <editorialDecl> verschoben: {len(moved)} Absatz/Absaetze")
    print(f"   neu ergaenzt: 2 (Umbau-Dokumentation, Divergenz-Hinweis)")
    print(f"   in <normalization> verblieben: {len(remaining)}")
    for r in remaining:
        print(f"      – {r}…")

    if not dry_run:
        write_tei(tree, path)
        print("   geschrieben.")
    print()
    return len(moved) + 2


def main():
    dry_run = "--dry-run" in sys.argv
    total = sum(process(s, dry_run) for s in ("FR1", "FR2", "FR3"))
    if dry_run:
        print("--dry-run: nichts geschrieben.")
    print(f"Aenderungen gesamt: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
