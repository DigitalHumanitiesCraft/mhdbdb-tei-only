#!/usr/bin/env python3
"""FR1/FR2/FR3: Titel und bibliographische Metadaten korrigieren (Issue #236, B und F).

Drei Baustellen:

1. **Titel** (B). „Leichs I-XIII" ist fuer FR1 falsch — 973 Leich-Versen stehen dort
   5.654 Sangspruch-Verse gegenueber. FR2 fuehrt „Lied XIV" statt „Lieder".

2. **FR3 beschreibt die falsche Edition** (F). `works.xml` und der TEI-Header geben
   die Goettinger Ausgabe von 1981 an; richtig ist der Supplementband von 2000
   (ISBN 3-525-82504-8, Hrsg. Haustein/Stackmann). Nur die unstrukturierte `<note>`
   war korrekt.

3. **Zotero-Title-Case** hat „Frauenlob Teil II" zu „Frauenlob Teil Ii" und
   „Teil III" zu „Teil Iii" verstuemmelt — publiziert bis in `api/works/work_463.json`.

`works.xml` ist Master, die TEI-Header werden nachgezogen.

Zur Supplement-Relation: Das Issue schlaegt `<relatedItem type="supplement">` innerhalb
des `biblStruct` vor. Das laesst `schema/mhdbdb-authority.rnc` nicht zu — `relatedItem`
existiert dort nur als Huelle *um* einen `biblStruct`, und `note` kennt kein `@type`.
Nach der Regel „Daten vor Schema" wird das Schema nicht aufgeweicht; die Relation wird
stattdessen mit dem bereits erlaubten `<ref type= target=>` in `<analytic>` ausgedrueckt.

Idempotent.

    python scripts/ingest/frauenlob/04-metadata.py [--dry-run]
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

REPO = Path(__file__).resolve().parents[3]
TEI_NS = "http://www.tei-c.org/ns/1.0"

TITLES = {
    "FR1": "Lyrik von Frauenlob (Leichs und Sangsprüche, GA I–XIII / Stackmann–Bertau 1981)",
    "FR2": "Lyrik von Frauenlob (Lieder, GA XIV / Stackmann–Bertau 1981)",
    "FR3": "Lyrik von Frauenlob (Supplement: Sangsprüche in Tönen Frauenlobs / Haustein–Stackmann 2000)",
}

ANALYTIC_TITLES = {
    "FR1": "Frauenlob Teil I",
    "FR2": "Frauenlob Teil II",
    "FR3": "Frauenlob Teil III",
}

FR3_MONOGR_TITLE = ("Sangsprüche in Tönen Frauenlobs. "
                    "Supplement zur Göttinger Frauenlob-Ausgabe")
FR3_ISBN = "3-525-82504-8"
FR3_DATE = "2000"
FR3_EDITORS = [("Jens", "Haustein"), ("Karl", "Stackmann")]
FR3_SERIES_VOLUME = "232"
FR3_NOTE = (
    "Frauenlob (Heinrich von Meissen). Sangsprüche in Tönen Frauenlobs. "
    "Supplement zur Göttinger Frauenlob-Ausgabe. 1. Teil: Einleitungen, Texte. "
    "Hrsg. v. Jens Haustein und Karl Stackmann unter Mitarbeit von Thomas Riebe "
    "und Christoph Fasbender. Göttingen: Vandenhoeck & Ruprecht, 2000 "
    "(Abhandlungen der Akademie der Wissenschaften zu Göttingen, "
    "Philologisch-historische Klasse, Folge 3, Band 232). "
    "Das Supplement bezieht sich auf die Göttinger Ausgabe von 1981 (FR1 und FR2). "
    "Der 2. Teil des Supplements (Apparate, Erläuterungen, Register) ist in der "
    "MHDBDB bewusst nicht aufgenommen, weil nur Texteditionen ingestiert werden."
)
FR3_SUPPLEMENT_REF = "Supplement zur Göttinger Ausgabe von 1981"


def q(tag):
    return f"{{{TEI_NS}}}{tag}"


def set_text(el, value, log, label):
    if el is None:
        return 0
    if el.text == value:
        return 0
    log.append(f"      {label}: {el.text!r} -> {value!r}")
    el.text = value
    return 1


def fix_biblstruct(bs, sigle, log):
    """Bringt einen biblStruct auf den korrekten Stand. Gibt Zahl der Aenderungen."""
    changes = 0
    analytic = bs.find(q("analytic"))
    if analytic is not None:
        changes += set_text(analytic.find(q("title")), ANALYTIC_TITLES[sigle],
                            log, "analytic/title")

    if sigle != "FR3":
        return changes

    monogr = bs.find(q("monogr"))
    if monogr is not None:
        changes += set_text(monogr.find(q("title")), FR3_MONOGR_TITLE, log, "monogr/title")
        for idno in monogr.findall(q("idno")):
            if idno.get("type") == "ISBN":
                changes += set_text(idno, FR3_ISBN, log, "ISBN")
        imprint = monogr.find(q("imprint"))
        if imprint is not None:
            changes += set_text(imprint.find(q("date")), FR3_DATE, log, "imprint/date")

        # Herausgeber austauschen: Stackmann/Bertau (GA 1981) -> Haustein/Stackmann (2000).
        current = [(e.findtext(q("forename")), e.findtext(q("surname")))
                   for e in monogr.findall(q("editor"))]
        if current != FR3_EDITORS:
            log.append(f"      editor: {current} -> {FR3_EDITORS}")
            anchor = None
            for e in monogr.findall(q("editor")):
                anchor = e
                monogr.remove(e)
            idx = list(monogr).index(monogr.find(q("imprint"))) if monogr.find(q("imprint")) is not None else len(monogr)
            for offset, (fore, sur) in enumerate(FR3_EDITORS):
                ed = etree.Element(q("editor"))
                ed.text = "\n" + " " * 18
                f = etree.SubElement(ed, q("forename")); f.text = fore
                f.tail = "\n" + " " * 18
                s = etree.SubElement(ed, q("surname")); s.text = sur
                s.tail = "\n" + " " * 16
                ed.tail = "\n" + " " * 16
                monogr.insert(idx + offset, ed)
            changes += 1

    series = bs.find(q("series"))
    if series is not None and series.find(q("biblScope")) is None:
        scope = etree.SubElement(series, q("biblScope"))
        scope.set("unit", "volume")
        scope.text = FR3_SERIES_VOLUME
        title_el = series.find(q("title"))
        if title_el is not None:
            title_el.tail = "\n" + " " * 16
        scope.tail = "\n" + " " * 14
        log.append(f"      series/biblScope[@unit=volume] = {FR3_SERIES_VOLUME}")
        changes += 1

    # Supplement-Relation. <relatedItem> ist im Authority-Schema nur als Huelle um
    # einen biblStruct erlaubt; <ref> in <analytic> ist der konforme Weg.
    if analytic is not None:
        existing = [r for r in analytic.findall(q("ref")) if r.get("type") == "supplement"]
        if not existing:
            ref = etree.SubElement(analytic, q("ref"))
            ref.set("type", "supplement")
            ref.set("target", "#FR1_FR1")
            ref.text = FR3_SUPPLEMENT_REF
            ref.tail = "\n" + " " * 14
            prev = ref.getprevious()
            if prev is not None:
                prev.tail = "\n" + " " * 16
            log.append('      <ref type="supplement" target="#FR1_FR1"> ergaenzt')
            changes += 1

    note = bs.find(q("note"))
    changes += set_text(note, FR3_NOTE, log, "note")
    return changes


def process_works_xml(dry_run):
    path = REPO / "authority-files" / "works.xml"
    tree = etree.parse(str(path))
    total = 0
    print("=== authority-files/works.xml ===")
    for sigle in ("FR1", "FR2", "FR3"):
        bs = tree.find(f".//{q('biblStruct')}[@key='{sigle}']")
        if bs is None:
            sys.exit(f"ERROR: biblStruct key={sigle} nicht gefunden")
        log = []
        n = fix_biblstruct(bs, sigle, log)
        if n:
            print(f"   {sigle}: {n} Aenderung(en)")
            for line in log:
                print(line)
        total += n
    if total and not dry_run:
        tree.write(str(path), encoding="UTF-8", xml_declaration=True)
        print("   geschrieben.")
    elif not total:
        print("   nichts zu tun.")
    print()
    return total


def process_tei(sigle, dry_run):
    path = REPO / "tei" / f"{sigle}.tei.xml"
    tree = etree.parse(str(path))
    log = []
    total = 0
    print(f"=== tei/{sigle}.tei.xml ===")

    total += set_text(tree.find(f".//{q('titleStmt')}/{q('title')}"),
                      TITLES[sigle], log, "titleStmt/title")
    total += set_text(tree.find(f".//{q('msName')}"), TITLES[sigle], log, "msName")

    bs = tree.find(f".//{q('biblStruct')}[@key='{sigle}']")
    if bs is not None:
        total += fix_biblstruct(bs, sigle, log)

    if total:
        print(f"   {total} Aenderung(en)")
        for line in log:
            print(line)
        if not dry_run:
            tree.write(str(path), encoding="UTF-8", xml_declaration=True)
            print("   geschrieben.")
    else:
        print("   nichts zu tun.")
    print()
    return total


def main():
    dry_run = "--dry-run" in sys.argv
    total = process_works_xml(dry_run)
    for sigle in ("FR1", "FR2", "FR3"):
        total += process_tei(sigle, dry_run)
    if dry_run:
        print("--dry-run: nichts geschrieben.")
    print(f"Aenderungen gesamt: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
