#!/usr/bin/env python3
"""
TEI XML Bibliography Replacer

Replaces <bibl type="edition"> elements in works.xml with <biblStruct> elements
from zotero-export.xml, matching on sigle/callNumber values.

The script can be run multiple times safely - it removes any existing biblStruct 
elements before adding new ones, preventing duplicates when new Zotero data is available.

The script also handles xml:id conflicts from Zotero exports by automatically
generating unique xml:id values when duplicates are detected.
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

def make_xml_id_unique(original_id, used_ids, sigle=None):
    """Generate a unique xml:id based on the original, avoiding conflicts."""
    if not original_id:
        # If no original ID, create one based on sigle
        base_id = f"biblStruct_{sigle}" if sigle else "biblStruct_unknown"
    else:
        base_id = original_id

    # If the original ID is unique, use it
    if base_id not in used_ids:
        used_ids.add(base_id)
        return base_id

    # If there's a conflict, try adding the sigle
    if sigle and f"{base_id}_{sigle}" not in used_ids:
        unique_id = f"{base_id}_{sigle}"
        used_ids.add(unique_id)
        return unique_id

    # If still conflicts, use a counter
    counter = 1
    while f"{base_id}_{counter}" in used_ids:
        counter += 1

    unique_id = f"{base_id}_{counter}"
    used_ids.add(unique_id)
    return unique_id

def replace_editions_with_biblstructs(works_tree, zotero_data):
    """Replace bibl type='edition' elements with matching biblStruct elements."""
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Track used xml:id values across the entire document to ensure uniqueness
    used_xml_ids = set()

    # First, collect all existing xml:id values in the document
    existing_ids = works_tree.xpath('//@xml:id', namespaces={'xml': 'http://www.w3.org/XML/1998/namespace'})
    for existing_id in existing_ids:
        used_xml_ids.add(existing_id)

    # Find all work entries
    works = works_tree.xpath('//tei:bibl[starts-with(@xml:id, "work_")]', namespaces=ns)
    logger.info(f"Found {len(works)} work entries")
    logger.info(f"Found {len(used_xml_ids)} existing xml:id values in document")
    
    total_replacements = 0
    works_with_replacements = 0
    missing_sigles = []
    total_removed = 0
    id_conflicts_fixed = 0
    
    for work in works:
        work_id = work.get('{http://www.w3.org/XML/1998/namespace}id', 'unknown')
        logger.debug(f"Processing work: {work_id}")
        
        # FIRST: Remove any existing biblStruct elements to avoid duplicates
        existing_biblstructs = work.xpath('.//tei:biblStruct', namespaces=ns)
        if existing_biblstructs:
            logger.debug(f"Removing {len(existing_biblstructs)} existing biblStruct elements from {work_id}")
            for existing_bs in existing_biblstructs:
                existing_bs.getparent().remove(existing_bs)
            total_removed += len(existing_biblstructs)
        
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

                    # Fix xml:id conflicts
                    original_id = biblstruct_copy.get('{http://www.w3.org/XML/1998/namespace}id')
                    if original_id and original_id in used_xml_ids:
                        new_id = make_xml_id_unique(original_id, used_xml_ids, sigle)
                        biblstruct_copy.set('{http://www.w3.org/XML/1998/namespace}id', new_id)
                        logger.debug(f"Fixed xml:id conflict: {original_id} -> {new_id}")
                        id_conflicts_fixed += 1
                    elif original_id:
                        used_xml_ids.add(original_id)

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
    logger.info(f"- Existing biblStruct elements removed: {total_removed}")
    logger.info(f"- New biblStruct elements added: {total_replacements}")
    logger.info(f"- xml:id conflicts fixed: {id_conflicts_fixed}")
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
        logger.info(f"- {total_replacements} new biblStruct elements added")
        logger.info(f"- {works_with_replacements} works modified")
        logger.info(f"- {len(missing_sigles)} sigles without matches")
        logger.info("Script can be run multiple times safely - existing biblStruct elements are removed before adding new ones")
        logger.info("xml:id conflicts from Zotero export are automatically resolved")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)