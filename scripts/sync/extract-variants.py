#!/usr/bin/env python3
"""
Regenerate authority-files/variants.xml from the current TEI corpus (Issue #44 / #115).

variants.xml is a DERIVED authority file: it maps each orthographic-variant id
(`type_N`) to its surface form, grouped under the lemma it attests. The original
generator (scripts/extract-variants.py on the archived `initial-data-wrangling`
branch) read the pre-#32 compound `@wordRef`; #32 migrated that to
`@corresp="variants.xml#type_N"`, so the old script no longer runs and the file
drifted (64,287 forms missing as of 2026-05). This is the maintained, post-#32
replacement.

Per <w> with @lemmaRef and a variants @corresp it records (lemma, type, form):
  <w lemmaRef="lexicon.xml#lemma_7672" corresp="variants.xml#type_93122">wißent</w>
  -> entry lemma_7672 / <form xml:id="type_93122">wißent</form>

xml:id uniqueness: a `type_N` is one orthographic form of one lemma. If the
corpus attests a type id with more than one form or under more than one lemma
(noise), the most frequent wins (ties: smallest lemma number / alphabetical
form) so each type id is emitted exactly once. Such collisions are reported.

Negative type ids (legacy punctuation codes, #115) are skipped. The two
`<?xml-model?>` PIs (added in #32) are preserved.

Usage:
    python scripts/sync/extract-variants.py            # dry-run -> authority-files/variants.regen.xml
    python scripts/sync/extract-variants.py --apply    # overwrite authority-files/variants.xml
"""

import io
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from lxml import etree

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'
XML = '{http://www.w3.org/XML/1998/namespace}'

TEI_DIR = Path('tei')
VARIANTS = Path('authority-files/variants.xml')
DRY_OUT = Path('authority-files/variants.regen.xml')

TYPE_POS_RE = re.compile(r'^type_\d+$')        # positive type id only
TYPE_NUM_RE = re.compile(r'^type_(\d+)$')
LEMMA_NUM_RE = re.compile(r'^lemma_(\d+)$')

PI_MODEL = [
    ('xml-model', 'href="../schema/mhdbdb-authority.rng" type="application/xml" schematypens="http://relaxng.org/ns/structure/1.0"'),
    ('xml-model', 'href="https://tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"'),
]


def fragment(value):
    """'lexicon.xml#lemma_7672' -> 'lemma_7672' (first whitespace token)."""
    tok = value.split()[0] if value else ''
    return tok.split('#', 1)[1] if '#' in tok else None


def collect(base_files):
    """type_id -> Counter(form), type_id -> Counter(lemma_id)."""
    type_form = defaultdict(Counter)
    type_lemma = defaultdict(Counter)
    for i, fp in enumerate(base_files):
        if (i + 1) % 100 == 0:
            print(f'  {i + 1}/{len(base_files)}...', flush=True)
        tree = etree.parse(str(fp))
        for w in tree.iter(f'{TEI}w'):
            lemma_ref = w.get('lemmaRef')
            corresp = w.get('corresp')
            if not lemma_ref or not corresp:
                continue
            lemma_id = fragment(lemma_ref)
            if not lemma_id:
                continue
            form = ''.join(w.itertext()).strip()
            if not form:
                continue
            for token in corresp.split():
                if not token.startswith('variants.xml#'):
                    continue
                type_id = token.split('#', 1)[1]
                if not TYPE_POS_RE.match(type_id):
                    continue  # negative/malformed -> skip (#115)
                type_form[type_id][form] += 1
                type_lemma[type_id][lemma_id] += 1
    return type_form, type_lemma


def resolve(type_form, type_lemma):
    """Pick one lemma + one form per type id.

    Return (lemma_to_types, type_to_form, type_to_lemma, multi_form, multi_lemma).
    type_to_lemma lets the diff look up a type's lemma in O(1) instead of scanning
    lemma_to_types per type (which was O(types x lemmas) and hung the run).
    """
    lemma_to_types = defaultdict(list)
    type_to_form = {}
    type_to_lemma = {}
    multi_form = multi_lemma = 0
    for type_id in type_form:
        forms = type_form[type_id]
        lemmas = type_lemma[type_id]
        if len(forms) > 1:
            multi_form += 1
        if len(lemmas) > 1:
            multi_lemma += 1
        # most frequent; ties -> alphabetical form / smallest lemma number
        form = sorted(forms.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]
        lemma = sorted(lemmas.items(), key=lambda kv: (-kv[1], int(LEMMA_NUM_RE.match(kv[0]).group(1)) if LEMMA_NUM_RE.match(kv[0]) else 1 << 62))[0][0]
        type_to_form[type_id] = form
        type_to_lemma[type_id] = lemma
        lemma_to_types[lemma].append(type_id)
    return lemma_to_types, type_to_form, type_to_lemma, multi_form, multi_lemma


def lemma_key(lemma_id):
    m = LEMMA_NUM_RE.match(lemma_id)
    return (0, int(m.group(1))) if m else (1, lemma_id)


def type_key(type_id):
    m = TYPE_NUM_RE.match(type_id)
    return int(m.group(1)) if m else 1 << 62


def build_tree(lemma_to_types, type_to_form, n_files, date_text):
    root = etree.Element(f'{TEI}TEI', nsmap={None: TEI_NS})
    header = etree.SubElement(root, f'{TEI}teiHeader')
    fileDesc = etree.SubElement(header, f'{TEI}fileDesc')
    titleStmt = etree.SubElement(fileDesc, f'{TEI}titleStmt')
    etree.SubElement(titleStmt, f'{TEI}title').text = 'MHDBDB Orthographic Variants Index'
    respStmt = etree.SubElement(titleStmt, f'{TEI}respStmt')
    etree.SubElement(respStmt, f'{TEI}resp').text = 'Extracted from'
    etree.SubElement(respStmt, f'{TEI}name').text = f'MHDBDB TEI Corpus ({n_files} texts)'
    pubStmt = etree.SubElement(fileDesc, f'{TEI}publicationStmt')
    etree.SubElement(pubStmt, f'{TEI}publisher').text = 'MHDBDB'
    # Semantik: <date> = Stand der Daten, nicht letzter Script-Lauf — siehe main()
    etree.SubElement(pubStmt, f'{TEI}date').text = date_text
    sourceDesc = etree.SubElement(fileDesc, f'{TEI}sourceDesc')
    etree.SubElement(sourceDesc, f'{TEI}p').text = 'Automatically extracted attestations from TEI corpus'

    text = etree.SubElement(root, f'{TEI}text')
    body = etree.SubElement(text, f'{TEI}body')
    div = etree.SubElement(body, f'{TEI}div')
    div.set('type', 'orthographicVariants')

    for lemma_id in sorted(lemma_to_types, key=lemma_key):
        entry = etree.SubElement(div, f'{TEI}entry')
        entry.set('corresp', f'lexicon.xml#{lemma_id}')
        for type_id in sorted(lemma_to_types[lemma_id], key=type_key):
            form = etree.SubElement(entry, f'{TEI}form')
            form.set(f'{XML}id', type_id)
            form.text = type_to_form[type_id]

    tree = etree.ElementTree(root)
    for target, content in PI_MODEL:
        root.addprevious(etree.ProcessingInstruction(target, content))
    return tree


def existing_date():
    """<date> der bestehenden variants.xml, oder None (Datei fehlt/kein date)."""
    if not VARIANTS.exists():
        return None
    tree = etree.parse(str(VARIANTS))
    el = tree.find(f'{TEI}teiHeader/{TEI}fileDesc/{TEI}publicationStmt/{TEI}date')
    return el.text if el is not None and el.text else None


def current_map():
    """type_id -> (lemma_id, form) from the existing variants.xml, for diffing."""
    if not VARIANTS.exists():
        return {}
    out = {}
    tree = etree.parse(str(VARIANTS))
    for entry in tree.iter(f'{TEI}entry'):
        lemma_id = fragment(entry.get('corresp') or '')
        for form in entry.findall(f'{TEI}form'):
            tid = form.get(f'{XML}id')
            if tid:
                out[tid] = (lemma_id, (form.text or '').strip())
    return out


def main():
    apply = '--apply' in sys.argv
    base_files = sorted(f for f in TEI_DIR.glob('*.tei.xml') if '.disamb.' not in f.name)
    print(f'Scanning {len(base_files)} corpus files for <w @lemmaRef @corresp>...')
    type_form, type_lemma = collect(base_files)
    lemma_to_types, type_to_form, type_to_lemma, multi_form, multi_lemma = resolve(type_form, type_lemma)

    n_types = len(type_to_form)
    n_lemmas = len(lemma_to_types)

    # diff vs current
    cur = current_map()
    new_ids = set(type_to_form)
    cur_ids = set(cur)
    added = new_ids - cur_ids
    removed = cur_ids - new_ids
    form_changed = sum(1 for t in (new_ids & cur_ids) if cur[t][1] != type_to_form[t])
    lemma_changed = sum(1 for t in (new_ids & cur_ids) if cur[t][0] != type_to_lemma[t])

    # Datum nur bei inhaltlicher Aenderung (#125): erst mit dem bestehenden
    # <date> serialisieren; ist das Ergebnis byte-identisch zur committeten
    # Datei, bleibt das Datum stehen (No-op-Lauf erzeugt keinen Diff).
    # Sonst heutiges Datum. <date> bedeutet damit "Stand der Daten".
    old_date = existing_date()
    today = date.today().isoformat()
    tree = build_tree(lemma_to_types, type_to_form, len(base_files), old_date or today)
    buf = io.BytesIO()
    tree.write(buf, xml_declaration=True, encoding='UTF-8', pretty_print=True)
    if old_date is not None and buf.getvalue() != VARIANTS.read_bytes():
        d = tree.find(f'{TEI}teiHeader/{TEI}fileDesc/{TEI}publicationStmt/{TEI}date')
        d.text = today
    out = VARIANTS if apply else DRY_OUT
    tree.write(str(out), xml_declaration=True, encoding='UTF-8', pretty_print=True)

    mode = 'APPLIED -> authority-files/variants.xml' if apply else f'DRY-RUN -> {out}'
    print('=' * 60)
    print(f'Regenerate variants.xml  [{mode}]')
    print('=' * 60)
    print(f'Distinct type ids (forms):  {n_types:>9,}')
    print(f'Distinct lemmas (entries):  {n_lemmas:>9,}')
    print(f'Current variants.xml:       {len(cur):>9,} type ids')
    print()
    print(f'  added (new in corpus):    {len(added):>9,}')
    print(f'  removed (gone from corpus):{len(removed):>8,}')
    print(f'  form text changed:        {form_changed:>9,}')
    print(f'  lemma assignment changed: {lemma_changed:>9,}')
    print()
    print(f'Data-quality (resolved by majority):')
    print(f'  type ids with >1 form:    {multi_form:>9,}')
    print(f'  type ids with >1 lemma:   {multi_lemma:>9,}')
    if not apply:
        print(f'\nDry-run only. Inspect {out}, then re-run with --apply.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
