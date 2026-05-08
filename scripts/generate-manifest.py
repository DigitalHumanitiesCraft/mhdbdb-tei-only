#!/usr/bin/env python3
"""
Generate manifest.json for MHDBDB TEI corpus
Extracts metadata from all 667 TEI files in tei/ directory
"""

import os
import json
from datetime import datetime
from lxml import etree

TEI_DIR = 'tei'
OUTPUT_FILE = 'tei/manifest.json'
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def extract_metadata(filepath):
    """Extract basic metadata from TEI header"""
    try:
        tree = etree.parse(filepath)

        # Extract sigle
        sigle_nodes = tree.xpath('//tei:idno[@type="sigle"]/text()', namespaces=TEI_NS)
        sigle = sigle_nodes[0].strip() if sigle_nodes else ''

        # Extract title
        title_nodes = tree.xpath('//tei:titleStmt/tei:title[@xml:lang="de"]/text()', namespaces=TEI_NS)
        title = title_nodes[0].strip() if title_nodes else ''

        # Extract author name
        author_nodes = tree.xpath('//tei:titleStmt/tei:author/text()', namespaces=TEI_NS)
        author = author_nodes[0].strip() if author_nodes else ''

        # Extract author ref
        author_ref_nodes = tree.xpath('//tei:titleStmt/tei:author/@ref', namespaces=TEI_NS)
        author_ref = author_ref_nodes[0] if author_ref_nodes else ''

        # Extract work ref
        work_ref_nodes = tree.xpath('//tei:msIdentifier/@corresp', namespaces=TEI_NS)
        work_ref = work_ref_nodes[0] if work_ref_nodes else ''

        # Get file size
        file_size = os.path.getsize(filepath)

        return {
            'filename': os.path.basename(filepath),
            'path': filepath.replace('\\', '/'),  # Normalize path for web
            'sigle': sigle,
            'title': title,
            'author': author,
            'authorRef': author_ref,
            'workRef': work_ref,
            'size': file_size
        }
    except Exception as e:
        print(f'[WARNING] Error processing {filepath}: {e}')
        return {
            'filename': os.path.basename(filepath),
            'path': filepath.replace('\\', '/'),
            'sigle': '',
            'title': '',
            'author': '',
            'authorRef': '',
            'workRef': '',
            'size': os.path.getsize(filepath)
        }

def main():
    """Main function to generate manifest"""
    print('[+] Generating TEI corpus manifest...')

    files = []
    total_size = 0

    # Check if TEI directory exists
    if not os.path.exists(TEI_DIR):
        print(f'[ERROR] TEI directory not found: {TEI_DIR}')
        return

    # Process all TEI files
    tei_files = sorted([f for f in os.listdir(TEI_DIR) if f.endswith('.tei.xml')])

    for i, filename in enumerate(tei_files, 1):
        filepath = os.path.join(TEI_DIR, filename)
        metadata = extract_metadata(filepath)
        files.append(metadata)
        total_size += metadata['size']

        if i % 50 == 0:
            print(f'   Processed {i}/{len(tei_files)} files...')

    # Create manifest
    manifest = {
        'version': '1.0',
        'generatedAt': datetime.now().isoformat(),
        'totalFiles': len(files),
        'totalSize': total_size,
        'totalSizeMB': round(total_size / (1024 * 1024), 2),
        'files': files
    }

    # Write manifest
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f'\n[SUCCESS] Manifest generated successfully!')
    print(f'   Total files: {len(files)}')
    print(f'   Total size: {manifest["totalSizeMB"]} MB')
    print(f'   Output: {OUTPUT_FILE}')

if __name__ == '__main__':
    main()
