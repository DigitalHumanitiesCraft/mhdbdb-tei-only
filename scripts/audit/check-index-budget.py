#!/usr/bin/env python3
"""
Index-Budget-Waechter (#111): meldet, wenn ein vorgebauter Index das
Groessenbudget des Browsers reisst.

Nicht zu verwechseln mit `check-file-sizes.py` (#350). Die beiden messen
verschiedene Dinge und haben verschiedene Gegner:

    check-file-sizes.py   GitHubs 100-MiB-Wand beim Push. Misst JEDE
                          committete Datei, bewusst ohne Pfadfilter, nur
                          die Groesse auf der Platte. Wird rot.
    dieses Skript         Das Budget im Browser. Misst nur data/*.json.gz,
                          dafuer auch die UNKOMPRIMIERTE Groesse, die
                          `git ls-tree` nicht kennt. Warnt nur.

Der Unterschied ist nicht akademisch. `corpus-index.json.gz` liegt bei
42,2 MB auf der Platte und bei 168,3 MB im Speicher des Browsers, sobald
sie entpackt in IndexedDB steht. Fuer GitHub ist die Datei unauffaellig,
fuer ein Notebook mit wenig RAM ist sie es nicht.

## Warum dieses Gate nur warnt

Entscheidung von Chris am 08.08.2026, auf Nachfrage. Eine Ueberschreitung
ist kein Fehler in einem Commit, den man zurueckweisen koennte: der Index
waechst durch Annotationsarbeit, und jedes einzelne Wachstum ist legitim.
Rot faerben wuerde heissen, den naechsten Backfill zu blockieren, bis
jemand ein Splitting gebaut hat. Der Zweck ist deshalb, den Zeitpunkt
nicht zu verpassen, an dem ADR-019 aus der Schublade muss.

Exit 0 gilt also auch bei gerissenem Budget. Rot wird dieser Lauf nur,
wenn die Messung selbst nicht moeglich war (Exit 2), denn dann weiss
niemand mehr, wo der Index steht.

## Warum die Schwellen dort liegen, wo sie liegen

Die beiden Trigger fuer den Korpus-Index stammen aus #111 (12.05.2026)
und sind hier unveraendert uebernommen. Gemessen am 08.08.2026:

    corpus-index.json.gz      42,17 MB gz    168,34 MB roh    Faktor 3,99
    authority-index.json.gz    3,29 MB gz     23,57 MB roh    Faktor 7,17
    naming-index.json.gz       0,11 MB gz      0,80 MB roh    Faktor 7,11

Der Korpus-Index hat damit 7,83 MB gz Kopfraum. Die im Ticket erwarteten
Zuwaechse: POS-Tags aus #27 mit 3 bis 5 MB bleiben auch am oberen Rand
der Schaetzung darunter (47,2), NER aus #109 mit 5 bis 10 MB reisst das
Budget am oberen Rand allein (52,2). Zusammen reissen sie es in JEDER
Kombination, auch beidseitig unten: 3 + 5 sind 8 MB und damit mehr als
der Kopfraum.

Fuer den Authority-Index nennt #111 keine Schwelle. Die hier gesetzte ist
aus seinem eigenen Verlauf abgeleitet und im Bericht als solche kenntlich.

## Einheit

Dezimale MB (1 MB = 1.000.000 Bytes), nicht MiB. Grund: dieses Budget ist
ein Download- und Speicherbudget, und #111 rechnet dezimal ("42 MB gz").
`check-file-sizes.py` rechnet in MiB, weil GitHubs Wand in MiB steht. Die
beiden Skripte sind bei derselben Datei deshalb um 4,9 Prozent
auseinander, und das ist Absicht, kein Rundungsfehler.

## Wie die unkomprimierte Groesse gemessen wird

Streamend dekomprimiert und dabei gezaehlt, ohne die Datei je ganz im
Speicher zu halten. Der naheliegende billige Weg waere das ISIZE-Feld in
den letzten vier Bytes des gzip-Members. Der ist hier bewusst nicht
genommen: ISIZE ist modulo 2^32 und bei mehreren Membern nur das letzte.
Ein Index, der die 4-GB-Grenze reisst, wuerde damit still als winzig
gemeldet, und zwar genau in dem Moment, fuer den dieses Gate gebaut ist.

Usage:
    python scripts/audit/check-index-budget.py             # Bericht + Exit-Code
    python scripts/audit/check-index-budget.py --quiet     # nur Auffaelliges
    python scripts/audit/check-index-budget.py --json      # maschinenlesbar
    python scripts/audit/check-index-budget.py --selftest  # Schwellen und Logik pruefen

Exit codes:
    0 = gemessen (auch bei gerissenem Budget, siehe oben)
    1 = nur bei --selftest: mindestens ein Fall fehlgeschlagen
    2 = Messung nicht moeglich: Verzeichnis oder Datei fehlt, gzip kaputt
"""
import argparse
import gzip
import io
import json
import sys
import zlib
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / 'data'

MB = 1_000_000

# Schwellen je Index, in dezimalen MB. Jede Zeile braucht eine Begruendung:
# eine Zahl ohne Messvorschrift ist in diesem Projekt schon zweimal
# falsch weitergetragen worden.
BUDGETS = {
    'corpus-index.json.gz': {
        'gz': 50,
        'raw': 200,
        'why': (
            "Aus #111 (12.05.2026) unveraendert uebernommen. Bei 50 MB gz "
            "beginnt der erste Seitenaufbau auf schmaler Leitung unzumutbar "
            "zu werden, bei 200 MB roh wird der Entpackschritt auf Geraeten "
            "mit wenig RAM zum Risiko."
        ),
    },
    'authority-index.json.gz': {
        'gz': 8,
        'raw': 60,
        'why': (
            "Nicht aus #111, dort steht keine Schwelle fuer diesen Index. "
            "Abgeleitet aus dem Ist-Stand (3,29 MB gz) mit Raum fuer eine "
            "Verdopplung: der Backfill aus #115 fuellt 977 Lemmata und "
            "225k Varianten-Referenzen nach und ist der groesste absehbare "
            "Zuwachs."
        ),
    },
}

# Fuer alles unter data/*.json.gz, was nicht namentlich oben steht. Das
# sind die kuratierten Zusatzdatensaetze der Rubrik aus #194, ein Index je
# Forschungsabfrage. Wer diese Schwelle reisst, liefert keinen
# Zusatzdatensatz mehr ab, sondern einen zweiten Korpus-Index, und
# braucht eine eigene Zeile in BUDGETS samt Begruendung.
DEFAULT_BUDGET = {
    'gz': 5,
    'raw': 40,
    'why': (
        "Voreinstellung fuer kuratierte Zusatzindexe (#194). Zum Vergleich: "
        "naming-index.json.gz liegt bei 0,11 MB gz."
    ),
}


def budget_for(name):
    return BUDGETS.get(name, DEFAULT_BUDGET)


def raw_size(path, chunk=1 << 20):
    """Unkomprimierte Groesse in Bytes, streamend gezaehlt.

    Bewusst nicht ueber das ISIZE-Feld des gzip-Trailers: das ist modulo
    2^32 und bei mehreren Membern nur das letzte. Siehe Modul-Docstring.
    """
    total = 0
    with gzip.open(path, 'rb') as fh:
        while True:
            block = fh.read(chunk)
            if not block:
                break
            total += len(block)
    return total


def usage(gz_bytes, raw_bytes, budget):
    """Auslastung in Prozent, die hoehere der beiden Achsen.

    Das ist die Zahl, nach der sortiert und gewarnt wird, und nicht der
    Abstand in MB. Der Abstand allein stellt die Rangfolge auf den Kopf:
    der Authority-Index liegt 4,7 MB unter seiner Schwelle und der
    Korpus-Index 7,8 MB, aber der eine ist zu 41 Prozent ausgelastet und
    der andere zu 84.
    """
    return max(100 * gz_bytes / MB / budget['gz'], 100 * raw_bytes / MB / budget['raw'])


def classify(gz_bytes, raw_bytes, budget):
    """'over' sobald eine der beiden Schwellen erreicht ist, sonst 'ok'.

    Erreicht heisst >=, nicht >. Eine Schwelle, die man genau treffen darf,
    ist eine Schwelle, die man auch genau ueberschreiten darf.
    """
    if gz_bytes / MB >= budget['gz'] or raw_bytes / MB >= budget['raw']:
        return 'over'
    return 'ok'


def measure():
    """[(name, gz_bytes, raw_bytes, budget, verdict)] fuer alle data/*.json.gz."""
    if not DATA.is_dir():
        print(f"::error title=Index budget::Verzeichnis nicht gefunden: {DATA}", file=sys.stderr)
        sys.exit(2)

    rows = []
    for path in sorted(DATA.glob('*.json.gz')):
        try:
            gz_bytes = path.stat().st_size
            raw_bytes = raw_size(path)
        # Reihenfolge ist nicht beliebig: gzip.BadGzipFile erbt von OSError.
        # Stuende OSError zuerst, meldete eine kaputte Datei "nicht lesbar"
        # und niemand wuesste, dass das gzip selbst hin ist.
        except (gzip.BadGzipFile, EOFError, zlib.error) as exc:
            print(f"::error file=data/{path.name}::kein lesbares gzip: {exc}", file=sys.stderr)
            sys.exit(2)
        except OSError as exc:
            print(f"::error file=data/{path.name}::nicht lesbar: {exc}", file=sys.stderr)
            sys.exit(2)
        budget = budget_for(path.name)
        rows.append((path.name, gz_bytes, raw_bytes, budget, classify(gz_bytes, raw_bytes, budget)))
    return rows


def selftest():
    """Schwellenlogik an synthetischen Werten, plus ein echtes gzip-Roundtrip."""
    cases = []
    corpus = BUDGETS['corpus-index.json.gz']

    # Der Ist-Stand vom 08.08.2026. Faellt dieser Fall um, hat sich
    # entweder der Index oder die Schwelle bewegt, und beides gehoert
    # gesehen.
    cases.append(("Korpus-Index heute (42,17 / 168,34 MB) ist im Budget",
                  classify(42_165_752, 168_343_630, corpus) == 'ok'))
    cases.append(("50 MB gz reisst das Budget, roh egal",
                  classify(50 * MB, 10 * MB, corpus) == 'over'))
    cases.append(("49,9 MB gz ist noch still",
                  classify(int(49.9 * MB), 10 * MB, corpus) == 'ok'))
    cases.append(("200 MB roh reisst das Budget, gz egal",
                  classify(1 * MB, 200 * MB, corpus) == 'over'))
    cases.append(("199,9 MB roh ist noch still",
                  classify(1 * MB, int(199.9 * MB), corpus) == 'ok'))
    # Genau der Fall aus #111: POS (#27) und NER (#109). Beide Raender der
    # Schaetzung gehoeren geprueft, sonst steht hier die zu bequeme Haelfte.
    cases.append(("POS plus NER auf den heutigen Stand reisst das Budget",
                  classify(42_165_752 + 5 * MB + 10 * MB, 168_343_630, corpus) == 'over'))
    cases.append(("POS allein reisst es auch am oberen Rand nicht (47,2)",
                  classify(42_165_752 + 5 * MB, 168_343_630, corpus) == 'ok'))
    cases.append(("NER allein reisst es am oberen Rand schon (52,2)",
                  classify(42_165_752 + 10 * MB, 168_343_630, corpus) == 'over'))
    cases.append(("NER an der Untergrenze reisst es noch nicht (47,2)",
                  classify(42_165_752 + 5 * MB, 168_343_630, corpus) == 'ok'))
    # Der Fall, der eine zu bequeme Formulierung im Docstring widerlegt
    # hat: beide Schaetzungen an ihrer UNTERGRENZE sind zusammen 8 MB und
    # damit schon mehr als die 7,83 MB Kopfraum.
    cases.append(("POS plus NER reissen es auch beidseitig unten (50,2)",
                  classify(42_165_752 + 3 * MB + 5 * MB, 168_343_630, corpus) == 'over'))

    auth = BUDGETS['authority-index.json.gz']
    cases.append(("Authority-Index heute (3,29 / 23,57 MB) ist im Budget",
                  classify(3_286_114, 23_566_168, auth) == 'ok'))

    # Die Rangfolge-Umkehr, wegen der ueberhaupt in Prozent gerechnet wird
    # (Stand 08.08.2026): der Authority-Index hat weniger MB Luft, der
    # Korpus-Index ist trotzdem der dringendere Fall.
    cases.append(("Korpus-Index hat mehr MB Luft als der Authority-Index",
                  (corpus['gz'] - 42_165_752 / MB) > (auth['gz'] - 3_286_114 / MB)))
    cases.append(("Auslastung dreht die Rangfolge trotzdem zum Korpus-Index",
                  usage(42_165_752, 168_343_630, corpus) > usage(3_286_114, 23_566_168, auth)))
    cases.append(("Auslastung nimmt die hoehere der beiden Achsen",
                  usage(1 * MB, 100 * MB, corpus) == 50.0))
    cases.append(("Volles Budget sind genau 100 Prozent",
                  usage(50 * MB, 0, corpus) == 100.0))

    cases.append(("Unbekannter Index faellt auf die Voreinstellung",
                  budget_for('arthurian-horses-index.json.gz') is DEFAULT_BUDGET))
    cases.append(("Bekannter Index nimmt seine eigene Schwelle",
                  budget_for('corpus-index.json.gz') is corpus))
    cases.append(("Jede Schwelle traegt eine Begruendung",
                  all(b['why'].strip() for b in list(BUDGETS.values()) + [DEFAULT_BUDGET])))

    # Der Fehlermodus, der dieses Skript rechtfertigt: die unkomprimierte
    # Groesse wird falsch gemessen und ein gerissenes Budget bleibt still.
    # Deshalb der Roundtrip gegen echtes gzip statt gegen ISIZE.
    import tempfile
    payload = b'{"x":' + b'0' * 5_000_000 + b'}'
    with tempfile.TemporaryDirectory() as tmp:
        probe = Path(tmp) / 'probe.json.gz'
        with gzip.open(probe, 'wb') as fh:
            fh.write(payload)
        measured = raw_size(probe)
        cases.append((f"Streaming-Messung trifft die rohe Groesse ({measured:,} B)",
                      measured == len(payload)))
        cases.append(("Die rohe Groesse ist um ein Vielfaches groesser als die gz-Groesse",
                      measured > probe.stat().st_size * 10))

    failed = [name for name, ok in cases if not ok]
    for name, ok in cases:
        print(f"  {'OK  ' if ok else 'FAIL'}  {name}")
    if failed:
        print(f"\nSelbsttest fehlgeschlagen: {len(failed)} von {len(cases)}", file=sys.stderr)
        return 1
    print(f"\nSelbsttest bestanden: {len(cases)} Faelle")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="Index-Budget-Waechter (#111). Warnt, faerbt den Lauf aber nicht rot.")
    parser.add_argument('--quiet', action='store_true', help="Nur Auffaelliges ausgeben.")
    parser.add_argument('--json', action='store_true', dest='as_json', help="Maschinenlesbare Ausgabe.")
    parser.add_argument('--selftest', action='store_true', help="Schwellen und Messlogik pruefen.")
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    rows = measure()
    if not rows:
        print(f"::error title=Index budget::Keine data/*.json.gz gefunden unter {DATA}", file=sys.stderr)
        return 2

    if args.as_json:
        print(json.dumps({
            'unit': 'decimal MB (1 MB = 1e6 bytes)',
            'indexes': [
                {
                    'file': f'data/{name}',
                    'gzBytes': gz,
                    'rawBytes': raw,
                    'gzMB': round(gz / MB, 2),
                    'rawMB': round(raw / MB, 2),
                    'budgetGzMB': budget['gz'],
                    'budgetRawMB': budget['raw'],
                    'verdict': verdict,
                }
                for name, gz, raw, budget, verdict in rows
            ],
        }, indent=2, ensure_ascii=False))
        return 0

    over = [r for r in rows if r[4] == 'over']

    for name, gz, raw, budget, verdict in over:
        print(
            f"::warning file=data/{name}::{gz / MB:.2f} MB gz / {raw / MB:.2f} MB roh "
            f"erreicht das Budget ({budget['gz']} MB gz / {budget['raw']} MB roh). "
            f"Zeit fuer ADR-019 (#111): der Index gehoert aufgeteilt oder ein Feld muss raus. "
            f"Dieser Lauf bleibt absichtlich gruen."
        )

    if not args.quiet or over:
        print(f"Index-Budget (#111), dezimale MB, gemessen an {DATA.relative_to(REPO)}:")
        print()
        print(f"  {'Datei':<28} {'gz':>9} {'roh':>10} {'Faktor':>7}  {'Budget':>13}  {'Ausl.':>6}  Status")
        for name, gz, raw, budget, verdict in rows:
            ratio = raw / gz if gz else 0
            print(
                f"  {name:<28} {gz / MB:>6.2f} MB {raw / MB:>7.2f} MB {ratio:>6.2f}x  "
                f"{budget['gz']:>3} / {budget['raw']:<3} MB  "
                f"{usage(gz, raw, budget):>5.0f}%  "
                f"{'REISST' if verdict == 'over' else 'ok'}"
            )
        print()
        total_gz = sum(r[1] for r in rows)
        total_raw = sum(r[2] for r in rows)
        print(f"  Summe aller Indexe: {total_gz / MB:.2f} MB gz, {total_raw / MB:.2f} MB roh.")
        print(f"  (Kein eigenes Budget: niemand laedt alle Indexe, die Rubrik aus #194 laedt je Abfrage.)")

        if over:
            print()
            print(f"  {len(over)} Index/Indexe ueber Budget. Siehe docs/DECISIONS.md, ADR-019.")
        elif not args.quiet:
            head = max(rows, key=lambda r: usage(r[1], r[2], r[3]))
            name, gz, raw, budget, _ = head
            print(f"  Am naechsten am Budget: data/{name} bei "
                  f"{usage(gz, raw, budget):.0f} Prozent Auslastung, "
                  f"noch {budget['gz'] - gz / MB:.2f} MB gz und "
                  f"{budget['raw'] - raw / MB:.2f} MB roh Luft.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
