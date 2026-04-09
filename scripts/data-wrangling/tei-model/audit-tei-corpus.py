"""
TEI Corpus Audit — Element & Attribute Inventory

Analyses all base TEI files (tei/*.tei.xml, excluding *.disamb.tei.xml)
to produce a complete inventory of elements, attributes, and values.

Output:
  - data/tei-audit.json    (machine-readable)
  - docs/TEI-AUDIT-REPORT.md (human-readable)

Usage:
  python scripts/data-wrangling/tei-model/audit-tei-corpus.py
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from lxml import etree

TEI_NS = '{http://www.tei-c.org/ns/1.0}'
XML_NS = '{http://www.w3.org/XML/1998/namespace}'

# Attribute value cardinality threshold: above this, only store pattern + samples
CARDINALITY_THRESHOLD = 100
# Max samples to store for high-cardinality attributes
MAX_SAMPLES = 10
# Max distinct values to store for low-cardinality attributes
MAX_VALUES = 500

def strip_ns(tag):
    """Strip TEI namespace from tag name."""
    if tag.startswith(TEI_NS):
        return tag[len(TEI_NS):]
    if tag.startswith(XML_NS):
        return 'xml:' + tag[len(XML_NS):]
    return tag


def detect_pattern(values):
    """Try to detect a URI/ID pattern from sample values."""
    if not values:
        return None
    samples = list(values)[:20]
    # Check for lexicon.xml#lemma_ pattern
    if all(v.startswith('lexicon.xml#lemma_') for v in samples):
        return 'lexicon.xml#lemma_{id}[_sense_{id}[_type_{id}]]'
    if all(v.startswith('lexicon.xml#') for v in samples):
        return 'lexicon.xml#{ref}'
    if all(v.startswith('persons.xml#') for v in samples):
        return 'persons.xml#person_{id}'
    if all(v.startswith('works.xml#') for v in samples):
        return 'works.xml#work_{id}'
    if all(v.startswith('genres.xml#') for v in samples):
        return 'genres.xml#genre_{hash}'
    if all(v.startswith('variants.xml#') for v in samples):
        return 'variants.xml#{ref}'
    if all(v.startswith('#') for v in samples):
        return '#{fragment_id}'
    if all(v.startswith('http') for v in samples):
        return '{URI}'
    # Check for SIGLE_digits pattern (xml:id)
    if all(re.match(r'^[A-Z0-9]+_', v) for v in samples):
        return '{SIGLE}_{position}'
    return None


def audit_corpus(tei_dir):
    """Run the full audit on all base TEI files."""
    # Collect files
    all_files = sorted(Path(tei_dir).glob('*.tei.xml'))
    base_files = [f for f in all_files if '.disamb.' not in f.name]

    print(f'Found {len(base_files)} base TEI files (excluded {len(all_files) - len(base_files)} .disamb files)')

    # Data structures
    # element_name -> {count, file_count, parents: Counter, children: Counter, attributes: {attr_name -> {count, file_count, values: Counter}}}
    elements = defaultdict(lambda: {
        'count': 0,
        'files': set(),
        'parents': Counter(),
        'children': Counter(),
        'child_sequences': Counter(),  # ordered child tag sequences
        'attributes': defaultdict(lambda: {
            'count': 0,
            'files': set(),
            'values': Counter(),
            'all_values': set(),  # for cardinality check
        })
    })

    file_stats = []
    total_elements = 0

    for i, filepath in enumerate(base_files):
        if (i + 1) % 50 == 0:
            print(f'  {i + 1}/{len(base_files)}...', flush=True)

        tree = etree.parse(str(filepath))
        filename = filepath.name
        file_element_count = 0

        for elem in tree.iter():
            if not isinstance(elem.tag, str):
                continue  # skip comments, PIs

            tag = strip_ns(elem.tag)
            el = elements[tag]
            el['count'] += 1
            el['files'].add(filename)
            file_element_count += 1

            # Parent relationship
            parent = elem.getparent()
            if parent is not None and isinstance(parent.tag, str):
                parent_tag = strip_ns(parent.tag)
                el['parents'][parent_tag] += 1

            # Child elements (direct children only)
            child_tags = []
            for child in elem:
                if isinstance(child.tag, str):
                    child_tag = strip_ns(child.tag)
                    el['children'][child_tag] += 1
                    child_tags.append(child_tag)

            # Record child sequence (for content model inference)
            if child_tags:
                # Deduplicate consecutive same-tags for pattern recognition
                deduped = []
                for t in child_tags:
                    if not deduped or deduped[-1] != t:
                        deduped.append(t)
                seq = ' > '.join(deduped)
                el['child_sequences'][seq] += 1

            # Attributes
            for attr_name, attr_value in elem.attrib.items():
                attr_key = strip_ns(attr_name)
                attr = el['attributes'][attr_key]
                attr['count'] += 1
                attr['files'].add(filename)
                attr['values'][attr_value] += 1
                if len(attr['all_values']) < CARDINALITY_THRESHOLD + 1:
                    attr['all_values'].add(attr_value)

        total_elements += file_element_count
        file_stats.append({
            'name': filename,
            'elements': file_element_count,
        })

    print(f'  Done. {total_elements:,} elements across {len(base_files)} files.')
    return elements, file_stats, base_files


def build_json(elements, file_stats, base_files):
    """Convert audit data to JSON-serializable structure."""
    # Sort files by element count
    file_stats.sort(key=lambda x: x['elements'])

    result = {
        'meta': {
            'files_analyzed': len(base_files),
            'files_excluded_pattern': '*.disamb.tei.xml',
            'date': str(date.today()),
            'script': 'scripts/data-wrangling/tei-model/audit-tei-corpus.py',
        },
        'corpus_stats': {
            'total_elements': sum(f['elements'] for f in file_stats),
            'total_files': len(base_files),
            'largest_file': file_stats[-1] if file_stats else None,
            'smallest_file': file_stats[0] if file_stats else None,
        },
        'elements': {}
    }

    # Sort elements by count (descending)
    sorted_elements = sorted(elements.items(), key=lambda x: x[1]['count'], reverse=True)

    for tag, data in sorted_elements:
        el = {
            'count': data['count'],
            'file_count': len(data['files']),
            'parents': dict(data['parents'].most_common(20)),
            'children': dict(data['children'].most_common(30)),
            'child_sequences_top10': dict(data['child_sequences'].most_common(10)),
            'attributes': {}
        }

        for attr_name, attr_data in sorted(data['attributes'].items(), key=lambda x: x[1]['count'], reverse=True):
            cardinality = len(attr_data['all_values'])
            is_high = cardinality > CARDINALITY_THRESHOLD

            attr_entry = {
                'count': attr_data['count'],
                'file_count': len(attr_data['files']),
                'distinct_values': cardinality if cardinality <= CARDINALITY_THRESHOLD else f'>{CARDINALITY_THRESHOLD}',
            }

            if is_high:
                attr_entry['cardinality'] = 'high'
                attr_entry['pattern'] = detect_pattern(attr_data['all_values'])
                attr_entry['samples'] = list(attr_data['all_values'])[:MAX_SAMPLES]
            else:
                attr_entry['cardinality'] = 'low'
                attr_entry['values'] = dict(attr_data['values'].most_common(MAX_VALUES))

            el['attributes'][attr_name] = attr_entry

        result['elements'][tag] = el

    return result


def build_markdown(audit_json):
    """Generate human-readable Markdown report from audit JSON."""
    meta = audit_json['meta']
    stats = audit_json['corpus_stats']
    elements = audit_json['elements']

    lines = []
    lines.append('# TEI Corpus Audit Report')
    lines.append('')
    lines.append(f'**Date:** {meta["date"]}')
    lines.append(f'**Files analyzed:** {meta["files_analyzed"]}')
    lines.append(f'**Excluded:** `{meta["files_excluded_pattern"]}`')
    lines.append(f'**Script:** `{meta["script"]}`')
    lines.append('')
    lines.append('---')
    lines.append('')

    # Corpus stats
    lines.append('## Korpus-Statistiken')
    lines.append('')
    lines.append(f'| Metrik | Wert |')
    lines.append(f'|--------|------|')
    lines.append(f'| Dateien | {stats["total_files"]} |')
    lines.append(f'| Elemente gesamt | {stats["total_elements"]:,} |')
    if stats['largest_file']:
        lines.append(f'| Groesste Datei | {stats["largest_file"]["name"]} ({stats["largest_file"]["elements"]:,} Elemente) |')
    if stats['smallest_file']:
        lines.append(f'| Kleinste Datei | {stats["smallest_file"]["name"]} ({stats["smallest_file"]["elements"]:,} Elemente) |')
    lines.append(f'| Distinkte Elemente | {len(elements)} |')
    lines.append('')

    # Element inventory (top 30)
    lines.append('## Element-Inventar (Top 30)')
    lines.append('')
    lines.append('| # | Element | Count | Dateien | Eltern | Attribute |')
    lines.append('|---|---------|-------|---------|--------|-----------|')
    for i, (tag, data) in enumerate(list(elements.items())[:30]):
        parents = ', '.join(f'{p}' for p in list(data['parents'].keys())[:5])
        attrs = ', '.join(f'@{a}' for a in list(data['attributes'].keys())[:5])
        lines.append(f'| {i+1} | `<{tag}>` | {data["count"]:,} | {data["file_count"]} | {parents} | {attrs} |')
    lines.append('')

    # Detailed attribute inventory for key elements
    key_elements = ['w', 'seg', 'hi', 'div', 'l', 'lb', 'lg', 'p', 'pb', 'head',
                    'supplied', 'num', 'caesura', 'pc', 'TEI', 'teiHeader',
                    'title', 'author', 'biblStruct', 'bibl', 'category', 'person']

    lines.append('## Attribut-Inventar (Schluessel-Elemente)')
    lines.append('')

    for tag in key_elements:
        if tag not in elements:
            continue
        data = elements[tag]
        lines.append(f'### `<{tag}>` — {data["count"]:,} Vorkommen in {data["file_count"]} Dateien')
        lines.append('')

        # Parents
        parent_str = ', '.join(f'`<{p}>` ({c:,})' for p, c in list(data['parents'].items())[:10])
        lines.append(f'**Eltern:** {parent_str}')
        lines.append('')

        # Children
        if data['children']:
            child_str = ', '.join(f'`<{c}>` ({n:,})' for c, n in list(data['children'].items())[:10])
            lines.append(f'**Kinder:** {child_str}')
            lines.append('')

        # Child sequences (content model hints)
        if data['child_sequences_top10']:
            lines.append('**Haeufigste Kind-Sequenzen:**')
            for seq, count in list(data['child_sequences_top10'].items())[:5]:
                lines.append(f'- `{seq}` ({count:,}x)')
            lines.append('')

        # Attributes
        if data['attributes']:
            lines.append('| Attribut | Count | Dateien | Kardinalitaet | Werte/Pattern |')
            lines.append('|----------|-------|---------|---------------|---------------|')
            for attr_name, attr_data in data['attributes'].items():
                card = attr_data.get('cardinality', '?')
                if card == 'low' and 'values' in attr_data:
                    vals = attr_data['values']
                    if len(vals) <= 10:
                        val_str = ', '.join(f'`{v}` ({c:,})' for v, c in sorted(vals.items(), key=lambda x: -x[1]))
                    else:
                        top5 = list(sorted(vals.items(), key=lambda x: -x[1]))[:5]
                        val_str = ', '.join(f'`{v}` ({c:,})' for v, c in top5) + f' ... +{len(vals)-5} more'
                else:
                    pattern = attr_data.get('pattern', '—')
                    val_str = f'Pattern: `{pattern}`' if pattern else f'{attr_data.get("distinct_values", "?")} distinkte'
                lines.append(f'| `@{attr_name}` | {attr_data["count"]:,} | {attr_data["file_count"]} | {card} | {val_str} |')
            lines.append('')

        lines.append('---')
        lines.append('')

    # IST/SOLL comparison
    lines.append('## IST/SOLL-Vergleich')
    lines.append('')

    # Non-standard attributes
    lines.append('### Nicht-Standard-Attribute')
    lines.append('')
    non_standard = []
    if 'w' in elements:
        for attr in ['meaningRef', 'wordRef']:
            if attr in elements['w']['attributes']:
                d = elements['w']['attributes'][attr]
                non_standard.append((attr, d['count'], d['file_count']))
    if non_standard:
        lines.append('| Attribut | Count | Dateien | Migration |')
        lines.append('|----------|-------|---------|-----------|')
        for attr, count, files in non_standard:
            migration = '`@ana`' if attr == 'meaningRef' else '`@corresp`'
            lines.append(f'| `@{attr}` | {count:,} | {files} | → {migration} |')
    else:
        lines.append('Keine nicht-Standard-Attribute auf `<w>` gefunden.')
    lines.append('')

    # seg type="pc" count
    if 'seg' in elements and 'type' in elements['seg']['attributes']:
        seg_vals = elements['seg']['attributes']['type'].get('values', {})
        pc_count = seg_vals.get('pc', 0)
        if pc_count:
            lines.append(f'### `<seg type="pc">` → `<pc>`')
            lines.append(f'')
            lines.append(f'{pc_count:,} Vorkommen von `<seg type="pc">`. TEI P5 empfiehlt `<pc>` als Ersatz.')
            lines.append('')

    # <l> in <p>
    if 'l' in elements and 'p' in elements['l'].get('parents', {}):
        l_in_p = elements['l']['parents'].get('p', 0)
        lines.append(f'### `<l>` in `<p>` (TEI-nonkonform fuer Prosa)')
        lines.append(f'')
        lines.append(f'{l_in_p:,} Vorkommen von `<l>` als Kind von `<p>`. TEI P5 definiert `<l>` als Verszeile.')
        lines.append('')

    # Full element list
    lines.append('## Anhang: Vollstaendige Element-Liste')
    lines.append('')
    lines.append('| Element | Count | Dateien |')
    lines.append('|---------|-------|---------|')
    for tag, data in elements.items():
        lines.append(f'| `<{tag}>` | {data["count"]:,} | {data["file_count"]} |')
    lines.append('')

    return '\n'.join(lines)


def main():
    # Determine paths relative to repo root
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent.parent  # scripts/data-wrangling/tei-model -> repo root
    tei_dir = repo_root / 'tei'
    json_out = script_dir / 'tei-audit.json'
    md_out = script_dir / 'TEI-AUDIT-REPORT.md'

    if not tei_dir.exists():
        print(f'Error: TEI directory not found: {tei_dir}')
        sys.exit(1)

    # Run audit
    print(f'TEI Corpus Audit')
    print(f'================')
    elements, file_stats, base_files = audit_corpus(str(tei_dir))

    # Build JSON
    print('Building JSON...', flush=True)
    audit_json = build_json(elements, file_stats, base_files)

    json_out.parent.mkdir(parents=True, exist_ok=True)
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(audit_json, f, indent=2, ensure_ascii=False)
    print(f'  Written: {json_out} ({json_out.stat().st_size // 1024} KB)')

    # Build Markdown
    print('Building Markdown report...', flush=True)
    md_content = build_markdown(audit_json)
    with open(md_out, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f'  Written: {md_out}')

    # Quick summary
    print()
    print(f'Summary:')
    print(f'  Files: {audit_json["corpus_stats"]["total_files"]}')
    print(f'  Elements: {audit_json["corpus_stats"]["total_elements"]:,}')
    print(f'  Distinct element types: {len(audit_json["elements"])}')
    w_data = audit_json['elements'].get('w', {})
    if w_data:
        print(f'  <w> elements: {w_data["count"]:,}')
        print(f'  <w> attributes: {", ".join(w_data.get("attributes", {}).keys())}')


if __name__ == '__main__':
    main()
