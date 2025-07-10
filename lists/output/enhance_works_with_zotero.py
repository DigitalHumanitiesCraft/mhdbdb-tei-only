#!/usr/bin/env python3
"""
TEI XML Bibliography Replacer

Replaces <bibl type="edition"> elements in works.xml with <biblStruct> elements
from zotero-export.xml, matching on sigle/callNumber values.
"""

from lxml import etree
from collections import defaultdict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def parse_xml_file(filename):
    """Parse XML file with namespace handling."""
    try:
        # Use a more lenient parser that doesn't validate IDs
        parser = etree.XMLParser(recover=True, remove_blank_text=False)
        tree = etree.parse(filename, parser)
        return tree
    except Exception as e:
        logger.error(f"Error parsing {filename}: {e}")
        raise

def extract_zotero_data(zotero_tree):
    """Extract biblStruct elements indexed by callNumber from Zotero export."""
    # Define namespace
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Dictionary to store callNumber -> list of biblStruct elements
    zotero_data = defaultdict(list)

    # Find all biblStruct elements
    biblstructs = zotero_tree.xpath('//tei:biblStruct', namespaces=ns)
    logger.info(f"Found {len(biblstructs)} biblStruct elements in Zotero export")

    for biblstruct in biblstructs:
        # Find callNumber idno
        call_numbers = biblstruct.xpath('.//tei:idno[@type="callNumber"]', namespaces=ns)

        for call_num_elem in call_numbers:
            call_number = call_num_elem.text.strip() if call_num_elem.text else None
            if call_number:
                # Make a deep copy of the biblStruct element
                biblstruct_copy = etree.fromstring(etree.tostring(biblstruct))
                zotero_data[call_number].append(biblstruct_copy)
                logger.debug(f"Added biblStruct for callNumber: {call_number}")

    logger.info(f"Indexed {len(zotero_data)} unique callNumbers")
    return zotero_data

def extract_work_sigles(work_elem):
    """Extract all sigle values from a work element."""
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    sigle_elements = work_elem.xpath('.//tei:idno[@type="sigle"]', namespaces=ns)
    sigles = []

    for sigle_elem in sigle_elements:
        sigle = sigle_elem.text.strip() if sigle_elem.text else None
        if sigle:
            sigles.append(sigle)

    return sigles

def replace_editions_with_biblstructs(works_tree, zotero_data):
    """Replace bibl type='edition' elements with matching biblStruct elements."""
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    # Find all work entries
    works = works_tree.xpath('//tei:bibl[starts-with(@xml:id, "work_")]', namespaces=ns)
    logger.info(f"Found {len(works)} work entries")

    total_replacements = 0
    works_with_replacements = 0
    missing_sigles = []

    for work in works:
        work_id = work.get('{http://www.w3.org/XML/1998/namespace}id', 'unknown')
        logger.debug(f"Processing work: {work_id}")

        # Extract all sigles for this work
        sigles = extract_work_sigles(work)
        if not sigles:
            logger.warning(f"No sigles found for work {work_id}")
            continue

        logger.debug(f"Work {work_id} has sigles: {sigles}")

        # Find matching biblStruct elements for any of the sigles
        matching_biblstructs = []
        matched_sigles = set()

        for sigle in sigles:
            if sigle in zotero_data:
                for biblstruct in zotero_data[sigle]:
                    # Add key attribute with the matching sigle
                    biblstruct_copy = etree.fromstring(etree.tostring(biblstruct))
                    biblstruct_copy.set('key', sigle)
                    matching_biblstructs.append(biblstruct_copy)
                    matched_sigles.add(sigle)
                    logger.debug(f"Found match for sigle {sigle}")
            else:
                missing_sigles.append(f"{work_id}: {sigle}")

        # Find existing edition elements
        edition_elements = work.xpath('.//tei:bibl[@type="edition"]', namespaces=ns)

        if matching_biblstructs:
            works_with_replacements += 1

            if edition_elements:
                # Replace existing edition elements
                logger.debug(f"Replacing {len(edition_elements)} edition elements with {len(matching_biblstructs)} biblStruct elements")

                # Insert new biblStruct elements at the position of the first edition element
                first_edition = edition_elements[0]
                parent = first_edition.getparent()
                insert_index = list(parent).index(first_edition)

                # Remove all existing edition elements
                for edition_elem in edition_elements:
                    edition_elem.getparent().remove(edition_elem)

                # Insert biblStruct elements
                for i, biblstruct in enumerate(matching_biblstructs):
                    parent.insert(insert_index + i, biblstruct)
                    total_replacements += 1
            else:
                # No existing edition elements, add biblStruct elements at the end
                logger.debug(f"No existing edition elements, adding {len(matching_biblstructs)} biblStruct elements at end")
                for biblstruct in matching_biblstructs:
                    work.append(biblstruct)
                    total_replacements += 1

        elif edition_elements:
            # No matches found, keep existing editions and log
            logger.debug(f"No matches found for work {work_id}, keeping existing {len(edition_elements)} edition elements")

    # Log summary
    logger.info(f"Replacement summary:")
    logger.info(f"- Total biblStruct elements added: {total_replacements}")
    logger.info(f"- Works with replacements: {works_with_replacements}")
    logger.info(f"- Missing sigles: {len(missing_sigles)}")

    if missing_sigles:
        logger.warning("Sigles with no matching callNumber in Zotero data:")
        for missing in missing_sigles:
            logger.warning(f"  {missing}")

    return total_replacements, works_with_replacements, missing_sigles

def main():
    """Main function to orchestrate the replacement process."""
    works_file = 'works.xml'
    zotero_file = 'zotero-export.xml'

    try:
        # Parse XML files
        logger.info("Parsing XML files...")
        works_tree = parse_xml_file(works_file)
        zotero_tree = parse_xml_file(zotero_file)

        # Extract Zotero data
        logger.info("Extracting Zotero bibliography data...")
        zotero_data = extract_zotero_data(zotero_tree)

        # Replace editions with biblStruct elements
        logger.info("Replacing edition elements with biblStruct elements...")
        total_replacements, works_with_replacements, missing_sigles = replace_editions_with_biblstructs(works_tree, zotero_data)

        # Write modified XML back to file
        logger.info(f"Writing modified XML back to {works_file}...")
        works_tree.write(works_file, encoding='utf-8', xml_declaration=True, pretty_print=True)

        logger.info("Process completed successfully!")
        logger.info(f"Final summary:")
        logger.info(f"- {total_replacements} biblStruct elements added")
        logger.info(f"- {works_with_replacements} works modified")
        logger.info(f"- {len(missing_sigles)} sigles without matches")

        return True

    except Exception as e:
        logger.error(f"Error during processing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)