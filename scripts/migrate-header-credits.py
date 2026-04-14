#!/usr/bin/env python3
"""Migrate MHDBDB TEI headers to link editor/founder attribution to contributors.xml.

One-shot migration for Editor-Attribution Commit 4 aus docs/features/
editor-attribution.md. Nach erfolgreichem Lauf + Validierung nach
scripts/_archived/ verschieben (analog zu den #32-Migrationsskripten).

Usage:
    python scripts/migrate-header-credits.py --dry-run          # preview
    python scripts/migrate-header-credits.py                    # apply to all 666
    python scripts/migrate-header-credits.py --sample ABG LZT   # limit to sample

Idempotenz-Garantien:
  - authority-Block: Script entfernt erst alle persName[@role in (founder,
    coordinator)], baut dann die drei kanonischen Einträge neu. Mehrfach-
    Ausführung ergibt immer denselben Output.
  - Kollektiver respStmt: _is_collective_mhdbdb_respstmt() erkennt das
    Alt-Muster generisch via beliebiges Kind mit @ref enthaltend
    "mhdbdb.plus.ac.at". Zweiter Durchlauf findet das migrierte orgName-
    Pattern und skippt.
  - Lead-editor respStmt: explizite Check-vor-Insert-Logik via
    name/@ref Match auf contributors.xml#contrib_NNN.

Diff-Sauberkeit: Script schreibt OHNE pretty_print=True. Whitespace-
Mimicry erfolgt explizit über _child_indent() und _capture_closing_indent()
Helper, damit eingefügte Elemente bündig zum Bestand formatiert sind.
Resultat: der Diff zeigt nur die echten inhaltlichen Änderungen, analog
zur P0-4-GND-Migration aus Commit 61a0b4a1a.
"""
import argparse
import glob
import sys
from pathlib import Path
from lxml import etree

TEI_NS_URI = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS_URI}}}'
NS = {'t': TEI_NS_URI}

CANONICAL_AUTHORITY = [  # in jeder Datei, in dieser Reihenfolge
    ('founder',     'contrib_001', 'Klaus M.',  'Schmidt'),
    ('founder',     'contrib_002', 'Horst',     'Pütz'),
    ('coordinator', 'contrib_003', 'Katharina', 'Zeppezauer-Wachauer'),
]

LEAD_EDITORS = {  # Sigle → (contrib_id, full_name)
    'TKR': ('contrib_004', 'Vlastimil Brom'),
    'TKA': ('contrib_004', 'Vlastimil Brom'),
    'VTC': ('contrib_004', 'Vlastimil Brom'),
    'JT':  ('contrib_005', 'Katrin Woesner'),
    # WZB (Wenzelsbibel) → contrib_006 Julia Hintersteiner kommt nach Merge
    # von feature/wenzelsbibel-ingest (#66) in einem separaten Mini-Commit.
    # NICHT 'ZWB' eintragen — tei/ZWB.tei.xml ist "Zweierlei Bettzeug",
    # ein anderer Text.
}


def _child_indent(parent):
    """Return the whitespace that should precede a child of `parent`.

    Source-of-truth order:
    1. parent.text — whitespace BEFORE the first child, i.e. the correct
       child-indent in a pretty-printed file (works even when the parent
       has only one child, where parent[0].tail would give the smaller
       closing-tag indent).
    2. parent[0].tail — only when parent has 2+ children, where the
       inter-sibling whitespace IS the child indent.
    3. Hardcoded fallback.
    """
    if parent.text and parent.text.strip() == '':
        return parent.text
    if len(parent) >= 2 and parent[0].tail and parent[0].tail.strip() == '':
        return parent[0].tail
    return '\n          '


def _capture_closing_indent(parent):
    """Return the whitespace BEFORE the closing tag of `parent`.

    Whatever currently sits on the last child's .tail — that's the text
    that immediately precedes </parent>. Captured BEFORE any mutation so
    the new last element gets the same closing-tag indent.
    """
    if len(parent):
        return parent[-1].tail or '\n        '
    return parent.text or '\n        '


def migrate_authority(tree):
    """Rebuild publicationStmt/authority with founders + coordinator."""
    auth = tree.find('.//t:publicationStmt/t:authority', NS)
    if auth is None:
        return False
    # Capture indents BEFORE mutating
    child_indent = _child_indent(auth)
    closing_indent = _capture_closing_indent(auth)
    inner_indent = child_indent + '  '
    # Remove existing founder/coordinator persName children
    for pn in list(auth.findall(f'{TEI}persName')):
        if pn.get('role') in ('founder', 'coordinator'):
            auth.remove(pn)
    # Append the canonical three with proper internal + sibling indentation
    for role, cid, fore, sur in CANONICAL_AUTHORITY:
        pn = etree.SubElement(
            auth, f'{TEI}persName',
            role=role, ref=f'contributors.xml#{cid}'
        )
        pn.text = inner_indent
        pn.tail = child_indent
        fn = etree.SubElement(pn, f'{TEI}forename')
        fn.text = fore
        fn.tail = inner_indent
        sn = etree.SubElement(pn, f'{TEI}surname')
        sn.text = sur
        sn.tail = child_indent
    # Restore the original closing-tag indent on the new last child
    if len(auth):
        auth[-1].tail = closing_indent
    return True


def _is_collective_mhdbdb_respstmt(rs):
    """True if this <respStmt> is the legacy collective MHDBDB attribution.

    Generic check: any direct child of <respStmt> with @ref containing
    "mhdbdb.plus.ac.at". Catches both <name ref="..."> (the dominant
    pattern) and the hypothetical <orgName ref="...">.
    """
    for child in rs:
        if 'mhdbdb.plus.ac.at' in (child.get('ref') or ''):
            return True
    return False


def migrate_collective_respstmt(tree):
    """Replace MHDBDB-collective respStmt with orgName link."""
    title_stmt = tree.find('.//t:titleStmt', NS)
    if title_stmt is None:
        return False
    child_indent = _child_indent(title_stmt)
    closing_indent = _capture_closing_indent(title_stmt)
    inner_indent = child_indent + '  '
    # Remove ANY existing collective MHDBDB respStmt (name OR orgName variant)
    for rs in list(title_stmt.findall(f'{TEI}respStmt')):
        if _is_collective_mhdbdb_respstmt(rs):
            title_stmt.remove(rs)
    # Idempotency: skip if a migrated version is already present
    for rs in title_stmt.findall(f'{TEI}respStmt'):
        on = rs.find(f'{TEI}orgName')
        if on is not None and 'contributors.xml#mhdbdb-team' in (on.get('ref') or ''):
            return True
    # Append canonical with proper indentation
    rs = etree.SubElement(title_stmt, f'{TEI}respStmt')
    rs.text = inner_indent
    rs.tail = child_indent
    rp = etree.SubElement(rs, f'{TEI}resp')
    rp.text = 'digitale Zusammenführung, Annotation und semantische Klassifikation'
    rp.tail = inner_indent
    on = etree.SubElement(rs, f'{TEI}orgName', ref='contributors.xml#mhdbdb-team')
    on.text = 'MHDBDB-Team (vollständige Liste in contributors.xml)'
    on.tail = child_indent
    if len(title_stmt):
        title_stmt[-1].tail = closing_indent
    return True


def add_lead_editor(tree, sigle):
    """For specific texts, add a dedicated respStmt with the lead editor."""
    if sigle not in LEAD_EDITORS:
        return False
    contrib_id, full_name = LEAD_EDITORS[sigle]
    title_stmt = tree.find('.//t:titleStmt', NS)
    if title_stmt is None:
        return False
    child_indent = _child_indent(title_stmt)
    closing_indent = _capture_closing_indent(title_stmt)
    inner_indent = child_indent + '  '
    # Idempotent: skip if already present
    for n in title_stmt.xpath('./t:respStmt/t:name', namespaces=NS):
        if n.get('ref') == f'contributors.xml#{contrib_id}':
            return False
    # Fix the previous last child's tail: it still has closing_indent
    # (set by migrate_collective_respstmt), but now it's becoming a
    # non-last child and needs child_indent as inter-sibling whitespace.
    if len(title_stmt):
        title_stmt[-1].tail = child_indent
    rs = etree.SubElement(title_stmt, f'{TEI}respStmt')
    rs.text = inner_indent
    rs.tail = child_indent
    rp = etree.SubElement(rs, f'{TEI}resp')
    rp.text = 'Hauptbearbeitung'
    rp.tail = inner_indent
    name = etree.SubElement(
        rs, f'{TEI}name',
        role='lead-editor',
        ref=f'contributors.xml#{contrib_id}'
    )
    name.text = full_name
    name.tail = child_indent
    if len(title_stmt):
        title_stmt[-1].tail = closing_indent
    return True


def main():
    p = argparse.ArgumentParser(
        description='Migrate MHDBDB TEI headers to link editor attribution '
                    'to contributors.xml'
    )
    p.add_argument('--dry-run', action='store_true',
                   help='Preview changes without writing')
    p.add_argument('--sample', nargs='+',
                   help='Limit to specified sigles (e.g. --sample ABG LZT)')
    args = p.parse_args()

    files = sorted(Path('tei').glob('*.tei.xml'))
    if args.sample:
        sample_set = set(args.sample)
        files = [f for f in files if f.name.replace('.tei.xml', '') in sample_set]
        missing = sample_set - {f.name.replace('.tei.xml', '') for f in files}
        if missing:
            print(f'Warning: sample sigles not found: {sorted(missing)}',
                  file=sys.stderr)

    print(f'Processing {len(files)} file(s)...')
    errs = []
    for f in files:
        sigle = f.name.replace('.tei.xml', '')
        try:
            tree = etree.parse(str(f))
            ch1 = migrate_authority(tree)
            ch2 = migrate_collective_respstmt(tree)
            ch3 = add_lead_editor(tree, sigle)
            if args.dry_run:
                print(f'  [DRY] {sigle}: auth={ch1} resp={ch2} lead={ch3}')
            else:
                # NO pretty_print=True — that would reformat the entire
                # document whitespace, generating thousands of noise diffs
                # across all 666 files. The .text/.tail handling in the
                # migrate_* functions ensures inserted elements blend with
                # the existing indentation.
                # standalone=None matches the P0-4 GND-migration baseline
                # (Commit 61a0b4a1a).
                tree.write(str(f), encoding='UTF-8',
                           xml_declaration=True, standalone=None)
                print(f'  [APPLY] {sigle}: auth={ch1} resp={ch2} lead={ch3}')
        except Exception as e:
            errs.append((f, str(e)))
            print(f'  [ERR] {sigle}: {e}', file=sys.stderr)

    print(f'Done. {len(errs)} error(s).')
    return 1 if errs else 0


if __name__ == '__main__':
    sys.exit(main())
