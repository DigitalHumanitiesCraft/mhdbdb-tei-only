#!/usr/bin/env python3
"""#309: Wie stark verzerrt die ungleiche Annotationsabdeckung die pro-1000-Raten?

Hintergrund: alle normierten Groessen der Analyse-Werkzeuge teilen durch
`text.wordCount`, also durch die Zahl der <w> mit @lemmaRef (CONTRACTS §B).
Wie weit diese Zahl hinter der tatsaechlichen Textlaenge zurueckbleibt, misst
`quantify-unannotated-tokens.py`. Dieses Skript beantwortet die Anschlussfrage:
verzerrt der Unterschied die Raten, und in welche Richtung?

Die Frage ist nicht trivial, weil beide Seiten betroffen sind. Fehlt Annotation
gleichmaessig ueber alle Lemmata, kuerzt sich der Effekt exakt weg. Beim
korpusweiten Hapax-Werkzeug wird sogar der Zaehler mitgedrueckt: eine
unannotierte seltene Form ist als Raritaet unsichtbar. Welcher Effekt gewinnt,
ist empirisch.

Gemessen wird die Hapax-Rate pro Text (Raritaeten je 1000 annotierte Tokens,
wie in hapax-legomena.js, Tab "Beitrag pro Text") gegen die Abdeckung aus dem
CSV von quantify-unannotated-tokens.py. Der Laengen-Confound wird kontrolliert,
weil die Rate aus denselben Gruenden laengenabhaengig sein koennte wie die
Type-Token-Ratio (CONTRACTS §H.5 Punkt 1).

Wichtig fuer die Interpretation: das Ergebnis ist eine Beobachtungskorrelation.
Die Abdeckung ist im Korpus nicht zufaellig verteilt (Gattung, Ingest-Aera,
Vers gegen Prosa), ein Gattungs-Confound ist also nicht ausgeschlossen. Die
mechanistische Herleitung steht in CONTRACTS §H.5 Punkt 0 und ist exakt; diese
Messung stuetzt sie, ersetzt sie aber nicht.

Usage:
    python scripts/audit/quantify-unannotated-tokens.py --out-dir <dir>
    python scripts/audit/coverage-bias-check.py --coverage-csv <dir>/189-unannotated-per-text.csv

Read-only, keine Korpus- oder Index-Aenderung.
"""
import argparse
import csv
import gzip
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# Texte unter dieser Groesse liefern instabile Raten (eine einzige Raritaet
# schlaegt in einem 200-Token-Fragment mit 5 pro 1000 durch).
MIN_TOKENS = 1000


def pearson(a, b):
    ma, mb = statistics.mean(a), statistics.mean(b)
    num = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    den = (sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b)) ** 0.5
    return num / den if den else 0.0


def ranks(values):
    """Raenge ohne Bindungskorrektur. Bei 345 stetigen Messwerten sind Bindungen
    selten genug, dass die Vereinfachung die dritte Nachkommastelle nicht traegt."""
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = [0.0] * len(values)
    for pos, i in enumerate(order):
        out[i] = pos
    return out


def spearman(a, b):
    return pearson(ranks(a), ranks(b))


def quartile_medians(pairs):
    """pairs: (coverage, rate). Liefert (Median unterstes Cov-Quartil, oberstes)."""
    ordered = sorted(pairs)
    q = max(1, len(ordered) // 4)
    return (statistics.median(p[1] for p in ordered[:q]),
            statistics.median(p[1] for p in ordered[-q:]))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('--coverage-csv', required=True,
                    help='189-unannotated-per-text.csv aus quantify-unannotated-tokens.py')
    ap.add_argument('--max-freq', type=int, default=1,
                    help='Raritaets-Schwelle: korpusweite Gesamtfrequenz <= n (default 1 = Hapax)')
    args = ap.parse_args()

    index_path = PROJECT_ROOT / 'data' / 'corpus-index.json.gz'
    with gzip.open(index_path, 'rt', encoding='utf-8') as fh:
        index = json.load(fh)
    texts = index['texts']
    print(f"Corpus-Index v{index.get('version')}, {len(texts)} Texte")

    # Korpusweite Gesamtfrequenz je Lemma, wie hapax-legomena.js sie bildet:
    # Summe der Positionslisten ueber alle Texte.
    total = Counter()
    for t in texts:
        for lemma_id, positions in (t.get('lemmata') or {}).items():
            total[lemma_id] += len(positions)
    rare = {lid for lid, n in total.items() if n <= args.max_freq}
    print(f"Raritaeten (Gesamtfrequenz <= {args.max_freq}): {len(rare):,} Lemmata")

    coverage = {}
    with Path(args.coverage_csv).open(encoding='utf-8-sig') as fh:
        for row in csv.DictReader(fh, delimiter=';'):
            coverage[row['sigle']] = float(row['coverage_prozent'])

    rows = []   # (coverage, wordCount, rate)
    for t in texts:
        wc = t.get('wordCount') or 0
        if wc < MIN_TOKENS or t['id'] not in coverage:
            continue
        hits = sum(1 for lid in (t.get('lemmata') or {}) if lid in rare)
        rows.append((coverage[t['id']], wc, hits / wc * 1000))

    print(f"ausgewertet: {len(rows)} Texte (ab {MIN_TOKENS} annotierten Tokens, Abdeckung bekannt)")
    if len(rows) < 20:
        print('zu wenige Texte fuer eine Aussage')
        return 1

    cov = [r[0] for r in rows]
    length = [r[1] for r in rows]
    rate = [r[2] for r in rows]

    print()
    print(f"  Spearman Abdeckung ~ Rate    {spearman(cov, rate):+.3f}")
    print(f"  Spearman Abdeckung ~ Laenge  {spearman(cov, length):+.3f}")
    print(f"  Spearman Laenge ~ Rate       {spearman(length, rate):+.3f}   <- Laengen-Confound?")

    lo, hi = quartile_medians([(c, y) for c, y in zip(cov, rate)])
    print(f"  Median Rate unterstes Abdeckungsquartil {lo:.2f} gegen oberstes {hi:.2f}")

    print()
    print('  nach Laengen-Terzil getrennt (kontrolliert den Laengen-Confound):')
    by_length = sorted(rows, key=lambda r: r[1])
    k = len(by_length) // 3
    for name, group in (('kurz', by_length[:k]),
                        ('mittel', by_length[k:2 * k]),
                        ('lang', by_length[2 * k:])):
        gc = [r[0] for r in group]
        gy = [r[2] for r in group]
        glo, ghi = quartile_medians([(c, y) for c, y in zip(gc, gy)])
        print(f"    {name:7s} n={len(group):3d}  Spearman {spearman(gc, gy):+.3f}  "
              f"Median unterstes Quartil {glo:.2f} gegen oberstes {ghi:.2f}")

    print()
    print('  Lesart: ein negativer Wert heisst, dass schwaecher annotierte Texte')
    print('  hoehere Raten zeigen, der Nenner-Effekt also den Zaehler-Effekt')
    print('  ueberwiegt. Beobachtungskorrelation, kein Kausalnachweis: die')
    print('  Abdeckung haengt im Korpus an Gattung und Ingest-Aera.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
