#!/usr/bin/env python3
"""
Replace corrected titles in works.xml:
1. Delete all titles containing "?" 
2. Add corrected titles from corrected_titles.xml
"""

from lxml import etree
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def parse_xml_file(filename):
    """Parse XML file with namespace handling."""
    try:
        parser = etree.XMLParser(recover=True, remove_blank_text=False)
        tree = etree.parse(filename, parser)
        return tree
    except Exception as e:
        logger.error(f"Error parsing {filename}: {e}")
        raise

def delete_titles_with_question_marks(works_tree):
    """Delete all title elements containing '?' from works.xml."""
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Find all titles containing "?"
    titles_to_delete = works_tree.xpath('//tei:title[contains(text(), "?")]', namespaces=ns)
    
    logger.info(f"Found {len(titles_to_delete)} titles containing '?' to delete")
    
    # Delete them
    for title in titles_to_delete:
        title.getparent().remove(title)
    
    return len(titles_to_delete)

def load_corrected_titles(corrected_titles_file):
    """Load corrected titles from the XML file."""
    logger.info(f"Loading corrected titles from {corrected_titles_file}")
    
    tree = parse_xml_file(corrected_titles_file)
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Extract all title elements
    title_elements = tree.xpath('//tei:title[@work-id]', namespaces=ns)
    
    logger.info(f"Found {len(title_elements)} corrected titles")
    
    return title_elements

def add_corrected_titles_to_works(works_tree, corrected_titles):
    """Add corrected titles to the appropriate works."""
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    titles_added = 0
    works_not_found = 0
    
    for corrected_title in corrected_titles:
        work_id = corrected_title.get('work-id')
        
        # Find the work element
        work_elements = works_tree.xpath(f'//tei:bibl[@xml:id="{work_id}"]', namespaces=ns)
        
        if not work_elements:
            logger.warning(f"Work {work_id} not found in works.xml")
            works_not_found += 1
            continue
        
        work_elem = work_elements[0]
        
        # Create a new title element without the work-id attribute
        new_title = etree.Element(
            '{http://www.tei-c.org/ns/1.0}title',
            nsmap={None: 'http://www.tei-c.org/ns/1.0'}
        )
        
        # Copy all attributes except work-id
        for attr_name, attr_value in corrected_title.attrib.items():
            if attr_name != 'work-id':
                new_title.set(attr_name, attr_value)
        
        # Copy text content
        new_title.text = corrected_title.text
        
        # Copy any child elements if they exist
        for child in corrected_title:
            new_title.append(child)
        
        # Find a good insertion point - after the main title
        main_title = work_elem.xpath('./tei:title[1]', namespaces=ns)
        if main_title:
            # Insert after the main title
            parent = main_title[0].getparent()
            insert_index = list(parent).index(main_title[0]) + 1
            parent.insert(insert_index, new_title)
        else:
            # No main title found, just append to work
            work_elem.append(new_title)
        
        logger.debug(f"Added title to {work_id}: {corrected_title.text}")
        titles_added += 1
    
    logger.info(f"Titles added: {titles_added}")
    logger.info(f"Works not found: {works_not_found}")
    
    return titles_added, works_not_found

def main():
    """Main function to orchestrate the title replacement."""
    works_file = 'works.xml'
    corrected_titles_file = 'corrected_titles.xml'  # Change this to your filename
    
    try:
        # Parse works.xml
        logger.info("Parsing works.xml...")
        works_tree = parse_xml_file(works_file)
        
        # Step 1: Delete titles containing "?"
        logger.info("Deleting titles containing '?'...")
        deleted_count = delete_titles_with_question_marks(works_tree)
        
        # Step 2: Load corrected titles
        corrected_titles = load_corrected_titles(corrected_titles_file)
        
        # Step 3: Add corrected titles to works
        logger.info("Adding corrected titles to works.xml...")
        titles_added, works_not_found = add_corrected_titles_to_works(works_tree, corrected_titles)
        
        # Step 4: Write updated works.xml
        logger.info(f"Writing updated works.xml...")
        works_tree.write(works_file, encoding='utf-8', xml_declaration=True, pretty_print=True)
        
        logger.info("Process completed successfully!")
        logger.info(f"Final summary:")
        logger.info(f"- {deleted_count} titles with '?' deleted")
        logger.info(f"- {titles_added} corrected titles added")
        logger.info(f"- {works_not_found} works not found")
        
        return True
        
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)