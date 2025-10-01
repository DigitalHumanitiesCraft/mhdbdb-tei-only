#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Authority Index

Generates pre-built authority index from authority-files/ directory.
Output: data/authority-index.json.gz (~1-2 MB compressed)

Includes:
- Lemmata from lexicon.xml
- Persons from persons.xml
- Works from works.xml
- Concepts from concepts.xml
- Genres from genres.xml
- Names from names.xml
- Variants from variants.xml

CRITICAL: Uses mhg_normalizer.py for text normalization.
"""

import json
import gzip
import sys
import os
from pathlib import Path
from datetime import datetime

# Check dependencies
try:
    from lxml import etree
except ImportError:
    print("❌ ERROR: lxml not installed")
    print("   Install with: pip install lxml")
    sys.exit(1)

# Import our normalizer
sys.path.insert(0, str(Path(__file__).parent))
from mhg_normalizer import normalize_mhg

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
AUTHORITY_DIR = PROJECT_ROOT / 'authority-files'
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_FILE = DATA_DIR / 'authority-index.json.gz'

# TEI namespace
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


def get_namespaces(tree):
    """
    Detect and return all namespaces in document (Critical Fix #2).

    Handles default namespaces and unprefixed elements.
    """
    nsmap = tree.getroot().nsmap.copy()

    # Move default namespace to 'tei' prefix
    if None in nsmap:
        nsmap['tei'] = nsmap[None]
        del nsmap[None]

    # Ensure TEI namespace exists
    if 'tei' not in nsmap:
        nsmap['tei'] = 'http://www.tei-c.org/ns/1.0'

    return nsmap


def parse_lexicon():
    """Parse lexicon.xml to extract lemmata."""
    print("📖 Parsing lexicon.xml...")
    lexicon_file = AUTHORITY_DIR / 'lexicon.xml'

    if not lexicon_file.exists():
        print(f"⚠️  Warning: {lexicon_file} not found, skipping")
        return []

    tree = etree.parse(str(lexicon_file))
    ns = get_namespaces(tree)

    lemmata = []
    entries = tree.xpath('//tei:entry', namespaces=ns)

    for entry in entries:
        lemma_id = entry.get('{http://www.w3.org/XML/1998/namespace}id')
        if not lemma_id:
            continue

        # Get lemma text from <form type="lemma"><orth>text</orth></form>
        orth_el = entry.xpath('.//tei:form[@type="lemma"]/tei:orth', namespaces=ns)
        if not orth_el:
            continue

        lemma_text = orth_el[0].text.strip() if orth_el[0].text else ''
        if not lemma_text:
            continue

        # Get part of speech
        pos_el = entry.xpath('.//tei:pos', namespaces=ns)
        pos = pos_el[0].text.strip() if pos_el and pos_el[0].text else ''

        # Note: No definition field in this structure, concepts linked via pointers

        # Normalize lemma for search
        normalized = normalize_mhg(lemma_text)

        lemmata.append({
            'id': lemma_id,
            'lemma': lemma_text,
            'normalized': normalized,
            'pos': pos
        })

    print(f"   Found {len(lemmata)} lemmata")
    return lemmata


def parse_persons():
    """Parse persons.xml to extract persons."""
    print("👤 Parsing persons.xml...")
    persons_file = AUTHORITY_DIR / 'persons.xml'

    if not persons_file.exists():
        print(f"⚠️  Warning: {persons_file} not found, skipping")
        return []

    tree = etree.parse(str(persons_file))
    ns = get_namespaces(tree)

    persons = []
    person_els = tree.xpath('//tei:person', namespaces=ns)

    for person_el in person_els:
        person_id = person_el.get('{http://www.w3.org/XML/1998/namespace}id')
        if not person_id:
            continue

        # Get preferred name
        name_el = person_el.xpath('.//tei:persName[@type="preferred"]', namespaces=ns)
        if not name_el:
            continue

        name = name_el[0].text.strip() if name_el[0].text else ''
        if not name:
            continue

        persons.append({
            'id': person_id,
            'name': name,
            'normalized': normalize_mhg(name)
        })

    print(f"   Found {len(persons)} persons")
    return persons


def parse_works():
    """Parse works.xml to extract works."""
    print("📚 Parsing works.xml...")
    works_file = AUTHORITY_DIR / 'works.xml'

    if not works_file.exists():
        print(f"⚠️  Warning: {works_file} not found, skipping")
        return []

    tree = etree.parse(str(works_file))
    ns = get_namespaces(tree)

    works = []
    # Try different possible root elements
    work_els = tree.xpath('//tei:bibl', namespaces=ns)
    if not work_els:
        work_els = tree.xpath('//work', namespaces=ns)

    for work_el in work_els:
        work_id = work_el.get('{http://www.w3.org/XML/1998/namespace}id')
        if not work_id:
            work_id = work_el.get('id')
        if not work_id:
            continue

        # Get title
        title_el = work_el.xpath('.//tei:title', namespaces=ns)
        if not title_el:
            title_el = work_el.xpath('.//title', namespaces=ns)

        title = title_el[0].text.strip() if title_el and title_el[0].text else ''
        if not title:
            continue

        # Get author ref
        author_el = work_el.xpath('.//tei:author', namespaces=ns)
        if not author_el:
            author_el = work_el.xpath('.//author', namespaces=ns)

        author_ref = author_el[0].get('ref') if author_el else ''

        works.append({
            'id': work_id,
            'title': title,
            'authorRef': author_ref,
            'normalized': normalize_mhg(title)
        })

    print(f"   Found {len(works)} works")
    return works


def parse_concepts():
    """Parse concepts.xml to extract concepts from taxonomy categories."""
    print("💡 Parsing concepts.xml...")
    concepts_file = AUTHORITY_DIR / 'concepts.xml'

    if not concepts_file.exists():
        print(f"⚠️  Warning: {concepts_file} not found, skipping")
        return []

    tree = etree.parse(str(concepts_file))
    ns = get_namespaces(tree)

    concepts = []
    # Find all category elements with concept_ prefix
    category_els = tree.xpath('//tei:category', namespaces=ns)

    for category_el in category_els:
        category_id = category_el.get('{http://www.w3.org/XML/1998/namespace}id')
        if not category_id:
            category_id = category_el.get('id')

        # Filter by concept_ prefix
        if not category_id or 'concept_' not in category_id:
            continue

        # Extract terms from catDesc
        catdesc_el = category_el.find('.//tei:catDesc', namespaces=ns)
        if catdesc_el is None:
            continue

        # Find German and English terms
        term_els = catdesc_el.findall('.//tei:term', namespaces=ns)
        term_de = ''
        term_en = ''

        for term_el in term_els:
            lang = term_el.get('{http://www.w3.org/XML/1998/namespace}lang')
            if lang == 'de':
                term_de = term_el.text.strip() if term_el.text else ''
            elif lang == 'en':
                term_en = term_el.text.strip() if term_el.text else ''

        if not term_de:
            continue

        concepts.append({
            'id': category_id,
            'termDE': term_de,
            'termEN': term_en,
            'normalized': normalize_mhg(term_de)
        })

    print(f"   Found {len(concepts)} concepts")
    return concepts


def parse_genres():
    """Parse genres.xml to extract genres from taxonomy categories."""
    print("🎭 Parsing genres.xml...")
    genres_file = AUTHORITY_DIR / 'genres.xml'

    if not genres_file.exists():
        print(f"⚠️  Warning: {genres_file} not found, skipping")
        return []

    tree = etree.parse(str(genres_file))
    ns = get_namespaces(tree)

    genres = []
    # Find all category elements with genre_ prefix
    category_els = tree.xpath('//tei:category', namespaces=ns)

    for category_el in category_els:
        category_id = category_el.get('{http://www.w3.org/XML/1998/namespace}id')
        if not category_id:
            category_id = category_el.get('id')

        # Filter by genre_ prefix
        if not category_id or 'genre_' not in category_id:
            continue

        # Extract terms from catDesc
        catdesc_el = category_el.find('.//tei:catDesc', namespaces=ns)
        if catdesc_el is None:
            continue

        # Find German and English terms
        term_els = catdesc_el.findall('.//tei:term', namespaces=ns)
        term_de = ''
        term_en = ''

        for term_el in term_els:
            lang = term_el.get('{http://www.w3.org/XML/1998/namespace}lang')
            if lang == 'de':
                term_de = term_el.text.strip() if term_el.text else ''
            elif lang == 'en':
                term_en = term_el.text.strip() if term_el.text else ''

        if not term_de:
            continue

        genres.append({
            'id': category_id,
            'termDE': term_de,
            'termEN': term_en,
            'normalized': normalize_mhg(term_de)
        })

    print(f"   Found {len(genres)} genres")
    return genres


def parse_names():
    """Parse names.xml to extract proper names from taxonomy categories."""
    print("📛 Parsing names.xml...")
    names_file = AUTHORITY_DIR / 'names.xml'

    if not names_file.exists():
        print(f"⚠️  Warning: {names_file} not found, skipping")
        return []

    tree = etree.parse(str(names_file))
    ns = get_namespaces(tree)

    names = []
    # Find all category elements with name_ prefix
    category_els = tree.xpath('//tei:category', namespaces=ns)

    for category_el in category_els:
        category_id = category_el.get('{http://www.w3.org/XML/1998/namespace}id')
        if not category_id:
            category_id = category_el.get('id')

        # Filter by name_ prefix
        if not category_id or 'name_' not in category_id:
            continue

        # Extract terms from catDesc
        catdesc_el = category_el.find('.//tei:catDesc', namespaces=ns)
        if catdesc_el is None:
            continue

        # Find German and English terms
        term_els = catdesc_el.findall('.//tei:term', namespaces=ns)
        term_de = ''
        term_en = ''

        for term_el in term_els:
            lang = term_el.get('{http://www.w3.org/XML/1998/namespace}lang')
            if lang == 'de':
                term_de = term_el.text.strip() if term_el.text else ''
            elif lang == 'en':
                term_en = term_el.text.strip() if term_el.text else ''

        if not term_de:
            continue

        names.append({
            'id': category_id,
            'termDE': term_de,
            'termEN': term_en,
            'normalized': normalize_mhg(term_de)
        })

    print(f"   Found {len(names)} names")
    return names


def parse_variants():
    """Parse variants.xml to extract orthographic variants."""
    print("🔤 Parsing variants.xml...")
    variants_file = AUTHORITY_DIR / 'variants.xml'

    if not variants_file.exists():
        print(f"⚠️  Warning: {variants_file} not found, skipping")
        return {}

    tree = etree.parse(str(variants_file))
    ns = get_namespaces(tree)

    variants = {}  # normalized_variant -> lemma_id
    entry_els = tree.xpath('//tei:entry | //entry', namespaces=ns)

    for entry in entry_els:
        # Get lemma reference from corresp attribute
        lemma_ref = entry.get('corresp')
        if not lemma_ref:
            lemma_ref = entry.get('lemmaRef')  # Fallback
        if not lemma_ref:
            continue

        # Extract lemma ID from reference (e.g., "lexicon.xml#lemma_879" -> "lemma_879")
        if '#' in lemma_ref:
            lemma_id = lemma_ref.split('#')[1]
        else:
            lemma_id = lemma_ref.lstrip('#')

        # Get all orthographic forms (using <form> elements, not <orth>)
        form_els = entry.xpath('.//tei:form', namespaces=ns)

        for form_el in form_els:
            variant = form_el.text
            if not variant:
                continue

            variant = variant.strip()
            normalized_variant = normalize_mhg(variant)

            # Map normalized variant to lemma ID
            if normalized_variant not in variants:
                variants[normalized_variant] = lemma_id

    print(f"   Found {len(variants)} variant mappings")
    return variants


def build_performance_maps(lemmata, works, concepts, genres):
    """
    Build performance Maps for fast lookups in the playground.
    These Maps are used by AuthorityExplorers.js for:
    - Concept → Lemmas mapping
    - Genre → Works mapping
    - Genre hierarchy lookup
    """
    print("\n🗺️  Building performance Maps...")

    maps = {
        'conceptToLemmas': {},
        'genreToWorks': {},
        'genreHierarchy': {}
    }

    # 1. Build conceptToLemmas map
    # Map concept IDs to lists of lemma IDs
    # NOTE: This requires linking data between concepts and lemmata
    # For now, skip as we don't have this relationship in the XML

    # 2. Build genreToWorks map
    # Map genre IDs to lists of work IDs
    # NOTE: Works don't have genre references in the current data structure
    # For now, skip as we don't have this relationship

    # 3. Build genreHierarchy map
    # Map genre IDs to their parent genre names
    # Parse genres.xml to extract parent relationships
    try:
        genres_file = AUTHORITY_DIR / 'genres.xml'
        if genres_file.exists():
            tree = etree.parse(str(genres_file))
            ns = get_namespaces(tree)

            # Find all categories with parents
            categories = tree.xpath('//tei:category', namespaces=ns)

            for category in categories:
                category_id = category.get('{http://www.w3.org/XML/1998/namespace}id')
                if not category_id or 'genre_' not in category_id:
                    continue

                # Find parent category
                parent_category = category.getparent()
                if parent_category is not None and parent_category.tag.endswith('category'):
                    parent_id = parent_category.get('{http://www.w3.org/XML/1998/namespace}id')

                    # Get parent name
                    catdesc = parent_category.find('.//tei:catDesc', namespaces=ns)
                    if catdesc is not None:
                        term_el = catdesc.find('.//tei:term[@xml:lang="de"]', namespaces=ns)
                        if term_el is not None and term_el.text:
                            parent_name = term_el.text.strip()
                            # Store as list of parent names (could be multiple levels)
                            maps['genreHierarchy'][category_id] = [parent_name]

            print(f"   Built genreHierarchy: {len(maps['genreHierarchy'])} entries")
    except Exception as e:
        print(f"   ⚠️  Could not build genreHierarchy: {e}")

    return maps


def build_index():
    """Build complete authority index."""
    print("\n🔨 Building authority index...")
    print(f"Authority files directory: {AUTHORITY_DIR}")

    # Parse all authority files
    lemmata = parse_lexicon()
    persons = parse_persons()
    works = parse_works()
    concepts = parse_concepts()
    genres = parse_genres()
    names = parse_names()
    variants = parse_variants()

    # Build performance Maps for fast lookups
    performance_maps = build_performance_maps(lemmata, works, concepts, genres)

    # Build index structure
    index = {
        'version': '1.0.0',  # Must match INDEX_VERSION in db-schema.js
        'generatedAt': datetime.utcnow().isoformat() + 'Z',
        'lemmata': lemmata,
        'persons': persons,
        'works': works,
        'concepts': concepts,
        'genres': genres,
        'names': names,
        'variants': variants,
        'maps': performance_maps  # NEW: Pre-built performance Maps
    }

    # Statistics
    total_items = len(lemmata) + len(persons) + len(works) + len(concepts) + len(genres) + len(names)
    print(f"\n📊 Statistics:")
    print(f"   Total items: {total_items:,}")
    print(f"   Lemmata: {len(lemmata):,}")
    print(f"   Persons: {len(persons):,}")
    print(f"   Works: {len(works):,}")
    print(f"   Concepts: {len(concepts):,}")
    print(f"   Genres: {len(genres):,}")
    print(f"   Names: {len(names):,}")
    print(f"   Variants: {len(variants):,}")

    return index


def save_index(index):
    """Save index to compressed JSON file."""
    print(f"\n💾 Saving to {OUTPUT_FILE}...")

    # Create data directory if needed
    DATA_DIR.mkdir(exist_ok=True)

    # Serialize to JSON
    json_data = json.dumps(index, ensure_ascii=False, separators=(',', ':'))

    # Get uncompressed size
    uncompressed_size = len(json_data.encode('utf-8'))

    # Compress with gzip
    with gzip.open(OUTPUT_FILE, 'wt', encoding='utf-8') as f:
        f.write(json_data)

    # Get compressed size
    compressed_size = OUTPUT_FILE.stat().st_size

    compression_ratio = (1 - compressed_size / uncompressed_size) * 100

    print(f"   Uncompressed: {uncompressed_size / (1024 * 1024):.2f} MB")
    print(f"   Compressed: {compressed_size / (1024 * 1024):.2f} MB")
    print(f"   Compression: {compression_ratio:.1f}%")
    print(f"\n✅ Authority index saved successfully!")


def main():
    """Main entry point."""
    print("=" * 60)
    print("MHDBDB Authority Index Builder")
    print("=" * 60)

    try:
        # Build index
        index = build_index()

        # Save index
        save_index(index)

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
