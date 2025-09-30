#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MHDBDB Variant Extraction Script
=================================
Extracts orthographic variants from TEI corpus and generates variants.xml

Usage:
    python scripts/extract-variants.py

Output:
    authority-files/variants.xml
"""

import sys
import io

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import xml.etree.ElementTree as ET
from collections import defaultdict
import glob
import os
from datetime import datetime

# TEI namespace
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}
XML_NS = {'xml': 'http://www.w3.org/XML/1998/namespace'}

# Register namespaces for proper output
ET.register_namespace('', 'http://www.tei-c.org/ns/1.0')
ET.register_namespace('xml', 'http://www.w3.org/XML/1998/namespace')


def extract_variants_from_tei_files(tei_dir='tei'):
    """
    Extract all variants from TEI files

    Returns:
        dict: {lemma_id: {type_id: {word_forms}}}
    """
    variants = defaultdict(lambda: defaultdict(set))
    processed_files = 0
    total_words = 0

    print(f"📚 Scanning TEI directory: {tei_dir}")
    tei_files = sorted(glob.glob(os.path.join(tei_dir, '*.xml')))
    print(f"📄 Found {len(tei_files)} TEI files")

    for i, tei_file in enumerate(tei_files, 1):
        if i % 100 == 0:
            print(f"   Processing file {i}/{len(tei_files)}...")

        try:
            tree = ET.parse(tei_file)
            root = tree.getroot()

            # Find all <w> elements with lemmaRef
            for w_elem in root.findall('.//tei:w[@lemmaRef]', TEI_NS):
                lemma_ref = w_elem.get('lemmaRef')
                word_ref = w_elem.get('wordRef')
                word_form = w_elem.text

                if lemma_ref and word_ref and word_form:
                    total_words += 1

                    # Extract IDs: "lexicon.xml#lemma_879" -> "lemma_879"
                    if '#' in lemma_ref:
                        lemma_id = lemma_ref.split('#')[1]
                    else:
                        continue

                    # Extract type ID: "lexicon.xml#lemma_879_sense_1449_type_48488" -> "type_48488"
                    if '_type_' in word_ref:
                        type_id = 'type_' + word_ref.split('_type_')[1]
                    else:
                        continue

                    # Store variant
                    variants[lemma_id][type_id].add(word_form.strip())

            processed_files += 1

        except ET.ParseError as e:
            print(f"   ⚠️  Parse error in {os.path.basename(tei_file)}: {e}")
            continue
        except Exception as e:
            print(f"   ⚠️  Error processing {os.path.basename(tei_file)}: {e}")
            continue

    print(f"✅ Processed {processed_files} files, extracted {total_words} word tokens")
    print(f"📊 Found {len(variants)} unique lemmas with variants")

    # Statistics
    total_types = sum(len(types) for types in variants.values())
    total_forms = sum(len(forms) for types in variants.values() for forms in types.values())
    print(f"📊 Total type IDs: {total_types}")
    print(f"📊 Total unique word forms: {total_forms}")

    return variants


def generate_variants_xml(variants, output_path='authority-files/variants.xml'):
    """
    Generate variants.xml file in TEI format

    Args:
        variants: dict from extract_variants_from_tei_files()
        output_path: where to write the file
    """
    print(f"\n🔨 Generating {output_path}...")

    # Create root element
    root = ET.Element('{http://www.tei-c.org/ns/1.0}TEI')

    # TEI Header
    tei_header = ET.SubElement(root, '{http://www.tei-c.org/ns/1.0}teiHeader')
    file_desc = ET.SubElement(tei_header, '{http://www.tei-c.org/ns/1.0}fileDesc')

    # Title statement
    title_stmt = ET.SubElement(file_desc, '{http://www.tei-c.org/ns/1.0}titleStmt')
    title = ET.SubElement(title_stmt, '{http://www.tei-c.org/ns/1.0}title')
    title.text = 'MHDBDB Orthographic Variants Index'

    resp_stmt = ET.SubElement(title_stmt, '{http://www.tei-c.org/ns/1.0}respStmt')
    resp = ET.SubElement(resp_stmt, '{http://www.tei-c.org/ns/1.0}resp')
    resp.text = 'Extracted from'
    name = ET.SubElement(resp_stmt, '{http://www.tei-c.org/ns/1.0}name')
    name.text = 'MHDBDB TEI Corpus (666 texts)'

    # Publication statement
    pub_stmt = ET.SubElement(file_desc, '{http://www.tei-c.org/ns/1.0}publicationStmt')
    publisher = ET.SubElement(pub_stmt, '{http://www.tei-c.org/ns/1.0}publisher')
    publisher.text = 'MHDBDB'
    date = ET.SubElement(pub_stmt, '{http://www.tei-c.org/ns/1.0}date')
    date.text = datetime.now().strftime('%Y-%m-%d')

    # Source description
    source_desc = ET.SubElement(file_desc, '{http://www.tei-c.org/ns/1.0}sourceDesc')
    p = ET.SubElement(source_desc, '{http://www.tei-c.org/ns/1.0}p')
    p.text = 'Automatically extracted attestations from TEI corpus'

    # Text body
    text = ET.SubElement(root, '{http://www.tei-c.org/ns/1.0}text')
    body = ET.SubElement(text, '{http://www.tei-c.org/ns/1.0}body')
    div = ET.SubElement(body, '{http://www.tei-c.org/ns/1.0}div')
    div.set('type', 'orthographicVariants')

    # Add variant entries
    # Sort lemmas numerically (lemma_879 -> 879)
    sorted_lemmas = sorted(variants.keys(), key=lambda x: int(x.replace('lemma_', '')))

    for lemma_id in sorted_lemmas:
        entry = ET.SubElement(div, '{http://www.tei-c.org/ns/1.0}entry')
        entry.set('corresp', f'lexicon.xml#{lemma_id}')

        # Sort type IDs
        types = variants[lemma_id]
        for type_id in sorted(types.keys(), key=lambda x: int(x.replace('type_', ''))):
            # Get unique word forms, sorted
            word_forms = sorted(types[type_id])

            for word_form in word_forms:
                form = ET.SubElement(entry, '{http://www.tei-c.org/ns/1.0}form')
                form.set('{http://www.w3.org/XML/1998/namespace}id', type_id)
                form.text = word_form

    # Write to file with pretty formatting
    tree = ET.ElementTree(root)
    ET.indent(tree, space='  ')

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    tree.write(output_path, encoding='utf-8', xml_declaration=True)

    # Check file size
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"✅ Generated {output_path}")
    print(f"📦 File size: {file_size_mb:.2f} MB")


def print_sample_stats(variants, n=5):
    """Print sample statistics"""
    print(f"\n📊 Sample Statistics (top {n} lemmas by variant count):")

    # Sort by number of unique word forms
    lemma_stats = []
    for lemma_id, types in variants.items():
        unique_forms = set()
        for type_id, forms in types.items():
            unique_forms.update(forms)
        lemma_stats.append((lemma_id, len(types), len(unique_forms)))

    lemma_stats.sort(key=lambda x: x[2], reverse=True)

    for lemma_id, type_count, form_count in lemma_stats[:n]:
        print(f"   {lemma_id}: {form_count} unique forms ({type_count} type IDs)")

        # Show sample forms
        sample_forms = []
        for type_id, forms in variants[lemma_id].items():
            sample_forms.extend(list(forms)[:2])
            if len(sample_forms) >= 5:
                break
        print(f"      Samples: {', '.join(sample_forms[:5])}")


def main():
    """Main execution"""
    print("=" * 60)
    print("MHDBDB Orthographic Variants Extraction")
    print("=" * 60)

    # Extract variants from TEI files
    variants = extract_variants_from_tei_files()

    if not variants:
        print("❌ No variants found. Check TEI file paths.")
        return 1

    # Print statistics
    print_sample_stats(variants)

    # Generate XML
    generate_variants_xml(variants)

    print("\n" + "=" * 60)
    print("✨ Extraction complete!")
    print("=" * 60)

    return 0


if __name__ == '__main__':
    exit(main())