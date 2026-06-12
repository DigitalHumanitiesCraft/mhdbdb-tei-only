#!/usr/bin/env python3
"""
Fix 640 <w> elements in WZB.lemma-autofill.tei.xml where the form 'in' was
incorrectly lemmatized as the preposition lemma_3028 (PRP) but is actually the
personal pronoun 'in' = ihnen/ihn (PRO).

Heuristic disambiguation:
  - Immediately preceded by a preposition (czu/zu/mit/von/bei/vor/an/ouf) → dat.
    plural 'ihnen' → lemma_5454 (sie, PRO)
  - Otherwise → acc. singular 'ihn' → lemma_1517 (er, PRO)

Both lemma_1517 and lemma_5454 have exactly one sense, so @meaningRef is
auto-assigned without disambiguation.

Source of xml_ids: all ABSTAIN rows for lemma_3028 in the Phase 3 pending TSV.
"""
import csv, re, sys
from pathlib import Path
from lxml import etree

sys.stdout.reconfigure(encoding='utf-8')

PROJECT = Path(__file__).parent.parent
PENDING = PROJECT / 'Wenzelsbibel' / 'phase3' / 'wzb-sense-pending.tsv'
TEI     = PROJECT / 'Wenzelsbibel' / 'WZB.lemma-autofill.tei.xml'
NS      = 'http://www.tei-c.org/ns/1.0'
XMLNS   = 'http://www.w3.org/XML/1998/namespace'

# Pronoun lemma assignments
LEMMA_ER  = 'lexicon.xml#lemma_1517'   # er/ihn — acc. singular
LEMMA_SIE = 'lexicon.xml#lemma_5454'   # sie/ihnen — dat. plural

MEANING_ER  = 'lexicon.xml#lemma_1517_sense_2355'
MEANING_SIE = 'lexicon.xml#lemma_5454_sense_8506'

# Patterns that indicate dative plural (zu ihnen, mit ihnen, etc.)
DAT_PREPS = re.compile(
    r'\b(czu|zu|mit|von|ous|vor|bei|an|ouf|durch|vmb|vmbe)\s+\[in\]', re.IGNORECASE)
# Verbs that take dative objects (indirect object = ihnen)
DAT_VERBS = re.compile(
    r'\b(gab|gaben|gib|gibt|sagte|sprich|sprach|sprachen|gebot|geboten|'
    r'befal|befalh|antwurte|antwortete|zeiget|czeigete|leret|lehrete)\s+\[in\]',
    re.IGNORECASE)


def classify(ctx: str) -> tuple[str, str]:
    """Return (lemmaRef, meaningRef) for the token."""
    if DAT_PREPS.search(ctx) or DAT_VERBS.search(ctx):
        return LEMMA_SIE, MEANING_SIE
    return LEMMA_ER, MEANING_ER


def main(dry_run: bool = False):
    # 1. Collect ABSTAIN xml_ids from pending TSV
    abstain_ids: dict[str, tuple[str, str]] = {}  # xml_id -> (lemmaRef, meaningRef)
    with PENDING.open(encoding='utf-8') as f:
        for row in csv.DictReader(f, delimiter='\t'):
            if (row['lemmaRef'] == 'lexicon.xml#lemma_3028'
                    and row.get('resolved_sense', '').strip() == 'ABSTAIN'):
                lemma_ref, meaning_ref = classify(row['context'])
                abstain_ids[row['xml_id']] = (lemma_ref, meaning_ref)

    print(f'ABSTAIN tokens to fix: {len(abstain_ids)}')
    sie_count = sum(1 for v in abstain_ids.values() if v[0] == LEMMA_SIE)
    er_count  = sum(1 for v in abstain_ids.values() if v[0] == LEMMA_ER)
    print(f'  -> lemma_5454 (ihnen, dat.pl.): {sie_count}')
    print(f'  -> lemma_1517 (ihn,  acc.sg.):  {er_count}')

    if not abstain_ids:
        print('Nothing to do.')
        return

    # 2. Parse TEI
    print(f'Parsing {TEI.name} ...')
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(TEI), parser)

    # 3. Fix each <w> element
    fixed = 0
    not_found = 0
    for w in tree.iter(f'{{{NS}}}w'):
        wid = w.get(f'{{{XMLNS}}}id', '')
        if wid not in abstain_ids:
            continue
        lemma_ref, meaning_ref = abstain_ids[wid]
        w.set('lemmaRef', lemma_ref)
        w.set('pos', 'PRO')
        w.set('meaningRef', meaning_ref)
        # Remove wordRef if present (variants.xml has no entry for pronouns)
        if 'wordRef' in w.attrib:
            del w.attrib['wordRef']
        fixed += 1

    not_found = len(abstain_ids) - fixed
    print(f'Fixed: {fixed}  |  Not found in TEI: {not_found}')

    if dry_run:
        print('DRY RUN — no changes written.')
        return

    # 4. Write TEI
    tree.write(str(TEI), encoding='utf-8', xml_declaration=True,
               pretty_print=False)
    print(f'TEI written to {TEI.name}')


if __name__ == '__main__':
    import argparse
    p = argparse.ArgumentParser(description='Fix pronoun in-lemma mismatches in WZB TEI.')
    p.add_argument('--dry-run', action='store_true')
    args = p.parse_args()
    main(dry_run=args.dry_run)
