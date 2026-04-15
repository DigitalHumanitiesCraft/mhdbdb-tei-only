#!/usr/bin/env python3
"""
Authority Files Audit — Structure, Cross-References, Data Quality

Analyses all 8 authority files in authority-files/ (inkl. contributors.xml) to produce:
  - Element/attribute inventory per file
  - Cross-reference inventory (which file references which)
  - Referential integrity check (orphaned references)
  - ID format analysis
  - Denormalization detection

Output:
  - authority-audit.json (machine-readable)
  - AUTHORITY-AUDIT-REPORT.md (human-readable)

Usage:
    python scripts/data-wrangling/tei-model/authority-files/audit-authority-files.py
"""

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from lxml import etree

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'
XML_NS = 'http://www.w3.org/XML/1998/namespace'
XML = f'{{{XML_NS}}}'

AUTHORITY_DIR = Path('authority-files')
SCRIPT_DIR = Path(__file__).resolve().parent


def collect_ids(tree):
    """Collect all xml:id values from a tree."""
    ids = set()
    for elem in tree.iter():
        xid = elem.get(f'{XML}id')
        if xid:
            ids.add(xid)
    return ids


def collect_refs(tree, filename):
    """Collect all cross-references from a tree."""
    refs = []
    for elem in tree.iter():
        for attr in ('ref', 'target', 'corresp'):
            val = elem.get(attr)
            if val and ('.xml' in val or val.startswith('#')):
                local = elem.tag.replace(TEI, '')
                # Parse target file and fragment
                if '#' in val:
                    target_file, fragment = val.split('#', 1)
                else:
                    target_file, fragment = val, None
                if not target_file:
                    target_file = filename  # internal ref
                refs.append({
                    'element': local,
                    'attribute': attr,
                    'target_file': target_file,
                    'fragment': fragment,
                    'full_value': val,
                })
    return refs


def audit_file(filepath):
    """Audit a single authority file."""
    tree = etree.parse(str(filepath))
    root = tree.getroot()
    filename = filepath.name

    # Element inventory
    elem_counts = Counter()
    attr_inventory = defaultdict(lambda: defaultdict(Counter))
    for elem in root.iter():
        local = elem.tag.replace(TEI, '').replace(f'{{{XML_NS}}}', 'xml:')
        if local.startswith('{'):
            continue
        elem_counts[local] += 1
        for attr, val in elem.attrib.items():
            attr_name = attr.replace(f'{XML}', 'xml:').replace(TEI, '')
            attr_inventory[local][attr_name][val] += 1

    # IDs
    ids = collect_ids(tree)
    id_formats = Counter()
    for xid in ids:
        if re.match(r'^[a-z]+_\d+$', xid):
            id_formats['numeric'] += 1
        elif re.match(r'^[a-z]+_\d{8}$', xid):
            id_formats['hierarchical'] += 1
        elif re.match(r'^[a-z]+_[a-f0-9]{8,}', xid):
            id_formats['uuid/hash'] += 1
        elif re.match(r'^[a-z]+_\d+_[a-z]+_\d+', xid):
            id_formats['compound'] += 1
        elif re.match(r'^[A-Z]+_[A-Z]+$', xid):
            id_formats['sigle_key'] += 1
        elif re.match(r'^mhdbdb-', xid):
            id_formats['taxonomy_root'] += 1
        else:
            id_formats['other'] += 1

    # Cross-references
    refs = collect_refs(tree, filename)

    # Data placement
    enc_desc = root.find(f'.//{TEI}encodingDesc')
    body = root.find(f'.//{TEI}body')
    enc_elem_count = len(list(enc_desc.iter())) if enc_desc is not None else 0
    body_elem_count = len(list(body.iter())) if body is not None else 0

    return {
        'filename': filename,
        'size_kb': filepath.stat().st_size // 1024,
        'element_counts': dict(elem_counts),
        'total_elements': sum(elem_counts.values()),
        'id_count': len(ids),
        'id_formats': dict(id_formats),
        'ref_count': len(refs),
        'data_placement': {
            'encodingDesc_elements': enc_elem_count,
            'body_elements': body_elem_count,
        },
    }, ids, refs


def check_referential_integrity(all_ids, all_refs):
    """Check if all cross-references point to existing IDs."""
    orphans = []
    for ref in all_refs:
        target_file = ref['target_file']
        fragment = ref['fragment']
        if not fragment:
            continue
        # Check if target ID exists in the target file
        if target_file in all_ids:
            if fragment not in all_ids[target_file]:
                orphans.append({
                    'source_file': ref.get('source_file', '?'),
                    'target': ref['full_value'],
                    'element': ref['element'],
                    'attribute': ref['attribute'],
                })
    return orphans


def detect_denormalization(all_refs):
    """Detect denormalized data (label text in cross-file refs)."""
    issues = []
    for ref in all_refs:
        if ref['element'] == 'ref' and ref['target_file'] and '.xml' in ref['target_file']:
            issues.append({
                'source_file': ref.get('source_file', '?'),
                'target': ref['full_value'],
                'issue': 'Label text in <ref> — should be <ptr>',
            })
    return issues


def build_report(audit_data, orphans, denorm, ref_summary):
    """Build markdown report."""
    lines = [
        '# Authority Files Audit Report',
        '',
        f'**Date:** {date.today().isoformat()}',
        f'**Files:** {len(audit_data)}',
        '',
        '---',
        '',
        '## Overview',
        '',
        '| File | Elements | IDs | Cross-Refs | Size |',
        '|------|----------|-----|------------|------|',
    ]

    for d in audit_data:
        lines.append(f'| {d["filename"]} | {d["total_elements"]:,} | {d["id_count"]:,} | {d["ref_count"]:,} | {d["size_kb"]:,} KB |')

    lines.extend(['', '## ID Formats', ''])
    for d in audit_data:
        if d['id_formats']:
            lines.append(f'**{d["filename"]}:** {d["id_formats"]}')

    lines.extend(['', '## Cross-Reference Summary', ''])
    lines.append('| From | To | Count | Mechanism |')
    lines.append('|------|------|-------|-----------|')
    for (src, tgt, mech), count in sorted(ref_summary.items(), key=lambda x: -x[1]):
        lines.append(f'| {src} | {tgt} | {count:,} | {mech} |')

    lines.extend(['', '## Referential Integrity', ''])
    if orphans:
        lines.append(f'**{len(orphans)} orphaned references found:**')
        lines.append('')
        lines.append('| Source | Target | Element | Attribute |')
        lines.append('|--------|--------|---------|-----------|')
        for o in orphans[:50]:
            lines.append(f'| {o["source_file"]} | {o["target"]} | {o["element"]} | {o["attribute"]} |')
        if len(orphans) > 50:
            lines.append(f'| ... | ... | ... | ({len(orphans)-50} more) |')
    else:
        lines.append('No orphaned references found.')

    lines.extend(['', '## Denormalization', ''])
    if denorm:
        by_file = defaultdict(int)
        for d in denorm:
            by_file[d['source_file']] += 1
        for f, c in sorted(by_file.items(), key=lambda x: -x[1]):
            lines.append(f'- {f}: {c} denormalized `<ref>` elements')
    else:
        lines.append('No denormalized references found.')

    lines.extend(['', '## Data Placement', ''])
    for d in audit_data:
        dp = d['data_placement']
        lines.append(f'- {d["filename"]}: encodingDesc={dp["encodingDesc_elements"]} elements, body={dp["body_elements"]} elements')

    return '\n'.join(lines)


def main():
    if not AUTHORITY_DIR.exists():
        print(f'Error: {AUTHORITY_DIR} not found')
        return 1

    files = sorted(AUTHORITY_DIR.glob('*.xml'))
    print(f'Auditing {len(files)} authority files...')

    audit_data = []
    all_ids = {}  # filename → set of IDs
    all_refs = []  # flat list of all refs
    ref_summary = Counter()  # (source, target, mechanism) → count

    for f in files:
        print(f'  {f.name}...')
        data, ids, refs = audit_file(f)
        audit_data.append(data)
        all_ids[f.name] = ids

        for ref in refs:
            ref['source_file'] = f.name
            all_refs.append(ref)
            if ref['target_file'] and ref['target_file'] != f.name:
                ref_summary[(f.name, ref['target_file'], f'<{ref["element"]} @{ref["attribute"]}>')] += 1
            elif not ref['target_file'] or ref['target_file'] == f.name:
                ref_summary[(f.name, f.name + ' (internal)', f'<{ref["element"]} @{ref["attribute"]}>')] += 1

    # Referential integrity
    print('Checking referential integrity...')
    orphans = check_referential_integrity(all_ids, all_refs)
    print(f'  {len(orphans)} orphaned references')

    # Denormalization
    denorm = detect_denormalization(all_refs)
    print(f'  {len(denorm)} denormalized references')

    # Save JSON
    json_out = SCRIPT_DIR / 'authority-audit.json'
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump({
            'date': date.today().isoformat(),
            'files': audit_data,
            'orphaned_references': orphans,
            'denormalized_references': len(denorm),
            'ref_summary': {f'{k[0]}→{k[1]} ({k[2]})': v for k, v in ref_summary.items()},
        }, f, indent=2, ensure_ascii=False)
    print(f'  Written: {json_out}')

    # Save report
    md_out = SCRIPT_DIR / 'AUTHORITY-AUDIT-REPORT.md'
    report = build_report(audit_data, orphans, denorm, ref_summary)
    with open(md_out, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f'  Written: {md_out}')

    # Summary
    print()
    print(f'Summary:')
    print(f'  Files: {len(audit_data)}')
    print(f'  Total elements: {sum(d["total_elements"] for d in audit_data):,}')
    print(f'  Total IDs: {sum(d["id_count"] for d in audit_data):,}')
    print(f'  Total cross-refs: {len(all_refs):,}')
    print(f'  Orphaned refs: {len(orphans)}')
    print(f'  Denormalized refs: {len(denorm)}')

    return 0


if __name__ == '__main__':
    sys.exit(main())
