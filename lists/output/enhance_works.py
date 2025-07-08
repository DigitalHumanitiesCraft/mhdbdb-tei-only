#!/usr/bin/env python3
import csv
import os
import sys
import logging
import re
from lxml import etree
from collections import defaultdict

# Define namespaces
TEI_NS = "http://www.tei-c.org/ns/1.0"
XML_NS = "http://www.w3.org/XML/1998/namespace"

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("enhance_works")

def _local_id(uri: str) -> str:
    """Extract work ID from URI"""
    if not uri:
        return ""
    return uri.rsplit("/", 1)[-1]

def normalize_title(title: str) -> str:
    """Normalize title for comparison - removes extra whitespace, brackets, punctuation"""
    if not title:
        return ""

    # Remove common bracketing patterns
    normalized = re.sub(r'^\[|\]$', '', title.strip())
    # Normalize whitespace
    normalized = re.sub(r'\s+', ' ', normalized)
    # Remove trailing punctuation for comparison
    normalized = re.sub(r'[.,;:]+$', '', normalized)

    return normalized.lower().strip()

def parse_editors(resp_stmt: str) -> set:
    """
    Enhanced editor parsing with better handling of complex names
    """
    editors = set()

    if not resp_stmt or "herausgegeben von" not in resp_stmt:
        return editors

    # Extract editor text
    editor_text = resp_stmt.replace("herausgegeben von", "").strip()
    if not editor_text:
        return editors

    # Handle different conjunctions
    editor_text = re.sub(r'\s+und\s+', ', ', editor_text)
    editor_text = re.sub(r'\s+&\s+', ', ', editor_text)

    # Split on commas, but be careful about names with commas
    parts = [part.strip() for part in editor_text.split(',')]

    # Simple heuristic: if a part is very short (1-2 chars), it might be
    # part of a name like "Smith, Jr." - combine with previous part
    cleaned_parts = []
    i = 0
    while i < len(parts):
        current = parts[i]

        # Look ahead for short suffixes that might be part of a name
        if i + 1 < len(parts) and len(parts[i + 1]) <= 3 and parts[i + 1] in ['Jr.', 'Sr.', 'II', 'III', 'IV']:
            current += f", {parts[i + 1]}"
            i += 2
        else:
            i += 1

        if current:
            cleaned_parts.append(current)

    for editor in cleaned_parts:
        editor = editor.strip()
        if editor and len(editor) > 1:  # Avoid single characters
            editors.add(editor)

    return editors

def read_print_works_csv(csv_file):
    """Read and process print-works.csv data with enhanced deduplication"""
    print_works_data = defaultdict(lambda: {
        'titles': {},  # Now store both original and normalized
        'editors': set()
    })
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate expected columns
            expected_cols = ['workId', 'responsibilityStatement', 'printTitle']
            missing_cols = [col for col in expected_cols if col not in reader.fieldnames]
            if missing_cols:
                logger.warning(f"Missing expected columns in CSV: {missing_cols}")

            for row_num, row in enumerate(reader, 1):
                work_uri = row.get("workId", "")
                work_id = _local_id(work_uri)
                
                if not work_id:
                    logger.warning(f"Row {row_num}: No valid work ID found")
                    continue
                
                # Parse editors with enhanced logic
                resp_stmt = row.get("responsibilityStatement", "").strip()
                editors = parse_editors(resp_stmt)
                print_works_data[work_id]['editors'].update(editors)
                
                # Handle titles with normalization
                print_title = row.get("printTitle", "").strip()
                if print_title:
                    normalized = normalize_title(print_title)
                    if normalized:  # Only add if normalization results in non-empty string
                        # Store mapping of normalized -> original for deduplication
                        print_works_data[work_id]['titles'][normalized] = print_title
        
        # Log deduplication results
        for work_id, data in print_works_data.items():
            logger.info(f"{work_id}: {len(data['titles'])} unique titles, {len(data['editors'])} unique editors")
            if len(data['titles']) > 0:
                logger.debug(f"  Titles: {list(data['titles'].values())}")
            if len(data['editors']) > 0:
                logger.debug(f"  Editors: {list(data['editors'])}")

        return print_works_data
        
    except Exception as e:
        logger.error(f"Error reading {csv_file}: {e}")
        return {}

def enhance_works_xml(works_xml_file, print_works_csv_file, output_file):
    """Enhance existing works.xml with print works data"""
    
    logger.info(f"Enhancing {works_xml_file} with data from {print_works_csv_file}")
    
    # Load print works data
    print_works_data = read_print_works_csv(print_works_csv_file)
    if not print_works_data:
        logger.warning("No print works data loaded")
        return False
    
    try:
        # Parse existing works.xml
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(works_xml_file, parser)
        root = tree.getroot()
        
        # Find all bibl elements
        bibls = root.findall(f".//{{{TEI_NS}}}bibl[@{{{XML_NS}}}id]")
        logger.info(f"Found {len(bibls)} works in {works_xml_file}")
        
        enhanced_count = 0
        
        for bibl in bibls:
            work_id = bibl.get(f"{{{XML_NS}}}id")
            if not work_id or work_id not in print_works_data:
                continue
            
            data = print_works_data[work_id]
            
            # Find or create edition bibl
            edition_bibl = bibl.find(f".//{{{TEI_NS}}}bibl[@type='edition']")
            if edition_bibl is None:
                # Create new edition bibl
                edition_bibl = etree.SubElement(bibl, f"{{{TEI_NS}}}bibl")
                edition_bibl.set("type", "edition")
            
            # Get existing titles with enhanced normalization
            existing_titles_normalized = set()
            for title_elem in edition_bibl.findall(f"./{{{TEI_NS}}}title"):
                if title_elem.text:
                    title_text = title_elem.text.strip()
                    normalized = normalize_title(title_text)
                    existing_titles_normalized.add(normalized)

                    # Add @ana="bibframe" to existing titles
                    title_elem.set("ana", "bibframe")
                    logger.debug(f"Existing title: '{title_text}' normalized to: '{normalized}'")

            # Add new titles from print works (only if not already present)
            new_titles_added = 0
            for normalized_title, original_title in sorted(data['titles'].items()):

                logger.debug(f"Checking new title: '{original_title}' normalized to: '{normalized_title}'")

                # Check if this title already exists (using normalized comparison)
                if normalized_title not in existing_titles_normalized:
                    title_elem = etree.Element(f"{{{TEI_NS}}}title")
                    title_elem.text = original_title
                    title_elem.set("ana", "print")  # Mark as coming from print data

                    # Insert after existing titles
                    last_title = None
                    for child in edition_bibl:
                        if child.tag == f"{{{TEI_NS}}}title":
                            last_title = child
                    
                    if last_title is not None:
                        last_title.addnext(title_elem)
                    else:
                        edition_bibl.insert(0, title_elem)
                    
                    # Add to set to prevent future duplicates in this run
                    existing_titles_normalized.add(normalized_title)
                    new_titles_added += 1
                    logger.info(f"Added new title: '{original_title}'")
                else:
                    logger.info(f"Skipped duplicate title: '{original_title}' (matches existing)")
            
            # Handle editors (existing logic is fine)
            existing_editors = set()
            for editor_elem in edition_bibl.findall(f"./{{{TEI_NS}}}editor"):
                if editor_elem.text:
                    existing_editors.add(editor_elem.text.strip())
            
            # Add new editors from print works
            new_editors_added = 0
            for editor in sorted(data['editors']):
                if editor not in existing_editors:
                    editor_elem = etree.Element(f"{{{TEI_NS}}}editor")
                    editor_elem.text = editor
                    # Insert after titles but before pubPlace/publisher/date
                    insert_pos = 0
                    for i, child in enumerate(edition_bibl):
                        if child.tag in [f"{{{TEI_NS}}}title", f"{{{TEI_NS}}}editor"]:
                            insert_pos = i + 1
                    
                    edition_bibl.insert(insert_pos, editor_elem)
                    new_editors_added += 1
                    logger.info(f"Added new editor: '{editor}'")
            
            if new_titles_added > 0 or new_editors_added > 0:
                enhanced_count += 1
                logger.info(f"Enhanced {work_id}: +{new_titles_added} titles, +{new_editors_added} editors")
        
        # Write enhanced XML
        enhanced_xml = etree.tostring(
            root, pretty_print=True, encoding='utf-8', xml_declaration=True
        )
        
        with open(output_file, 'wb') as f:
            f.write(enhanced_xml)
        
        logger.info(f"Enhanced {enhanced_count} works. Output written to {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error enhancing works XML: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python enhance_works.py <works.xml> <print-works.csv> <output.xml>")
        print("Example: python enhance_works.py ./lists/output/works.xml ./lists/print-works.csv ./lists/output/works_enhanced.xml")
        sys.exit(1)
    
    works_xml_file = sys.argv[1]
    print_works_csv_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Validate input files exist
    if not os.path.exists(works_xml_file):
        logger.error(f"Works XML file not found: {works_xml_file}")
        sys.exit(1)
    
    if not os.path.exists(print_works_csv_file):
        logger.error(f"Print works CSV file not found: {print_works_csv_file}")
        sys.exit(1)
    
    # Run enhancement
    success = enhance_works_xml(works_xml_file, print_works_csv_file, output_file)
    
    if success:
        logger.info("Enhancement completed successfully!")
    else:
        logger.error("Enhancement failed!")
        sys.exit(1)