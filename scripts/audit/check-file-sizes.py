#!/usr/bin/env python3
"""
Größenwächter (#350): keine committete Datei darf GitHubs harte 100-MiB-Wand erreichen.

GitHub blockiert Dateien über 100 MiB beim Push ("GitHub blocks files larger
than 100 MiB") und warnt ab 50 MiB. Das ist die einzige Größengrenze mit
Zähnen: die Repo-Größe selbst kennt nur eine Empfehlung (unter 1 GB ideal,
unter 5 GB dringend empfohlen), und die einzige Konsequenz bei Überschreitung
ist laut Doku eine Mail vom Support.

Gemessen am 04.08.2026: `tei/OVG.tei.xml` liegt bei 62,9 MiB und ist die
einzige Datei über der 50-MiB-Warnschwelle. In der History stand sie schon
bei 79,7 MiB. Annotationsarbeit lässt TEI-Dateien wachsen, ohne dass jemand
auf die Dateigröße schaut: ein Backfill über @lemmaRef oder @pos kann OVG
zweistellig in Prozent wachsen lassen.

## Warum die Schwelle bei 90 MiB liegt und nicht bei 100

Dieses Gate kann einen abgelehnten Push nicht verhindern. GitHub weist den
Push zurück, bevor irgendein Workflow startet, und dann existiert der Commit
bereits lokal. Der Zweck ist deshalb Vorwarnung, nicht Abwehr: bei 90 MiB
schlägt das Gate an, solange der Push noch durchgeht und die Datei sich noch
geordnet aufteilen lässt. Wer erst bei 100 MiB warnt, warnt nie.

Der eigentliche Rettungsanker ist der lokale Lauf vor dem Push:

    python scripts/audit/check-file-sizes.py

## Was gemessen wird

Der HEAD-Baum, nicht jeder Blob eines Pushes. GitHub prüft jeden Blob im
Pack, also auch einen, der nur in einem Zwischencommit zu groß war und im
Endstand wieder klein ist. Dieser Fall bleibt hier unsichtbar. Für die
Vorwarnfunktion ist das die richtige Auflösung: die Frage lautet nicht
"war eine Datei je zu groß", sondern "wie nah ist der aktuelle Stand an
der Wand".

## Warum ohne Pfadfilter

Der Workflow file-size-check.yml trägt bewusst keine `paths:`-Liste. Eine
Datei kann in jedem Verzeichnis zu groß werden, und ein Wächter, der vorher
entscheiden muss, welcher Ordner wachsen darf, hat dieselbe Grenzziehung am
Hals, die sich dieses Projekt beim Em-Dash-Gate schon einmal abgewöhnt hat.
Der Lauf kostet Sekunden, weil `git ls-tree` die Größen mitliefert und keine
Datei gelesen werden muss.

## Selbsttest

Dieses Gate wird jahrelang grün sein: der Abstand zur Schwelle beträgt heute
27 MiB. Ein Gate, das immer grün ist, sagt nichts, solange niemand den Fehler
einbaut, den es fangen soll (JOURNAL zum 31.07.). Deshalb sind Parser und
Klassifikation getrennt und werden an synthetischen Eingaben belegt:

    python scripts/audit/check-file-sizes.py --selftest

Usage:
    python scripts/audit/check-file-sizes.py             # Bericht + Exit-Code
    python scripts/audit/check-file-sizes.py --quiet     # nur Exit-Code bei Erfolg
    python scripts/audit/check-file-sizes.py --selftest  # Parser und Schwellen prüfen

Exit codes:
    0 = alle Dateien unter der Fail-Schwelle (Warnungen sind grün)
    1 = mindestens eine Datei ab 90 MiB
    2 = git nicht lesbar oder unerwartetes ls-tree-Format
"""
import argparse
import io
import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parents[2]

MIB = 1024 * 1024

# GitHubs harte Grenze. Steht hier nur als Bezugspunkt fuer den Bericht,
# geprueft wird gegen FAIL_MIB.
GITHUB_BLOCK_MIB = 100
# Ab hier rot: 10 MiB Puffer, damit der Push noch durchgeht, waehrend man
# die Datei aufteilt.
FAIL_MIB = 90
# Ab hier ein Hinweis im Log, ohne den Lauf zu faerben. GitHubs eigene
# Warnschwelle liegt bei 50 MiB; die waere hier Dauerrauschen, weil OVG
# permanent darueber liegt. 75 MiB ist der Punkt, ab dem ein Splitting-Plan
# auf den Tisch gehoert.
WARN_MIB = 75


def parse_ls_tree(text):
    """`git ls-tree -r -l -z HEAD`-Ausgabe zu [(size_bytes, path)].

    Format je Eintrag:  <mode> SP <type> SP <sha> SP* <size> TAB <path>
    Eintraege sind NUL-getrennt, nicht zeilengetrennt. Das ist der Grund
    fuer -z: ohne den Schalter escapt git Pfade mit Nicht-ASCII zu
    "tei/M\\303\\244rchen.xml", und dieser gequotete String landete dann in
    der ::warning-Annotation, wo er auf keine Datei zeigt (Review 1). Mit -z
    liefert git den Pfad roh, inklusive Umlauten und Zeilenumbruechen.
    Nicht-Blobs (Submodule) tragen '-' als Groesse und fallen raus.
    """
    out = []
    for line in text.split('\0'):
        if not line.strip():
            continue
        meta, _, path = line.partition('\t')
        if not path:
            raise ValueError(f"Kein Tab-Trenner in ls-tree-Zeile: {line!r}")
        fields = meta.split()
        if len(fields) != 4:
            raise ValueError(f"Unerwartetes ls-tree-Format: {line!r}")
        _mode, objtype, _sha, size = fields
        if objtype != 'blob' or size == '-':
            continue
        out.append((int(size), path))
    return out


def classify(size_bytes):
    """'fail' ab FAIL_MIB, 'warn' ab WARN_MIB, sonst 'ok'."""
    mib = size_bytes / MIB
    if mib >= FAIL_MIB:
        return 'fail'
    if mib >= WARN_MIB:
        return 'warn'
    return 'ok'


def tracked_blobs():
    try:
        res = subprocess.run(
            ['git', 'ls-tree', '-r', '-l', '-z', 'HEAD'],
            cwd=REPO, capture_output=True, text=True, encoding='utf-8', check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"::error title=File size audit::git ls-tree nicht lesbar: {exc}", file=sys.stderr)
        sys.exit(2)
    try:
        return parse_ls_tree(res.stdout)
    except ValueError as exc:
        print(f"::error title=File size audit::{exc}", file=sys.stderr)
        sys.exit(2)


def selftest():
    """Parser und Schwellen an synthetischen Eingaben, nicht an echten Dateien."""
    cases = []

    sample = (
        "100644 blob 4c0d84416a91ccb6b8929b372c4a3a265ae2c1fb 65931062\ttei/OVG.tei.xml\0"
        "100644 blob df1a16c1b686bc5b3ff1b9cdf787bf0f854b5efb 47375833\ttei/PL1.tei.xml\0"
        "160000 commit 0000000000000000000000000000000000000000       -\tvendor/sub\0"
        "100644 blob 0000000000000000000000000000000000000000      42\tpfad mit leerzeichen.txt\0"
        # Mit -z liefert git Umlaute roh statt als "M\303\244rchen" (Review 1).
        "100644 blob 0000000000000000000000000000000000000000      17\ttei/Märchen.xml\0"
    )
    parsed = parse_ls_tree(sample)
    cases.append((
        "Parser liest Blobs und ueberspringt Submodule",
        parsed == [
            (65931062, 'tei/OVG.tei.xml'),
            (47375833, 'tei/PL1.tei.xml'),
            (42, 'pfad mit leerzeichen.txt'),
            (17, 'tei/Märchen.xml'),
        ],
    ))
    cases.append(("Parser haelt Leerzeichen im Pfad zusammen", parsed[2][1] == 'pfad mit leerzeichen.txt'))
    cases.append(("Nicht-ASCII-Pfad bleibt unversehrt fuer die Annotation", parsed[3][1] == 'tei/Märchen.xml'))
    cases.append(("Parser vertraegt leere Eintraege", parse_ls_tree("\0\0") == []))

    # Die beiden Fehlermodi, die dieses Skript rechtfertigen: eine Datei
    # waechst ueber die Schwelle, und eine Formataenderung wird still
    # durchgewunken.
    cases.append(("89,9 MiB warnt, ist aber noch nicht rot", classify(int(89.9 * MIB)) == 'warn'))
    cases.append(("genau 90 MiB ist rot", classify(FAIL_MIB * MIB) == 'fail'))
    cases.append(("95 MiB ist rot", classify(95 * MIB) == 'fail'))
    cases.append(("75 MiB warnt", classify(WARN_MIB * MIB) == 'warn'))
    cases.append(("74,9 MiB ist still", classify(int(74.9 * MIB)) == 'ok'))
    cases.append(("OVG heute (62,9 MiB) ist still", classify(65931062) == 'ok'))
    cases.append(("Schwellen liegen unter GitHubs Wand", FAIL_MIB < GITHUB_BLOCK_MIB and WARN_MIB < FAIL_MIB))

    for bad in ("100644 blob abc 42 kein-tab.txt", "100644 blob 42\tzu-wenig-felder.txt"):
        try:
            parse_ls_tree(bad)
            ok = False
        except ValueError:
            ok = True
        cases.append((f"Formatdrift wirft statt durchzuwinken: {bad[:32]}...", ok))

    failed = [name for name, ok in cases if not ok]
    for name, ok in cases:
        print(f"  {'OK  ' if ok else 'FAIL'}  {name}")
    if failed:
        print(f"\nSelbsttest fehlgeschlagen: {len(failed)} von {len(cases)}", file=sys.stderr)
        return 1
    print(f"\nSelbsttest bestanden: {len(cases)} Faelle")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Groessenwaechter gegen GitHubs 100-MiB-Wand (#350).")
    parser.add_argument('--quiet', action='store_true', help="Keine Ausgabe bei Erfolg (nur Exit-Code).")
    parser.add_argument('--selftest', action='store_true', help="Parser und Schwellen an synthetischen Eingaben pruefen.")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    blobs = tracked_blobs()
    if not blobs:
        print("::error title=File size audit::git ls-tree lieferte keine Blobs.", file=sys.stderr)
        return 2

    fails = sorted((s, p) for s, p in blobs if classify(s) == 'fail')
    warns = sorted((s, p) for s, p in blobs if classify(s) == 'warn')

    for size, path in warns:
        print(
            f"::warning file={path}::{size / MIB:.1f} MiB. Ab {FAIL_MIB} MiB ist dieser Lauf rot, "
            f"ab {GITHUB_BLOCK_MIB} MiB lehnt GitHub den Push ab. Zeit fuer einen Splitting-Plan."
        )

    if fails:
        print("Dateien ab der Fail-Schwelle:", file=sys.stderr)
        for size, path in fails:
            print(f"  {size / MIB:6.1f} MiB  {path}", file=sys.stderr)
            print(
                f"::error file={path}::{size / MIB:.1f} MiB liegt ueber der Schwelle von {FAIL_MIB} MiB. "
                f"GitHub blockiert den Push ab {GITHUB_BLOCK_MIB} MiB. Die Datei muss aufgeteilt werden, "
                f"solange der Push noch durchgeht.",
                file=sys.stderr,
            )
        print("", file=sys.stderr)
        print("Der Puffer ist Absicht: ab 100 MiB laesst sich nichts mehr pushen, auch kein Fix.", file=sys.stderr)
        return 1

    if not args.quiet:
        largest = max(blobs)
        print(f"Alle {len(blobs)} committeten Dateien unter {FAIL_MIB} MiB.")
        print(f"  groesste:  {largest[0] / MIB:.1f} MiB  {largest[1]}")
        print(f"  Abstand zur Fail-Schwelle:      {FAIL_MIB - largest[0] / MIB:.1f} MiB")
        print(f"  Abstand zu GitHubs harter Wand: {GITHUB_BLOCK_MIB - largest[0] / MIB:.1f} MiB")
        if warns:
            print(f"  {len(warns)} Datei(en) ueber der Warnschwelle von {WARN_MIB} MiB, siehe oben.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
