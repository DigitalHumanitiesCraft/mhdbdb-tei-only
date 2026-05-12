#!/usr/bin/env python3
"""Survey aller Concepts fuer die Begriffs-Verteilung (#47 R2 Follow-up).

Hintergrund: `playground/js/ui/tei/concept-distribution.js` aggregiert beim
Klick auf einen Begriff alle Lemmata, die diesen Concept referenzieren, und
summiert Vorkommen ueber alle 667 Texte. Bei sehr grossen Concepts (z.B.
viele tausend zugeordnete Lemmata) koennte das den Browser einfrieren.
Heute sind nur 2/567 Concepts manuell validiert.

Dieses Skript spiegelt die JS-Logik 1:1 in Python und berechnet:

  - lemma_count           Anzahl Lemmata mit conceptIds.includes(concept_id)
  - text_hits             Anzahl Texte mit mindestens einem Treffer
  - total_occurrences     Summe aller Lemma-Positionen ueber alle Texte
  - distinct_lemmata_max  Maximum distinkter Lemmata in einem einzelnen Text

Output: Markdown-Report nach docs/research/concept-distribution-survey.md
(Histogramm + Tabellen-Tops + Anomalie-Flags + Empfehlung fuer Worst-Case-Test).

Usage:
    python scripts/audit/survey-concept-distribution.py
    python scripts/audit/survey-concept-distribution.py --out path/to/report.md
    python scripts/audit/survey-concept-distribution.py --json   # zusaetzlich JSON dump

Datenquelle: data/authority-index.json.gz + data/corpus-index.json.gz.
"""
import argparse
import gzip
import json
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
AUTHORITY_INDEX = PROJECT_ROOT / 'data' / 'authority-index.json.gz'
CORPUS_INDEX = PROJECT_ROOT / 'data' / 'corpus-index.json.gz'
DEFAULT_OUT = PROJECT_ROOT / 'docs' / 'research' / 'concept-distribution-survey.md'

# Schwellen analog Handoff-Spec. Wenn ein Concept eine Schwelle ueberschreitet,
# wird es in der Anomalie-Tabelle gelistet und ggf. fuer den Browser-Performance-
# Check als Worst-Case-Kandidat empfohlen.
THRESHOLD_LEMMATA_HIGH = 2000      # "viele Lemmata" -> Aggregation-Hotspot
THRESHOLD_OCCURRENCES_HIGH = 100_000  # "viele Vorkommen" -> grosse Render-Last
THRESHOLD_LEMMATA_ZERO = 0         # exakt 0 = Concept ohne Sense-Referenz


def load_json_gz(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def build_concept_to_lemmata(lemmata):
    """Spiegelung von findMatchingLemmata(), aber als reverse-index aufgebaut.

    JS iteriert pro User-Anfrage ueber alle Lemmata. Hier ein Pass -> dict.
    Resultat: {concept_id: [{'id', 'lemma', 'pos'}, ...]}
    """
    out = {}
    for lemma in lemmata:
        senses = lemma.get('senses') or []
        if not senses:
            continue
        # Sammle alle Concepts, die irgendein Sense dieses Lemmas referenziert.
        # `break` in der JS-Logik entspricht: Lemma erscheint genau einmal pro
        # Concept, auch wenn mehrere Senses denselben Concept teilen.
        seen_for_lemma = set()
        for sense in senses:
            for cid in sense.get('conceptIds') or []:
                if cid in seen_for_lemma:
                    continue
                seen_for_lemma.add(cid)
                out.setdefault(cid, []).append({
                    'id': lemma.get('id'),
                    'lemma': lemma.get('lemma'),
                    'pos': lemma.get('pos'),
                })
    return out


def compute_distribution(matching_lemmata_ids, texts):
    """Spiegelung von computeDistribution(). Returns aggregierte Werte.

    matching_lemmata_ids: set/list of lemma_ids
    texts: corpus_index['texts']
    """
    lemma_id_set = set(matching_lemmata_ids)
    text_hits = 0
    total_occurrences = 0
    distinct_max = 0
    for text in texts:
        text_lemmata = text.get('lemmata') or {}
        text_total = 0
        text_distinct = 0
        # Eine kleine Optimierung: iteriere ueber den kleineren der beiden Sets.
        if len(lemma_id_set) <= len(text_lemmata):
            for lid in lemma_id_set:
                positions = text_lemmata.get(lid)
                if positions:
                    text_total += len(positions)
                    text_distinct += 1
        else:
            for lid, positions in text_lemmata.items():
                if lid in lemma_id_set and positions:
                    text_total += len(positions)
                    text_distinct += 1
        if text_total > 0:
            text_hits += 1
            total_occurrences += text_total
            if text_distinct > distinct_max:
                distinct_max = text_distinct
    return text_hits, total_occurrences, distinct_max


def survey(authority, corpus):
    concepts = authority.get('concepts') or []
    lemmata = authority.get('lemmata') or []
    texts = corpus.get('texts') or []

    print(f"Concepts: {len(concepts):,}", file=sys.stderr)
    print(f"Lemmata:  {len(lemmata):,}", file=sys.stderr)
    print(f"Texts:    {len(texts):,}", file=sys.stderr)

    concept_to_lemmata = build_concept_to_lemmata(lemmata)
    print(f"Concepts mit min. 1 Lemma: {len(concept_to_lemmata):,}", file=sys.stderr)

    rows = []
    total = len(concepts)
    for i, c in enumerate(concepts, 1):
        if i % 50 == 0:
            print(f"  ... {i}/{total}", file=sys.stderr)
        cid = c.get('id')
        matching = concept_to_lemmata.get(cid, [])
        lemma_count = len(matching)
        if lemma_count == 0:
            text_hits = 0
            total_occurrences = 0
            distinct_max = 0
        else:
            lemma_ids = [m['id'] for m in matching]
            text_hits, total_occurrences, distinct_max = compute_distribution(lemma_ids, texts)
        rows.append({
            'id': cid,
            'termDE': c.get('termDE') or '',
            'termEN': c.get('termEN') or '',
            'lemma_count': lemma_count,
            'text_hits': text_hits,
            'total_occurrences': total_occurrences,
            'distinct_lemmata_max': distinct_max,
        })
    return rows


def stats_block(values, label):
    """Min / Median / P95 / Max-Block fuer eine Werte-Liste."""
    nonzero = [v for v in values if v > 0]
    if not nonzero:
        return f"- **{label}**: alle Werte 0"
    nonzero_sorted = sorted(nonzero)
    p95_idx = max(0, int(len(nonzero_sorted) * 0.95) - 1)
    return (
        f"- **{label}** (n={len(nonzero):,} von {len(values):,} non-zero): "
        f"min={min(nonzero):,}, median={int(statistics.median(nonzero)):,}, "
        f"P95={nonzero_sorted[p95_idx]:,}, max={max(nonzero):,}"
    )


def render_table(rows, key, n=15, descending=True):
    sorted_rows = sorted(rows, key=lambda r: r[key], reverse=descending)[:n]
    out = ["| Concept-ID | termDE | Lemmata | Text-Hits | Vorkommen |",
           "|---|---|---:|---:|---:|"]
    for r in sorted_rows:
        out.append(
            f"| `{r['id']}` | {r['termDE'] or '-'} "
            f"| {r['lemma_count']:,} | {r['text_hits']:,} | {r['total_occurrences']:,} |"
        )
    return "\n".join(out)


def render_report(rows, authority_version, corpus_version):
    lemma_counts = [r['lemma_count'] for r in rows]
    text_hits = [r['text_hits'] for r in rows]
    occurrences = [r['total_occurrences'] for r in rows]
    distinct_max = [r['distinct_lemmata_max'] for r in rows]

    zero_lemmata = [r for r in rows if r['lemma_count'] == 0]
    high_lemmata = [r for r in rows if r['lemma_count'] >= THRESHOLD_LEMMATA_HIGH]
    high_occurrences = [r for r in rows if r['total_occurrences'] >= THRESHOLD_OCCURRENCES_HIGH]

    worst_case = max(rows, key=lambda r: r['lemma_count'])
    biggest_occurrence = max(rows, key=lambda r: r['total_occurrences'])

    parts = []
    parts.append("# Concept-Distribution Survey\n")
    parts.append(
        "Programmatischer Vollscan aller Concepts gegen den Korpus, um Worst-Case-"
        "Lasten fuer das Frontend-Modul `playground/js/ui/tei/concept-distribution.js` "
        "zu identifizieren. Spiegelt die JS-Aggregations-Logik 1:1.\n"
    )
    parts.append(
        f"**Datenstand:** authority-index v{authority_version}, "
        f"corpus-index v{corpus_version}. Insgesamt {len(rows):,} Concepts ausgewertet.\n"
    )

    parts.append("## Verteilungs-Statistik\n")
    parts.append(stats_block(lemma_counts, "Lemmata pro Concept"))
    parts.append(stats_block(text_hits, "Texte mit Treffern pro Concept"))
    parts.append(stats_block(occurrences, "Gesamtvorkommen pro Concept"))
    parts.append(stats_block(distinct_max, "Distinkte Lemmata pro Text (Maximum je Concept)"))

    parts.append("\n## Anomalien\n")
    parts.append(
        f"- Concepts ohne zugeordnete Lemmata: **{len(zero_lemmata):,}** "
        f"(von {len(rows):,})"
    )
    parts.append(
        f"- Concepts mit >= {THRESHOLD_LEMMATA_HIGH:,} Lemmata "
        f"(Aggregation-Hotspots): **{len(high_lemmata):,}**"
    )
    parts.append(
        f"- Concepts mit >= {THRESHOLD_OCCURRENCES_HIGH:,} Vorkommen "
        f"(Render-Last): **{len(high_occurrences):,}**"
    )

    parts.append("\n## Worst-Case-Kandidaten\n")
    parts.append(
        f"**Hoechste Lemma-Last:** `{worst_case['id']}` "
        f"({worst_case['termDE'] or '-'}) mit "
        f"{worst_case['lemma_count']:,} zugeordneten Lemmata, "
        f"{worst_case['text_hits']:,} Texten, "
        f"{worst_case['total_occurrences']:,} Vorkommen.\n"
    )
    parts.append(
        f"**Hoechste Vorkommen-Last:** `{biggest_occurrence['id']}` "
        f"({biggest_occurrence['termDE'] or '-'}) mit "
        f"{biggest_occurrence['total_occurrences']:,} Vorkommen, "
        f"{biggest_occurrence['lemma_count']:,} Lemmata, "
        f"{biggest_occurrence['text_hits']:,} Texten.\n"
    )
    parts.append(
        "Empfehlung fuer Browser-Performance-Check: das erste der beiden "
        "Concepts im Playground laden und DevTools-Profiler messen. Wenn das "
        "rendering+aggregation `<` 500ms bleibt, Playwright-Regression-Test "
        "schreiben; wenn `>` 2s, Performance-Patch (Web-Worker oder "
        "requestIdleCallback-Chunking in `findMatchingLemmata`).\n"
    )

    parts.append("## Top 15 nach Lemma-Count\n")
    parts.append(render_table(rows, 'lemma_count', n=15))
    parts.append("\n## Top 15 nach Vorkommen\n")
    parts.append(render_table(rows, 'total_occurrences', n=15))
    parts.append("\n## Top 15 nach Texte mit Treffern\n")
    parts.append(render_table(rows, 'text_hits', n=15))

    if zero_lemmata:
        parts.append(
            f"\n## Concepts ohne zugeordnete Lemmata ({len(zero_lemmata):,})\n"
        )
        parts.append(
            "Diese Concepts haben kein einziges Lemma mit "
            "`senses[*].conceptIds.includes(this.id)`. Im Frontend zeigen "
            "sie den Block \"Keine Lemmata sind diesem Begriff zugeordnet\".\n"
        )
        parts.append("| Concept-ID | termDE |")
        parts.append("|---|---|")
        for r in sorted(zero_lemmata, key=lambda r: r['id'])[:50]:
            parts.append(f"| `{r['id']}` | {r['termDE'] or '-'} |")
        if len(zero_lemmata) > 50:
            parts.append(f"\n... und {len(zero_lemmata) - 50:,} weitere.")

    return "\n".join(parts) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--out', type=Path, default=DEFAULT_OUT,
                        help=f"Output-Pfad fuer Markdown-Report (default: {DEFAULT_OUT.relative_to(PROJECT_ROOT)})")
    parser.add_argument('--json', action='store_true',
                        help="Zusaetzlich JSON-Dump neben dem Markdown ablegen.")
    args = parser.parse_args()

    print(f"Lade {AUTHORITY_INDEX.relative_to(PROJECT_ROOT)} ...", file=sys.stderr)
    authority = load_json_gz(AUTHORITY_INDEX)
    print(f"Lade {CORPUS_INDEX.relative_to(PROJECT_ROOT)} ...", file=sys.stderr)
    corpus = load_json_gz(CORPUS_INDEX)

    rows = survey(authority, corpus)
    report = render_report(rows, authority.get('version', '?'), corpus.get('version', '?'))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding='utf-8')
    print(f"Report -> {args.out.relative_to(PROJECT_ROOT)}", file=sys.stderr)

    if args.json:
        json_path = args.out.with_suffix('.json')
        json_path.write_text(
            json.dumps(rows, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        print(f"JSON   -> {json_path.relative_to(PROJECT_ROOT)}", file=sys.stderr)

    return 0


if __name__ == '__main__':
    sys.exit(main())
