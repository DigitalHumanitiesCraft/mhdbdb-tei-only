#!/usr/bin/env python3
"""Abgleich der Legacy-Linecode-Quelle gegen den TEI-Bestand (Issue #236).

Liest source/FR3-linecode.txt bzw. source/FR2-linecode.txt und stellt die daraus
abgeleitete Struktur der im TEI vorhandenen gegenueber. Schreibt nichts.

Vorbedingung fuer 02-restore-parallel-level.py: laeuft dieses Skript nicht sauber
durch, ist der Umbau nicht abgesichert.

    python scripts/ingest/frauenlob/01-verify-linecode-vs-tei.py

Exit 0 = deckungsgleich, Exit 1 = Abweichung.
"""
import sys
import collections
from pathlib import Path

# Windows-Konsole schreibt sonst cp1252 und stirbt an "ä"/"–".
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    from lxml import etree
except ImportError:
    sys.exit("ERROR: lxml not installed")

REPO = Path(__file__).resolve().parents[3]
SOURCE = Path(__file__).resolve().parent / "source"
TEI_NS = "http://www.tei-c.org/ns/1.0"
NS = {"t": TEI_NS}
XID = "{http://www.w3.org/XML/1998/namespace}id"

# Stellenaufteilung der 19-stelligen Linecodes, vgl. docs/data/linecode-templates.csv
TEMPLATES = {
    # sigle: (name, slices) — slices als (feld, start, ende)
    "FR3": ("0000000uddaaass---h", [
        ("u", 7, 8), ("ton", 8, 10), ("strophe", 10, 13),
        ("lg", 13, 15), ("vers", 15, 18), ("head", 18, 19),
    ]),
    "FR2": ("0000000000000dss--h", [
        ("lied", 13, 14), ("strophe", 14, 16), ("vers", 16, 18), ("head", 18, 19),
    ]),
}


# Bekannte Ingest-Normalisierung, von KZW in #236 benannt: bei Ton XV, Strophen 23
# und 24 nummeriert die Quelle das einzige <lg> jeweils als 1, das TEI als 2 bzw. 3.
# Kein Datenverlust (die Verszahlen stimmen), deshalb erlaubt. Der Eintrag steht hier
# als Ratsche: eine WEITERE Umnummerierung wird zum Fehler, statt in einer pauschalen
# Toleranz mitzulaufen. Schluessel: ((ton, strophe), u) -> (Quelle, TEI).
LG_UMNUMMERIERT = {
    ((15, 23), 1): ([1], [2]),
    ((15, 24), 1): ([1], [3]),
}


def parse_linecode_file(path, sigle):
    """Liest eine Linecode-Quelldatei. Gibt (zeilen, aufgefuellt, uebersprungen) zurueck.

    Defekt heisst hier: nicht 19-stellig. 86 Zeilen in FR3 haben nur 18 Stellen,
    weil eine fuehrende Null fehlt (VIII,215/u=1 und V,209/u=2) — siehe README.
    Diese werden mit zfill aufgefuellt und mitgezaehlt, nicht verworfen.

    Nicht-numerische und zu lange Codes kann dieses Verfahren nicht deuten. Sie
    werden uebersprungen, aber gemeldet: ein stiller Uebersprung wuerde genau die
    Fehlerklasse verbergen, gegen die dieses Skript schuetzen soll. Aktuell ist
    die Liste in beiden Quelldateien leer (0 nicht-numerische, 0 ueberlange).
    """
    _, slices = TEMPLATES[sigle]
    rows, padded, skipped = [], 0, []
    for lineno, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not raw.strip():
            continue
        code, _, text = raw.partition(" ")
        if not code.isdigit():
            skipped.append((lineno, "nicht numerisch", raw[:40]))
            continue
        if len(code) < 19:
            code = code.zfill(19)
            padded += 1
        elif len(code) > 19:
            skipped.append((lineno, f"{len(code)} Stellen", raw[:40]))
            continue
        row = {name: int(code[a:b]) for name, a, b in slices}
        row["lineno"] = lineno
        row["text"] = text.strip()
        # Der xml:id-Rumpf ist der Linecode ohne fuehrende Nullen.
        row["idstem"] = str(int(code))
        rows.append(row)
    return rows, padded, skipped


def tei_structure_fr3(tree):
    """(ton, strophe) -> {u: [lg-Nummern]} aus dem TEI.

    Bewusst unabhaengig von der div-Verschachtelung: u, Ton und Strophe werden je
    <lg> aus dem xml:id des ersten Tokens gelesen. Damit liefert die Pruefung vor
    und nach dem Umbau aus 02-restore-parallel-level.py dasselbe Ergebnis und
    bleibt als dauerhaftes Gate brauchbar.
    """
    body = tree.find(f".//{{{TEI_NS}}}body")
    struct = collections.OrderedDict()
    n_l = 0
    for lg in body.iter(f"{{{TEI_NS}}}lg"):
        lines = lg.findall(f".//{{{TEI_NS}}}l")
        n_l += len(lines)
        first_w = lg.find(f".//{{{TEI_NS}}}w")
        if first_w is None:
            continue
        stem = first_w.get(XID).split("_")[1].zfill(12)
        u, ton, strophe = int(stem[0]), int(stem[1:3]), int(stem[3:6])
        struct.setdefault((ton, strophe), {}).setdefault(u, []).append(int(lg.get("n")))
    return struct, n_l


def tei_structure_fr2(tree):
    """lied -> [strophen] aus dem TEI.

    div/@n traegt seit #236 die GA-Ebene ("XIV,1"); fuer den Abgleich zaehlt nur
    die Liednummer dahinter.
    """
    body = tree.find(f".//{{{TEI_NS}}}body")
    struct = collections.OrderedDict()
    n_l = 0
    for div in body.findall(f"{{{TEI_NS}}}div"):
        n = (div.get("n") or "").rsplit(",", 1)[-1]
        lgs = list(div.iter(f"{{{TEI_NS}}}lg"))
        struct[int(n)] = [int(lg.get("n")) for lg in lgs]
        n_l += sum(len(lg.findall(f".//{{{TEI_NS}}}l")) for lg in lgs)
    return struct, n_l


def check_fr3():
    rows, padded, skipped = parse_linecode_file(SOURCE / "FR3-linecode.txt", "FR3")
    tree = etree.parse(str(REPO / "tei" / "FR3.tei.xml"))
    tei_struct, tei_l = tei_structure_fr3(tree)

    heads = [r for r in rows if r["head"]]
    body_rows = [r for r in rows if not r["head"]]

    src = collections.OrderedDict()
    for r in body_rows:
        src.setdefault((r["ton"], r["strophe"]), {}).setdefault(r["u"], set()).add(r["lg"])

    print(f"  Quellzeilen: {len(rows)} (davon {padded} auf 19 Stellen aufgefuellt)")
    print(f"  davon Ueberschriften (h != 0): {len(heads)}")
    print(f"  Strophen  Quelle {len(src):>4}   TEI {len(tei_struct):>4}")
    print(f"  Verse     Quelle {len(body_rows):>4}   TEI {tei_l:>4}")

    errors = []
    errors.extend(f"uebersprungene Quellzeile {ln} ({grund}): {txt!r}"
                  for ln, grund, txt in skipped)
    only_src = sorted(set(src) - set(tei_struct))
    only_tei = sorted(set(tei_struct) - set(src))
    if only_src:
        errors.append(f"nur in der Quelle: {only_src}")
    if only_tei:
        errors.append(f"nur im TEI: {only_tei}")

    # Drei Ebenen, absteigend streng: u-Mengen, dann Zahl der <lg> je Zeuge, dann
    # ihre Nummern. Die mittlere Ebene ist die eigentlich neue: eine abweichende
    # Strophen-Unterteilung INNERHALB eines Zeugen laesst die Verssumme unberuehrt
    # und lief vorher durch.
    bekannt = 0
    for key in sorted(set(src) & set(tei_struct)):
        su = sorted(src[key])
        tu = sorted(tei_struct[key])
        if su != tu:
            errors.append(f"u-Ebenen {key}: Quelle {su} vs TEI {tu}")
            continue
        for u in su:
            s_lg = sorted(src[key][u])
            t_lg = sorted(tei_struct[key][u])
            if len(s_lg) != len(t_lg):
                errors.append(f"lg-Anzahl {key} u={u}: "
                              f"Quelle {len(s_lg)} vs TEI {len(t_lg)}")
            elif s_lg != t_lg:
                if LG_UMNUMMERIERT.get((key, u)) == (s_lg, t_lg):
                    bekannt += 1
                else:
                    errors.append(f"lg-Nummern {key} u={u}: Quelle {s_lg} vs TEI {t_lg}")
    if len(body_rows) != tei_l:
        errors.append(f"Verszahl: Quelle {len(body_rows)} vs TEI {tei_l}")
    print(f"  lg-Nummern: {bekannt} von {len(LG_UMNUMMERIERT)} bekannten "
          f"Umnummerierungen angetroffen")
    # Ratsche in beide Richtungen. Ohne diesen Zweig bliebe ein Eintrag, dessen
    # Fall inzwischen aufgeraeumt ist, als toter Code samt einer Begruendung
    # stehen, die nichts mehr beschreibt.
    if bekannt != len(LG_UMNUMMERIERT):
        # Absichtlich offen formuliert: "Ausnahme gehoert gestrichen" waere nur
        # im Fall "aufgeraeumt" richtig. Ist eine Adresse ANDERS umnummeriert,
        # feuert oben schon der lg-Nummern-Fehler, und eine zweite Diagnose
        # daneben wuerde jemanden dazu verleiten, einen noch gebrauchten Eintrag
        # zu loeschen.
        errors.append(
            f"LG_UMNUMMERIERT: {bekannt} von {len(LG_UMNUMMERIERT)} Eintraegen "
            f"angetroffen. Entweder ist der Fall aufgeraeumt (dann Eintrag "
            f"streichen) oder er sieht anders aus als beschrieben (dann steht "
            f"die Abweichung oben) — bitte pruefen"
        )

    print()
    print("  Ueberschriften-Tokens (h=1), Sitz im Textfluss:")
    for r in heads:
        stem = "(vor dem ersten div)" if r["ton"] == 0 else \
            f"Ton {r['ton']}, Strophe {r['strophe']}, lg {r['lg']}, Vers {r['vers']}"
        print(f"    {r['text']!r:<26} {stem}")

    return errors


def check_fr2():
    rows, padded, skipped = parse_linecode_file(SOURCE / "FR2-linecode.txt", "FR2")
    tree = etree.parse(str(REPO / "tei" / "FR2.tei.xml"))
    tei_struct, tei_l = tei_structure_fr2(tree)

    heads = [r for r in rows if r["head"]]
    body_rows = [r for r in rows if not r["head"]]
    src = collections.OrderedDict()
    for r in body_rows:
        src.setdefault(r["lied"], set()).add(r["strophe"])

    print(f"  Quellzeilen: {len(rows)} (davon {padded} aufgefuellt)")
    print(f"  Lieder    Quelle {len(src):>4}   TEI {len(tei_struct):>4}")
    print(f"  Verse     Quelle {len(body_rows):>4}   TEI {tei_l:>4}")
    print(f"  Ueberschriften: {[r['text'] for r in heads]}")

    errors = []
    errors.extend(f"uebersprungene Quellzeile {ln} ({grund}): {txt!r}"
                  for ln, grund, txt in skipped)
    if set(src) != set(tei_struct):
        errors.append(f"Lieder: Quelle {sorted(src)} vs TEI {sorted(tei_struct)}")
    # In FR2 sind die Strophennummern der Quelle und `lg/@n` im TEI dieselbe
    # durchlaufende Zaehlung (Lied 1 -> 1..5, Lied 2 -> 6..10, nachgemessen fuer
    # alle sieben Lieder). Deshalb hier auf Gleichheit pruefen, nicht nur auf die
    # Anzahl: eine Umnummerierung bei gleicher Strophenzahl liefe sonst durch.
    for lied in sorted(set(src) & set(tei_struct)):
        s_str, t_str = sorted(src[lied]), sorted(tei_struct[lied])
        if s_str != t_str:
            errors.append(f"Strophen Lied {lied}: Quelle {s_str} vs TEI {t_str}")
    if len(body_rows) != tei_l:
        errors.append(f"Verszahl: Quelle {len(body_rows)} vs TEI {tei_l}")
    return errors


def main():
    all_errors = []
    for sigle, fn in (("FR3", check_fr3), ("FR2", check_fr2)):
        print(f"=== {sigle} ===")
        errors = fn()
        if errors:
            print()
            for e in errors:
                print(f"  ABWEICHUNG: {e}")
        else:
            print("  -> deckungsgleich")
        print()
        all_errors.extend(errors)

    if all_errors:
        print(f"FEHLGESCHLAGEN: {len(all_errors)} Abweichung(en)")
        return 1
    print("OK: Quelle und TEI sind deckungsgleich.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
