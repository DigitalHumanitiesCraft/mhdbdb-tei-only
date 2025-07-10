#!/usr/bin/env python3
"""
TEI XML Alternate Titles Adder

Reads work-addons files and adds alternate titles to works.xml based on
label elements with labelImportance != "primary" and labelGiver != "false".

The script can be run multiple times safely - it removes any existing
alternate titles before adding new ones, preventing duplicates.

Features text normalization (whitespace cleanup).
"""

import os
import re
from lxml import etree
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def parse_xml_file(filename):
    """Parse XML file with namespace handling."""
    try:
        # Use a more lenient parser
        parser = etree.XMLParser(recover=True, remove_blank_text=False)
        tree = etree.parse(filename, parser)
        return tree
    except Exception as e:
        logger.error(f"Error parsing {filename}: {e}")
        raise

def normalize_text(text):
    """Normalize text by collapsing multiple whitespace into single spaces."""
    if not text:
        return text
    # Replace multiple whitespace (spaces, tabs, newlines) with single spaces
    normalized = re.sub(r'\s+', ' ', text.strip())
    return normalized

def extract_alternate_labels(addon_file_path):
    """Extract alternate labels from a work-addons file."""
    if not os.path.exists(addon_file_path):
        return []
    
    try:
        tree = parse_xml_file(addon_file_path)
        ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
        
        # Find all label elements that are not primary and don't have labelGiver="false"
        labels = tree.xpath('//tei:label[@labelImportance!="primary" and @labelGiver!="false"]', namespaces=ns)
        
        alternate_titles = []
        
        for label in labels:
            # Extract attributes
            lang = label.get('lang', 'unknown')
            label_giver = label.get('labelGiver', 'unknown')
            label_text = label.text.strip() if label.text else ''
            
            if not label_text:
                logger.warning(f"Empty label text in {addon_file_path}")
                continue
            
            # Normalize text content
            label_text = normalize_text(label_text)

            # Log missing attributes
            if lang == 'unknown':
                logger.warning(f"Missing lang attribute in {addon_file_path}")
            if label_giver == 'unknown':
                logger.warning(f"Missing labelGiver attribute in {addon_file_path}")
            
            alternate_titles.append({
                'lang': lang,
                'ana': label_giver,
                'text': label_text
            })
        
        return alternate_titles
        
    except Exception as e:
        logger.error(f"Error processing {addon_file_path}: {e}")
        return []

def add_alternate_titles_to_work(work_elem, alternate_titles):
    """Add alternate title elements to a work element."""
    if not alternate_titles:
        return 0
    
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Find the main title element
    main_title = work_elem.xpath('./tei:title[1]', namespaces=ns)
    if not main_title:
        logger.warning("No main title found in work element")
        return 0
    
    main_title_elem = main_title[0]
    parent = main_title_elem.getparent()
    
    # Find insertion point (after main title)
    insert_index = list(parent).index(main_title_elem) + 1
    
    # Create and insert alternate title elements
    titles_added = 0
    
    for i, alt_title in enumerate(alternate_titles):
        # Create new title element
        title_elem = etree.Element(
            '{http://www.tei-c.org/ns/1.0}title',
            nsmap={None: 'http://www.tei-c.org/ns/1.0'}
        )
        
        # Set attributes
        title_elem.set('{http://www.w3.org/XML/1998/namespace}lang', alt_title['lang'])
        title_elem.set('type', 'alternate')
        title_elem.set('ana', alt_title['ana'])
        
        # Set text content
        title_elem.text = alt_title['text']
        
        # Insert at appropriate position
        parent.insert(insert_index + i, title_elem)
        titles_added += 1
    
    return titles_added

def add_alternate_titles_to_works(works_tree, work_addons_dir):
    """Add alternate titles to all works in the tree."""
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Find all work entries
    works = works_tree.xpath('//tei:bibl[starts-with(@xml:id, "work_")]', namespaces=ns)
    logger.info(f"Found {len(works)} work entries")
    
    total_titles_added = 0
    total_titles_removed = 0
    works_processed = 0
    missing_files = []
    
    for work in works:
        work_id = work.get('{http://www.w3.org/XML/1998/namespace}id', 'unknown')
        
        # FIRST: Remove any existing alternate titles to avoid duplicates
        existing_alt_titles = work.xpath('.//tei:title[@type="alternate"]', namespaces=ns)
        if existing_alt_titles:
            logger.debug(f"Removing {len(existing_alt_titles)} existing alternate titles from {work_id}")
            for existing_title in existing_alt_titles:
                existing_title.getparent().remove(existing_title)
            total_titles_removed += len(existing_alt_titles)

        # Extract work number from work_id (e.g., "work_294" -> "294")
        if work_id.startswith('work_'):
            work_number = work_id[5:]  # Remove "work_" prefix
        else:
            logger.warning(f"Invalid work ID format: {work_id}")
            continue
        
        # Construct addon file path
        addon_file_path = os.path.join(work_addons_dir, f"work_{work_number}.xml")
        
        if not os.path.exists(addon_file_path):
            missing_files.append(work_id)
            logger.debug(f"Missing addon file for {work_id}: {addon_file_path}")
            continue
        
        # Extract alternate titles from addon file
        alternate_titles = extract_alternate_labels(addon_file_path)
        
        if alternate_titles:
            # Add alternate titles to the work
            titles_added = add_alternate_titles_to_work(work, alternate_titles)
            total_titles_added += titles_added
            works_processed += 1
            logger.debug(f"Added {titles_added} alternate titles to {work_id}")
        else:
            logger.debug(f"No alternate titles found for {work_id}")
    
    # Log summary
    logger.info(f"Processing summary:")
    logger.info(f"- Existing alternate titles removed: {total_titles_removed}")
    logger.info(f"- New alternate titles added: {total_titles_added}")
    logger.info(f"- Works with alternate titles: {works_processed}")
    logger.info(f"- Missing addon files: {len(missing_files)}")
    
    if missing_files:
        logger.warning("Works with missing addon files:")
        for missing in missing_files[:10]:  # Show first 10
            logger.warning(f"  {missing}")
        if len(missing_files) > 10:
            logger.warning(f"  ... and {len(missing_files) - 10} more")
    
    return total_titles_added, works_processed, missing_files

def main():
    """Main function to orchestrate the title addition process."""
    works_file = 'works.xml'
    work_addons_dir = 'work-addons'
    
    try:
        # Check if work-addons directory exists
        if not os.path.exists(work_addons_dir):
            logger.error(f"work-addons directory not found: {work_addons_dir}")
            return False
        
        # Parse works.xml
        logger.info("Parsing works.xml...")
        works_tree = parse_xml_file(works_file)
        
        # Process alternate titles
        logger.info("Processing alternate titles from work-addons files...")
        total_titles_added, works_processed, missing_files = add_alternate_titles_to_works(works_tree, work_addons_dir)
        
        # Write modified XML back to file
        logger.info(f"Writing modified XML back to {works_file}...")
        works_tree.write(works_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
        
        logger.info("Process completed successfully!")
        logger.info(f"Final summary:")
        logger.info(f"- {total_titles_added} new alternate titles added")
        logger.info(f"- {works_processed} works modified")
        logger.info(f"- {len(missing_files)} works with missing addon files")
        logger.info("Script can be run multiple times safely - existing alternate titles are removed before adding new ones")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)