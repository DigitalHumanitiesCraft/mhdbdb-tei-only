#!/usr/bin/env python3
"""Korpus- und Authority-File-Zaehlungen aus den Daten extrahieren und mit
den in der Doku verankerten Zahlen abgleichen.

Hintergrund: bei jeder Korpus-Aenderung (z.B. WZB-Aufnahme 2026-05-08
hat das Korpus von 666 auf 667 Dateien gebracht) muessen mehrere Stellen
in docs/TEI-MODEL.md, docs/INDEX.md und docs/ROADMAP.md mitwandern,
sonst driftet die Doku schnell. Dieser Audit zeigt den aktuellen Stand
plus die Stellen in den Docs, wo die Zahlen NICHT mehr stimmen.

Es ist explizit kein Auto-Fixer: das Script meldet Drift, aendert aber
keine Doku. Die Begruendung ("WZB +1") gehoert in den Commit, nicht in
eine generische Markdown-Edit.

Usage:
    python scripts/audit/doc-count-audit.py             # default: full report
    python scripts/audit/doc-count-audit.py --check     # exit non-zero bei drift
"""
import argparse
import glob
import io
import re
import sys
from pathlib import Path
from lxml import etree

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)


def count_xml_elements(path: str, xpath: str) -> int:
    """Count elements matching xpath in path (TEI namespace assumed)."""
    tree = etree.parse(path)
    return len(tree.xpath(xpath, namespaces={'tei': 'http://www.tei-c.org/ns/1.0'}))


def collect_counts() -> dict:
    counts = {}
    counts['corpus_files'] = len(glob.glob('tei/*.tei.xml'))
    counts['authority_files'] = len(glob.glob('authority-files/*.xml'))
    counts['lexicon_entries'] = count_xml_elements('authority-files/lexicon.xml', '//tei:entry[@xml:id]')
    counts['variants_entries'] = count_xml_elements('authority-files/variants.xml', '//tei:entry[@corresp]')
    counts['variants_forms'] = count_xml_elements('authority-files/variants.xml', '//tei:form[@xml:id]')
    counts['persons'] = count_xml_elements('authority-files/persons.xml', '//tei:person[@xml:id]')
    counts['works'] = count_xml_elements('authority-files/works.xml', '//tei:bibl[@xml:id]')
    counts['concepts'] = count_xml_elements('authority-files/concepts.xml', '//tei:category[@xml:id]')
    counts['genres'] = count_xml_elements('authority-files/genres.xml', '//tei:category[@xml:id]')
    counts['names'] = count_xml_elements('authority-files/names.xml', '//tei:category[@xml:id]')
    counts['contributors_persons'] = count_xml_elements('authority-files/contributors.xml', '//tei:person[@xml:id]')
    counts['contributors_orgs'] = count_xml_elements('authority-files/contributors.xml', '//tei:org[@xml:id]')
    return counts


# (label, key, formatted-as-found-in-docs)
LABELS = [
    ('Korpus-Dateien (tei/)', 'corpus_files'),
    ('Authority-Dateien (authority-files/)', 'authority_files'),
    ('lexicon.xml — Lemmata', 'lexicon_entries'),
    ('variants.xml — Eintraege', 'variants_entries'),
    ('variants.xml — Formen', 'variants_forms'),
    ('persons.xml — Personen', 'persons'),
    ('works.xml — Werke', 'works'),
    ('concepts.xml — Kategorien', 'concepts'),
    ('genres.xml — Kategorien', 'genres'),
    ('names.xml — Kategorien', 'names'),
    ('contributors.xml — Personen', 'contributors_persons'),
    ('contributors.xml — Organisationen', 'contributors_orgs'),
]

# Doc paths to scan for drift. Each entry is (path, keys-that-should-match).
# Patterns search for any occurrence of the count number that is NOT the
# actual current value — when found, that means the doc is stale.
DOC_TARGETS = [
    ('docs/TEI-MODEL.md', ['corpus_files', 'lexicon_entries', 'works', 'persons',
                            'concepts', 'genres', 'names', 'variants_entries', 'variants_forms']),
    ('docs/INDEX.md', ['corpus_files']),
    ('docs/ROADMAP.md', ['corpus_files']),
    # CLAUDE.md is intentionally vague ("~670 TEI texts"), no exact check.
]


def find_stale_numbers(doc_path: str, current: int, key: str) -> list:
    """Look for stale counts in the doc.

    Strategy: tight drift window (±2 absolute, or ±2% relative for large
    numbers) plus a strong keyword anchor immediately after the number.
    This catches the common case "WZB ingest bumped 666 -> 667 but doc
    still says 666" without flagging arbitrary numbers near generic
    words like "TEI" or "files".

    Counts below 100 are not scanned: too many false positives from
    table indices, percentages, section numbers, version strings."""
    if not Path(doc_path).exists() or current < 100:
        return []

    # Strong keyword anchors (must appear immediately after the number).
    near_keywords = {
        'corpus_files': r'\s*(?:TEI(?:-XML)?\s+(?:files?|Dateien)|Korpus(?:-?[Dd]ateien)?)',
        'lexicon_entries': r'\s*Lemmata',
        'works': r'\s*Werke',
        'variants_entries': r'\s*(?:Variant|Eintr[äa]ge)',
        'variants_forms': r'\s*Formen',
        'persons': r'\s*Personen',
        'concepts': r'\s*(?:Konzepte|Begriffe|Kategorien)',
        'genres': r'\s*(?:Gattungen|Kategorien)',
        'names': r'\s*(?:Namen|Kategorien)',
    }
    keywords = near_keywords.get(key)
    if not keywords:
        return []

    # Drift window: 2 absolute or 2% relative (whichever is larger),
    # capped at 50 to avoid catching e.g. "100" near "Lemmata" when
    # current is 43754.
    window_size = max(2, min(50, int(current * 0.02)))
    content = Path(doc_path).read_text(encoding='utf-8')

    findings = []
    for m in re.finditer(rf'\b(\d{{1,3}}(?:[.,]\d{{3}})+|\d{{3,7}})\b', content):
        raw = m.group(1)
        try:
            num = int(raw.replace('.', '').replace(',', ''))
        except ValueError:
            continue
        if num == current or abs(num - current) > window_size:
            continue
        # Keyword must appear immediately after (within ~3 chars: space, slash,
        # comma, closing bracket are all ok).
        suffix = content[m.end():m.end() + 25]
        if re.match(keywords, suffix):
            line_no = content[:m.start()].count('\n') + 1
            # Show a bit of context centered on the match
            ctx_start = max(0, m.start() - 25)
            ctx = content[ctx_start:m.end() + 30].replace('\n', ' ').strip()
            findings.append((line_no, raw, ctx[:80]))
    return findings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--check', action='store_true',
                    help='exit code 1 if any stale numbers found in docs')
    args = ap.parse_args()

    counts = collect_counts()

    print('=== Current corpus + authority counts ===')
    print()
    print('| Position | Aktueller Wert |')
    print('|----------|----------------|')
    for label, key in LABELS:
        print(f'| {label} | {counts[key]:,} |')
    print()

    print('=== Doc drift scan ===')
    print()
    total_drift = 0
    for doc_path, keys in DOC_TARGETS:
        if not keys:
            continue
        for key in keys:
            findings = find_stale_numbers(doc_path, counts[key], key)
            if findings:
                print(f'  {doc_path} — expected {counts[key]:,} for {key}:')
                for line_no, raw, ctx in findings[:5]:
                    print(f'    L{line_no}: "{raw}" near "{ctx}"')
                if len(findings) > 5:
                    print(f'    ... +{len(findings) - 5} more')
                total_drift += len(findings)

    if total_drift == 0:
        print('  No drift detected against scanned docs.')
    else:
        print()
        print(f'  Total potential drift hits: {total_drift}')
        print('  Note: heuristic scan; review manually before editing.')

    if args.check and total_drift > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
