#!/usr/bin/env python3
"""#189: Korpusweite Quantifizierung unannotierter Wortformen (Diagnose, read-only).

Hintergrund: Wortformen ohne @lemmaRef (und meist ohne @pos) sind fuer alle
Lemma-Features unsichtbar (GWTK-Pilotfall rott/rotten/rotte, jungen/junger).
Dieses Skript vermisst den Bestand und baut eine Priorisierungsliste:

1. Pro Text: annotierte vs. unannotierte <w> im <body> (Coverage).
2. Korpusweit: unannotierte Oberflaechenformen aggregiert (MHG-normalisiert).
3. Ambiguitaets-Flag: Formen, die zugleich als annotierte Schreibform im
   Korpus vorkommen (= Homograph eines existierenden Lemmas) — genau die
   Faelle, in denen das Alt-System mutmasslich bewusst NICHT annotiert hat.

Output: CSV-Reports + Konsolen-Summary. Keine Korpus-Aenderung.

Usage:
    python scripts/audit/quantify-unannotated-tokens.py [--out-dir <dir>] [--top 50]
"""
import argparse
import csv
import io
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
from mhg_normalizer import normalize_mhg  # noqa: E402
from corpus_files import corpus_files  # noqa: E402

# Konvention in scripts/audit/ (#329): Windows-Konsolen laufen auf cp1252,
# und Audit-Skripte geben Korpus- und Lexikonformen aus. Die MHG-Breven ŏ
# und ŭ liegen ausserhalb von cp1252, ein Treffer wuerde das Skript also an
# seiner eigenen Ausgabe toeten. Der Wrapper steht deshalb einheitlich in
# allen Skripten, die etwas ausgeben, statt pro Datei abgewogen zu werden.
# Er deckt nur stdout; wer ueber stderr meldet, braucht ihn dort ebenso.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TEI = '{http://www.tei-c.org/ns/1.0}'


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--out-dir', default=str(PROJECT_ROOT / 'data' / 'audit'))
    ap.add_argument('--top', type=int, default=50)
    args = ap.parse_args()

    per_text = []                      # (sigle, total_w, unannot, coverage)
    unannot_forms = Counter()          # normalized form -> count
    unannot_form_texts = defaultdict(set)
    unannot_examples = {}              # normalized form -> ein Original-Beispiel
    annotated_forms = set()            # normalisierte Formen MIT lemmaRef

    files = corpus_files()
    for i, fp in enumerate(files):
        if (i + 1) % 100 == 0:
            print(f'  {i + 1}/{len(files)}...', flush=True)
        sigle = fp.name.replace('.tei.xml', '')
        tree = etree.parse(str(fp))
        body = tree.find(f'.//{TEI}body')
        if body is None:
            continue
        total = unannot = 0
        for w in body.iter(f'{TEI}w'):
            form = ''.join(w.itertext()).strip()
            if not form:
                continue
            total += 1
            norm = normalize_mhg(form.lower())
            if w.get('lemmaRef'):
                annotated_forms.add(norm)
            else:
                unannot += 1
                unannot_forms[norm] += 1
                unannot_form_texts[norm].add(sigle)
                unannot_examples.setdefault(norm, form)
        coverage = (total - unannot) / total * 100 if total else 100.0
        per_text.append((sigle, total, unannot, coverage))

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    per_text.sort(key=lambda r: r[2], reverse=True)
    with open(out_dir / '189-unannotated-per-text.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['sigle', 'tokens_w_gesamt', 'unannotiert', 'coverage_prozent'])
        for sigle, total, unannot, cov in per_text:
            w.writerow([sigle, total, unannot, f'{cov:.2f}'])

    with open(out_dir / '189-unannotated-forms.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';')
        w.writerow(['form_normalisiert', 'beispiel_original', 'vorkommen',
                    'texte', 'homograph_zu_annotierter_form'])
        for norm, count in unannot_forms.most_common():
            w.writerow([norm, unannot_examples[norm], count,
                        len(unannot_form_texts[norm]),
                        'ja' if norm in annotated_forms else 'nein'])

    total_w = sum(r[1] for r in per_text)
    total_un = sum(r[2] for r in per_text)
    ambig = [(n, c) for n, c in unannot_forms.most_common() if n in annotated_forms]
    print(f'\n<w>-Tokens gesamt: {total_w:,} | unannotiert: {total_un:,} '
          f'({total_un / total_w * 100:.2f} %) | unannotierte Formen (Types): {len(unannot_forms):,}')
    print(f'Davon homograph zu annotierten Formen: {len(ambig):,} Types, '
          f'{sum(c for _, c in ambig):,} Tokens — die Priorisierungskandidaten (#189)')
    print(f'\nTop {args.top} ambige Formen (Vorkommen):')
    for norm, count in ambig[:args.top]:
        print(f'  {count:>7,}  {unannot_examples[norm]}  ({len(unannot_form_texts[norm])} Texte)')
    print(f'\nTop 15 Texte nach unannotierten Tokens:')
    for sigle, total, unannot, cov in per_text[:15]:
        print(f'  {unannot:>8,}  {sigle:<6} (Coverage {cov:.1f} %)')
    print(f'\nReports: {out_dir}')
    return 0


if __name__ == '__main__':
    sys.exit(main())
