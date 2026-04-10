#!/usr/bin/env python3
"""
Phase H2: Migrate UUID person IDs to numeric + create Schweizer Anonymus

1. Rename 4 UUID-format person IDs to sequential numeric IDs (person_1768+)
2. Update cascade references in works.xml and tei/*.tei.xml
3. Create person_schweizer_anonymus as person_1772 with GND 103130276

UUID persons (from audit):
  person_778d109...  Karl IV.                 → no refs
  person_b30959e...  Rüdeger von Hunchofen    → no refs
  person_c5ec3a1...  Ezzo                     → no refs
  person_0515479...  Albertanus von Brescia    → works.xml (work_563) + tei/LUU.tei.xml

Usage:
    python scripts/data-wrangling/tei-model/authority-files/migrate-person-uuids.py [--dry-run]
"""

import argparse
import logging
import re
import sys
from pathlib import Path
from lxml import etree

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

TEI_NS = 'http://www.tei-c.org/ns/1.0'
TEI = f'{{{TEI_NS}}}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'

PERSONS_FILE = Path('authority-files/persons.xml')
WORKS_FILE = Path('authority-files/works.xml')
TEI_DIR = Path('tei')

# Schweizer Anonymus: confirmed by Katharina (2026-04-10), GND from lobid.org
SCHWEIZER_ANONYMUS = {
    'name': 'Schweizer Anonymus',
    'gnd': '103130276',
}


def find_max_person_id(root):
    """Find highest numeric person ID."""
    max_id = 0
    for person in root.findall(f'.//{TEI}person'):
        pid = person.get(XML_ID, '')
        m = re.match(r'person_(\d+)$', pid)
        if m:
            max_id = max(max_id, int(m.group(1)))
    return max_id


def find_uuid_persons(root):
    """Find persons with UUID-format IDs."""
    uuid_persons = []
    for person in root.findall(f'.//{TEI}person'):
        pid = person.get(XML_ID, '')
        if pid.startswith('person_') and not re.match(r'person_\d+$', pid) and pid != 'person_anonym':
            name_el = person.find(f'{TEI}persName')
            name = name_el.text.strip() if name_el is not None and name_el.text else '?'
            uuid_persons.append((person, pid, name))
    return uuid_persons


def update_refs_in_file(tree, old_id, new_id):
    """Update @ref attributes referencing old_id in a parsed tree. Returns count."""
    count = 0
    root = tree.getroot()
    for elem in root.iter():
        ref = elem.get('ref', '')
        if old_id in ref:
            new_ref = ref.replace(old_id, new_id)
            elem.set('ref', new_ref)
            count += 1
        corresp = elem.get('corresp', '')
        if old_id in corresp:
            new_corresp = corresp.replace(old_id, new_id)
            elem.set('corresp', new_corresp)
            count += 1
    return count


def create_schweizer_anonymus(root, new_id):
    """Create a new <person> element for Schweizer Anonymus."""
    person = etree.Element(f'{TEI}person')
    person.set(XML_ID, new_id)
    person.text = '\n          '

    persName = etree.SubElement(person, f'{TEI}persName')
    persName.set('type', 'preferred')
    persName.text = SCHWEIZER_ANONYMUS['name']
    persName.tail = '\n          '

    gnd = etree.SubElement(person, f'{TEI}idno')
    gnd.set('type', 'GND')
    gnd.text = SCHWEIZER_ANONYMUS['gnd']
    gnd.tail = '\n        '

    # Insert into <listPerson>
    list_person = root.find(f'.//{TEI}listPerson')
    if list_person is not None:
        list_person.append(person)

    return person


def main():
    parser = argparse.ArgumentParser(description='Phase H2: Migrate UUID person IDs + create Schweizer Anonymus')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would change without modifying files')
    args = parser.parse_args()

    if args.dry_run:
        logger.info('DRY RUN — no files will be modified')

    # Parse persons.xml
    xml_parser = etree.XMLParser(remove_blank_text=False)
    persons_tree = etree.parse(str(PERSONS_FILE), xml_parser)
    persons_root = persons_tree.getroot()

    # Find max ID and UUID persons
    max_id = find_max_person_id(persons_root)
    uuid_persons = find_uuid_persons(persons_root)
    logger.info(f'Highest numeric ID: person_{max_id}')
    logger.info(f'UUID persons found: {len(uuid_persons)}')

    # Build rename mapping
    rename_map = {}
    next_id = max_id + 1
    for person, old_id, name in uuid_persons:
        new_id = f'person_{next_id}'
        rename_map[old_id] = new_id
        logger.info(f'  {name}: {old_id[:30]}... -> {new_id}')
        next_id += 1

    # Schweizer Anonymus gets the next ID
    sa_id = f'person_{next_id}'
    logger.info(f'  Schweizer Anonymus (new): {sa_id}')

    if not args.dry_run:
        # 1. Rename in persons.xml
        for person, old_id, name in uuid_persons:
            new_id = rename_map[old_id]
            person.set(XML_ID, new_id)

        # 2. Create Schweizer Anonymus
        create_schweizer_anonymus(persons_root, sa_id)

        # 3. Update old schweizer_anonymus ref in works.xml to new numeric ID
        works_tree = etree.parse(str(WORKS_FILE), xml_parser)
        cascade_works = 0
        for old_id, new_id in rename_map.items():
            cascade_works += update_refs_in_file(works_tree, old_id, new_id)
        # Also update person_schweizer_anonymus -> sa_id
        cascade_works += update_refs_in_file(works_tree, 'person_schweizer_anonymus', sa_id)
        works_tree.write(str(WORKS_FILE), encoding='UTF-8', xml_declaration=True)
        logger.info(f'  works.xml: {cascade_works} refs updated')

        # 4. Update refs in tei/*.tei.xml
        cascade_tei = 0
        for tei_file in sorted(TEI_DIR.glob('*.tei.xml')):
            tei_tree = etree.parse(str(tei_file), xml_parser)
            count = 0
            for old_id, new_id in rename_map.items():
                count += update_refs_in_file(tei_tree, old_id, new_id)
            if count > 0:
                tei_tree.write(str(tei_file), encoding='UTF-8', xml_declaration=True)
                sigle = tei_file.stem.replace('.tei', '')
                logger.info(f'  {sigle}: {count} refs updated')
                cascade_tei += count
        logger.info(f'  tei/ total: {cascade_tei} refs updated')

        # 5. Write persons.xml
        persons_tree.write(str(PERSONS_FILE), encoding='UTF-8', xml_declaration=True)

    logger.info('')
    logger.info(f'{"Would rename" if args.dry_run else "Renamed"} {len(uuid_persons)} UUID persons')
    logger.info(f'{"Would create" if args.dry_run else "Created"} Schweizer Anonymus as {sa_id} (GND {SCHWEIZER_ANONYMUS["gnd"]})')

    return 0


if __name__ == '__main__':
    sys.exit(main())
