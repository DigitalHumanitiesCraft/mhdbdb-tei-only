#!/usr/bin/env python3
"""Gate: eine Aenderung darf keine bestehende variants-Zuordnung still umschlagen lassen (#378, ADR-021).

`variants` im Authority-Index bildet eine normalisierte Schreibform auf ein
Lemma ab (bei mehreren Kandidaten: den ersten nach Vorschrift B). Dieses Gate
vergleicht die Abbildung des committeten Index mit der der Base und meldet jede
Form, die in beiden steht und auf ein anderes Lemma zeigt ("umgeklappt").
Belegfall #367: ein einziges umannotiertes Token gab lemma_7338 die Form
`woren` gegen 111 Verbbelege, und kein Gate schlug an.

Regeln:
  - Eine umgeklappte Form macht den Lauf rot, ausser eine Quittung deckt genau
    diesen Uebergang ab: scripts/audit/variants-flips-ack.json
    {"from": <Base-Version>, "to": <Head-Version>, "flips": <Anzahl>, "reason": ...}.
    Die Quittung gilt nur fuer das Versionspaar und nur mit genau der gemessenen
    Anzahl; beim naechsten Bump ist sie von selbst wirkungslos und muss nicht
    gepflegt werden. .gitignore schliesst scripts/audit/*.json aus (wie bei den
    Baselines): ein neuer Stand wird mit `git add -f` aufgenommen.
  - Neue und entfallene Formen sind erwartbar und werden nur gezaehlt.
  - Invariante des Head: fuer jede Form in variantCandidates ist
    variants[Form] der erste Kandidat. Verletzung ist immer rot.

Usage:
    python scripts/audit/check-variants-flips.py --base <git-rev>

Exit codes:
    0 = keine Umklappung, oder durch Quittung gedeckt
    1 = ungedeckte Umklappung, oder Invariante verletzt
    2 = Vorbedingung verletzt (Base nicht aufloesbar, Index nicht lesbar)
"""
import argparse
import gzip
import io
import json
import subprocess
import sys
from pathlib import Path

# Konvention in scripts/audit/ (#329): Windows-Konsolen laufen auf cp1252.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
INDEX = 'data/authority-index.json.gz'
ACK = PROJECT_ROOT / 'scripts' / 'audit' / 'variants-flips-ack.json'
SHOW_MAX = 20


def load_head():
    return json.loads(gzip.decompress((PROJECT_ROOT / INDEX).read_bytes()))


def load_base(rev):
    probe = subprocess.run(['git', 'rev-parse', '--verify', f'{rev}^{{commit}}'],
                           cwd=PROJECT_ROOT, capture_output=True, text=True)
    if probe.returncode != 0:
        print(f'::error title=Variants-Flip-Gate::Base "{rev}" ist lokal nicht aufloesbar.')
        sys.exit(2)
    blob = subprocess.run(['git', 'show', f'{probe.stdout.strip()}:{INDEX}'],
                          cwd=PROJECT_ROOT, capture_output=True)
    if blob.returncode != 0:
        return None
    return json.loads(gzip.decompress(blob.stdout))


def check(base, head):
    """Return (flips, added, removed, invariant_violations) fuer zwei Indexe."""
    b, h = base['variants'], head['variants']
    flips = sorted((f, b[f], h[f]) for f in b.keys() & h.keys() if b[f] != h[f])
    added = len(h.keys() - b.keys())
    removed = len(b.keys() - h.keys())
    cand = head.get('variantCandidates', {})
    violations = sorted(f for f, ids in cand.items() if not ids or h.get(f) != ids[0])
    return flips, added, removed, violations


def acked(base_version, head_version, n_flips):
    if not ACK.exists():
        return False
    ack = json.loads(ACK.read_text(encoding='utf-8'))
    return (ack.get('from') == base_version and ack.get('to') == head_version
            and ack.get('flips') == n_flips and bool(ack.get('reason')))


def main():
    parser = argparse.ArgumentParser(description='Umgeklappte variants-Zuordnungen erkennen (#378).')
    parser.add_argument('--base', required=True, help='Git-Rev des Vergleichsstands (z.B. origin/main)')
    args = parser.parse_args()

    head = load_head()
    base = load_base(args.base)
    if base is None:
        print(f'{INDEX}: in Base nicht vorhanden (neue Datei) - OK')
        return 0

    flips, added, removed, violations = check(base, head)
    bv, hv = base.get('version'), head.get('version')
    print(f'variants {bv} -> {hv}: {len(head["variants"]):,} Formen im Head '
          f'({len(base["variants"]):,} in der Base), neu {added:,}, entfallen {removed:,}, '
          f'umgeklappt {len(flips):,}')

    failed = False
    if violations:
        failed = True
        print(f'::error file={INDEX}::{len(violations)} Formen mit variantCandidates, deren '
              f'variants-Wert nicht der erste Kandidat ist, z.B. {violations[:5]}')

    if flips:
        for form, old, new in flips[:SHOW_MAX]:
            print(f'  {form}: {old} -> {new}')
        if len(flips) > SHOW_MAX:
            print(f'  ... +{len(flips) - SHOW_MAX:,} weitere')
        if acked(bv, hv, len(flips)):
            print(f'Quittung {ACK.name} deckt {len(flips):,} Umklappungen ({bv} -> {hv}) - OK')
        else:
            failed = True
            print(f'::error file={INDEX}::{len(flips):,} bestehende variants-Zuordnungen sind '
                  f'umgeklappt ({bv} -> {hv}). Pruefen, ob jede gewollt ist (ADR-021: Vorschrift B); '
                  f'dann scripts/audit/variants-flips-ack.json mit from, to, flips und reason '
                  f'schreiben, sonst die Ursache beheben.')
    elif not failed:
        print('Keine Umklappung - OK')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
