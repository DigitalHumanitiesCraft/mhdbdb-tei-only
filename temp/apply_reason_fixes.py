import re
import os
import sys
import argparse
from lxml import etree

def apply_fixes(tei_path, result_dir):
    print(f"Processing {tei_path} using results from {result_dir}...")
    # Parse TEI
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(tei_path, parser)
    root = tree.getroot()
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}
    
    # Read all result files
    reason_map = {}
    # Extract sigle from tei_path filename (e.g., "AC1" from "tei/AC1.disamb.tei.xml")
    sigle = os.path.basename(tei_path).split('.')[0]
    print(f"Looking for result files for sigle: {sigle}")

    for filename in os.listdir(result_dir):
        if filename.endswith("-result.md") and sigle in filename:
            with open(os.path.join(result_dir, filename), 'r', encoding='utf-8') as f:
                for line in f:
                    # Parse line: ID | ... | reason="..."
                    match = re.search(r'^(AC1_\d+_\d+|ABS_\d+_\d+|ABG_\d+_\d+)\s*\|.*?reason="([^"]+)"', line)
                    # Note: The regex above might be too specific with the ID prefixes. 
                    # A more general regex for ID would be better, but let's stick to the pattern.
                    # Actually, let's make it generic for any ID starting with the sigle.
                    if not match:
                         match = re.search(r'^(' + sigle + r'_\d+_\d+)\s*\|.*?reason="([^"]+)"', line)

                    if match:
                        xml_id = match.group(1)
                        reason = match.group(2)
                        reason_map[xml_id] = reason

    print(f"Found {len(reason_map)} reason attributes to apply.")
    
    count = 0
    for xml_id, reason in reason_map.items():
        # Find element
        node = root.xpath(f'//*[@xml:id="{xml_id}"]', namespaces=ns)
        if node:
            w = node[0]
            if w.get('pos') and ' ' in w.get('pos'): # Only apply if compound
                w.set('reason', reason)
                count += 1
            else:
                # print(f"Skipping {xml_id}: pos '{w.get('pos')}' is not compound.")
                pass
        else:
            print(f"Warning: ID {xml_id} not found in XML.")
            
    print(f"Applied {count} reason attributes.")
    
    # Save
    tree.write(tei_path, encoding='UTF-8', xml_declaration=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Apply reason attributes to TEI XML.')
    parser.add_argument('tei_file', help='Path to the TEI XML file')
    parser.add_argument('result_dir', help='Directory containing result files')
    args = parser.parse_args()

    apply_fixes(args.tei_file, args.result_dir)