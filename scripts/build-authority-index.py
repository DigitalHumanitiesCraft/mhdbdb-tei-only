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

import argparse
import json
import gzip
import subprocess
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
    TEI = '{http://www.tei-c.org/ns/1.0}'

    lemmata = []
    entries = tree.findall(f'.//{TEI}entry')

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

        # Extract etymology (morphological components)
        etym_components = []
        etym_el = entry.xpath('.//tei:etym[@type="morphological"]', namespaces=ns)
        if etym_el:
            comp_els = etym_el[0].xpath('.//tei:seg[@type="component"]', namespaces=ns)
            for comp in comp_els:
                corresp = comp.get('corresp')
                text = comp.text.strip() if comp.text else ''
                if text:
                    component_data = {'text': text}
                    if corresp and '#' in corresp:
                        component_data['lemmaRef'] = corresp.split('#')[1]
                    etym_components.append(component_data)

        # Extract all senses with details
        sense_els = entry.xpath('.//tei:sense', namespaces=ns)
        senses = []
        for sense_el in sense_els:
            sense_id = sense_el.get('{http://www.w3.org/XML/1998/namespace}id')
            if not sense_id:
                continue

            # Extract concept pointers
            concept_ptrs = sense_el.xpath('.//tei:ptr[contains(@target, "concepts.xml#")]', namespaces=ns)
            concept_ids = []
            for ptr in concept_ptrs:
                target = ptr.get('target')
                if target and '#' in target:
                    concept_ids.append(target.split('#')[1])

            senses.append({
                'id': sense_id,
                'conceptIds': concept_ids
            })

        # Normalize lemma for search
        normalized = normalize_mhg(lemma_text)

        lemmata.append({
            'id': lemma_id,
            'lemma': lemma_text,
            'normalized': normalized,
            'pos': pos,
            'senseCount': len(senses),
            'etymology': etym_components if etym_components else None,
            'senses': senses if senses else None
        })

    print(f"   Found {len(lemmata)} lemmata")
    return lemmata


# Module-level person→works lookup, populated by _build_person_works_map()
_person_works = {}


def _build_person_works_map(works):
    """Build person_id → comma-separated work_ids from parsed works data."""
    global _person_works
    for work in works:
        author_ref = work.get('authorRef')
        if not author_ref:
            continue
        # "persons.xml#person_5" → "person_5"
        person_id = author_ref.split('#')[-1] if '#' in author_ref else author_ref
        if person_id not in _person_works:
            _person_works[person_id] = []
        _person_works[person_id].append(work['id'])
    # Convert lists to comma-separated strings
    for pid in _person_works:
        _person_works[pid] = ','.join(_person_works[pid])
    print(f"   Built person→works map: {len(_person_works)} persons with works")


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
    TEI = '{http://www.tei-c.org/ns/1.0}'
    person_els = tree.findall(f'.//{TEI}person')

    for person_el in person_els:
        person_id = person_el.get('{http://www.w3.org/XML/1998/namespace}id')
        if not person_id:
            continue

        # Get preferred name
        name_el = person_el.xpath('.//tei:persName[@type="preferred"]', namespaces=ns)
        if not name_el:
            continue

        preferred_name = name_el[0].text.strip() if name_el[0].text else ''
        if not preferred_name:
            continue

        # Extract GND identifier
        gnd_el = person_el.xpath('.//tei:idno[@type="GND"]', namespaces=ns)
        gnd = gnd_el[0].text.strip() if gnd_el and gnd_el[0].text else None

        # Extract Wikidata identifier
        wikidata_el = person_el.xpath('.//tei:idno[@type="wikidata"]', namespaces=ns)
        wikidata = wikidata_el[0].text.strip() if wikidata_el and wikidata_el[0].text else None

        # Person→Work mapping is derived from works.xml <author @ref>
        # (populated after parse_works via _build_person_works_map)
        works = _person_works.get(person_id)

        persons.append({
            'id': person_id,
            'preferredName': preferred_name,
            'gnd': gnd,
            'wikidata': wikidata,
            'works': works,
            'normalized': normalize_mhg(preferred_name)
        })

    print(f"   Found {len(persons)} persons")
    return persons


# Module-level genre name lookup, populated by _build_genre_names()
_genre_names = {}


def _build_genre_names():
    """Build genre_id → German term lookup from genres.xml."""
    global _genre_names
    genres_file = AUTHORITY_DIR / 'genres.xml'
    if not genres_file.exists():
        return
    tree = etree.parse(str(genres_file))
    TEI = '{http://www.tei-c.org/ns/1.0}'
    XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
    for cat in tree.iter(f'{TEI}category'):
        cid = cat.get(XML_ID, '')
        if not cid.startswith('genre_'):
            continue
        for term in cat.findall(f'{TEI}catDesc/{TEI}term'):
            lang = term.get('{http://www.w3.org/XML/1998/namespace}lang', '')
            if lang == 'de' and term.text:
                _genre_names[cid] = term.text.strip()
                break
    print(f"   Built genre name lookup: {len(_genre_names)} entries")


def parse_works():
    """Parse works.xml to extract works with full details."""
    print("📚 Parsing works.xml...")
    _build_genre_names()
    works_file = AUTHORITY_DIR / 'works.xml'

    if not works_file.exists():
        print(f"⚠️  Warning: {works_file} not found, skipping")
        return []

    tree = etree.parse(str(works_file))
    ns = get_namespaces(tree)

    works = []
    # Try different possible root elements
    TEI = '{http://www.tei-c.org/ns/1.0}'
    work_els = tree.findall(f'.//{TEI}bibl')
    if not work_els:
        work_els = tree.findall('.//work')  # fallback for non-TEI

    for work_el in work_els:
        work_id = work_el.get('{http://www.w3.org/XML/1998/namespace}id')
        if not work_id:
            work_id = work_el.get('id')
        if not work_id:
            continue

        # Extract ALL titles (multiple support with metadata)
        title_els = work_el.xpath('./tei:title', namespaces=ns)
        if not title_els:
            title_els = work_el.xpath('./title', namespaces=ns)

        titles = []
        main_title = None
        for title_el in title_els:
            title_text = title_el.text.strip() if title_el.text else ''
            if title_text:
                title_data = {
                    'text': title_text,
                    'lang': title_el.get('{http://www.w3.org/XML/1998/namespace}lang'),
                    'type': title_el.get('type'),
                    'ana': title_el.get('ana')
                }
                titles.append(title_data)
                if not main_title:
                    main_title = title_text

        if not main_title:
            continue

        # Extract ALL sigle values (can be multiple)
        sigle_els = work_el.xpath('.//tei:idno[@type="sigle"]', namespaces=ns)
        sigles = [s.text.strip() for s in sigle_els if s.text]
        sigle = ', '.join(sigles) if sigles else None

        # Get author - prefer text content over ref
        author_el = work_el.xpath('.//tei:author', namespaces=ns)
        if not author_el:
            author_el = work_el.xpath('.//author', namespaces=ns)

        author_ref = author_el[0].get('ref') if author_el else None
        author_text = author_el[0].text.strip() if author_el and author_el[0].text else None
        author = author_text or author_ref or "Unbekannt"

        # Extract genre references (<ptr target="genres.xml#genre_ID"/>)
        # Genre label text is resolved from genres.xml via _genre_names lookup
        genre_ptrs = work_el.xpath('./tei:ptr[contains(@target, "genres.xml#")]', namespaces=ns)
        genres = []
        for ptr in genre_ptrs:
            target = ptr.get('target')
            if target:
                genre_id = target.split('#')[1] if '#' in target else target
                genre_text = _genre_names.get(genre_id, '')
                genres.append({
                    'id': genre_id,
                    'text': genre_text
                })

        # Extract biblStruct elements (bibliographic sources)
        bibl_struct_els = work_el.xpath('.//tei:biblStruct', namespaces=ns)
        bibl_structs = []
        for bibl_struct in bibl_struct_els:
            key = bibl_struct.get('key')
            corresp = bibl_struct.get('corresp')
            # Get full text content (normalized whitespace)
            text_content = ' '.join(bibl_struct.itertext()).strip()
            text_content = ' '.join(text_content.split())  # Normalize whitespace

            if key:
                bibl_structs.append({
                    'key': key,
                    'corresp': corresp,
                    'textContent': text_content
                })

        # Extract Handschriftencensus link
        hc_el = work_el.xpath('.//tei:idno[@type="handschriftencensus"]', namespaces=ns)
        handschriftencensus = hc_el[0].text.strip() if hc_el and hc_el[0].text else None

        # Extract GND identifier (for works)
        gnd_el = work_el.xpath('.//tei:idno[@type="GND"]', namespaces=ns)
        gnd = None
        if gnd_el and gnd_el[0].text:
            gnd_text = gnd_el[0].text.strip()
            # Extract just the ID if it's a full URL
            if 'gnd/' in gnd_text:
                gnd = gnd_text.split('gnd/')[-1]
            else:
                gnd = gnd_text

        # Extract Wikidata identifier (for works)
        wikidata_el = work_el.xpath('.//tei:idno[@type="wikidata"]', namespaces=ns)
        wikidata = None
        if wikidata_el and wikidata_el[0].text:
            wikidata_text = wikidata_el[0].text.strip()
            # Extract just the Q-ID if it's a full URL
            if '/entity/' in wikidata_text:
                wikidata = wikidata_text.split('/entity/')[-1]
            else:
                wikidata = wikidata_text

        works.append({
            'id': work_id,
            'title': main_title,
            'titles': titles,
            'sigle': sigle,
            'sigles': sigles,
            'author': author,
            'authorRef': author_ref,
            'genres': genres,
            'biblStructs': bibl_structs,
            'handschriftencensus': handschriftencensus,
            'gnd': gnd,
            'wikidata': wikidata,
            'normalized': normalize_mhg(main_title)
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
    TEI = '{http://www.tei-c.org/ns/1.0}'

    concepts = []
    # Find all category elements with concept_ prefix
    category_els = tree.findall(f'.//{TEI}category')

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

        # Find German and English terms — primary vs. alternative kept separate
        # so the autocomplete can match synonyms without overwriting the primary
        # label (Issue #113-Followup, KZW 2026-05-18).
        term_els = catdesc_el.findall('.//tei:term', namespaces=ns)
        term_de = ''
        term_en = ''
        alt_de = []
        alt_en = []

        for term_el in term_els:
            lang = term_el.get('{http://www.w3.org/XML/1998/namespace}lang')
            ttype = term_el.get('type')
            text = term_el.text.strip() if term_el.text else ''
            if not text:
                continue
            if lang == 'de':
                if ttype == 'alternative':
                    alt_de.append(text)
                elif not term_de:
                    term_de = text
            elif lang == 'en':
                if ttype == 'alternative':
                    alt_en.append(text)
                elif not term_en:
                    term_en = text

        if not term_de:
            continue

        concept_entry = {
            'id': category_id,
            'termDE': term_de,
            'termEN': term_en,
            'normalized': normalize_mhg(term_de)
        }
        if alt_de:
            concept_entry['altDE'] = alt_de
            concept_entry['altNormalized'] = [normalize_mhg(t) for t in alt_de]
        if alt_en:
            concept_entry['altEN'] = alt_en
        concepts.append(concept_entry)

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
    TEI = '{http://www.tei-c.org/ns/1.0}'

    genres = []
    # Find all category elements with genre_ prefix
    category_els = tree.findall(f'.//{TEI}category')

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
    TEI = '{http://www.tei-c.org/ns/1.0}'

    names = []
    # Find all category elements with name_ prefix
    category_els = tree.findall(f'.//{TEI}category')

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

        # Extract concept pointers (for semantic connections)
        concept_ptrs = category_el.xpath('.//tei:ptr[contains(@target, "concepts.xml#")]', namespaces=ns)
        concept_ids = []
        for ptr in concept_ptrs:
            target = ptr.get('target')
            if target and '#' in target:
                concept_ids.append(target.split('#')[1])

        names.append({
            'id': category_id,
            'termDE': term_de,
            'termEN': term_en,
            'conceptIds': concept_ids if concept_ids else None,
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
    TEI = '{http://www.tei-c.org/ns/1.0}'

    variants = {}  # normalized_variant -> lemma_id
    entry_els = tree.findall(f'.//{TEI}entry')

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
    # NEW: Now we have this data from lemma senses!
    for lemma in lemmata:
        if not lemma.get('senses'):
            continue

        lemma_id = lemma['id']
        for sense in lemma['senses']:
            if not sense.get('conceptIds'):
                continue

            for concept_id in sense['conceptIds']:
                if concept_id not in maps['conceptToLemmas']:
                    maps['conceptToLemmas'][concept_id] = []
                # Deduplicate: only add each lemma once per concept
                # (fixes bug in old version that counted same lemma multiple times)
                if lemma_id not in maps['conceptToLemmas'][concept_id]:
                    maps['conceptToLemmas'][concept_id].append(lemma_id)

    print(f"   Built conceptToLemmas: {len(maps['conceptToLemmas'])} concepts mapped to lemmas")

    # 2. Build genreToWorks map
    # Map genre IDs to lists of work IDs
    # NEW: Now we have this data from work genres!
    for work in works:
        if not work.get('genres'):
            continue

        work_id = work['id']
        for genre_ref in work['genres']:
            genre_id = genre_ref['id']
            if genre_id not in maps['genreToWorks']:
                maps['genreToWorks'][genre_id] = []
            if work_id not in maps['genreToWorks'][genre_id]:
                maps['genreToWorks'][genre_id].append(work_id)

    print(f"   Built genreToWorks: {len(maps['genreToWorks'])} genres mapped to works")

    # 3. Build genreHierarchy map
    # Map genre IDs to their parent genre names
    # Parse genres.xml to extract parent relationships via <ptr type="broader">
    try:
        genres_file = AUTHORITY_DIR / 'genres.xml'
        if genres_file.exists():
            tree = etree.parse(str(genres_file))
            ns = get_namespaces(tree)
            TEI = '{http://www.tei-c.org/ns/1.0}'

            # Build lookup: genre_id -> genre name (German)
            genre_names = {}
            categories = tree.findall(f'.//{TEI}category')
            for category in categories:
                cat_id = category.get('{http://www.w3.org/XML/1998/namespace}id')
                if not cat_id:
                    continue

                # Get German term
                catdesc = category.find('.//tei:catDesc', namespaces=ns)
                if catdesc is not None:
                    # Find all terms and filter for German
                    terms = catdesc.findall('.//tei:term', namespaces=ns)
                    for term in terms:
                        lang = term.get('{http://www.w3.org/XML/1998/namespace}lang')
                        if lang == 'de' and term.text:
                            genre_names[cat_id] = term.text.strip()
                            break

            # Find all categories with broader relationships
            for category in categories:
                category_id = category.get('{http://www.w3.org/XML/1998/namespace}id')
                if not category_id:
                    continue

                # Find <ptr type="broader"> elements
                catdesc = category.find('tei:catDesc', namespaces=ns)
                if catdesc is not None:
                    broader_ptrs = catdesc.findall('tei:ptr[@type="broader"]', namespaces=ns)

                    if broader_ptrs:
                        parent_names = []
                        for ptr in broader_ptrs:
                            target = ptr.get('target')
                            if target and target.startswith('#'):
                                parent_id = target[1:]  # Remove '#' prefix
                                if parent_id in genre_names:
                                    parent_names.append(genre_names[parent_id])

                        if parent_names:
                            maps['genreHierarchy'][category_id] = parent_names

            print(f"   Built genreHierarchy: {len(maps['genreHierarchy'])} entries")
    except Exception as e:
        print(f"   ⚠️  Could not build genreHierarchy: {e}")

    return maps


def build_index():
    """Build complete authority index."""
    print("\n🔨 Building authority index...")
    print(f"Authority files directory: {AUTHORITY_DIR}")

    # Reset module-level caches (safe for repeated calls in test harnesses)
    global _person_works, _genre_names
    _person_works = {}
    _genre_names = {}

    # Parse all authority files
    # works before persons: person→works map is derived from works.xml <author @ref>
    lemmata = parse_lexicon()
    works = parse_works()
    _build_person_works_map(works)
    persons = parse_persons()
    concepts = parse_concepts()
    genres = parse_genres()
    names = parse_names()
    variants = parse_variants()

    # Build performance Maps for fast lookups
    performance_maps = build_performance_maps(lemmata, works, concepts, genres)

    # Build index structure
    index = {
        'version': '1.4.0',  # 1.2.0: Authority migration (genre ptrs, person-works derivation, Frauendienst split). 1.2.1: WZB-Lemmata + Varianten + Werk-Eintrag. 1.2.2: #104 FLG/FLG1-Werk-Titel + work_571 biblStruct auf Vollmann-Profe/Neumann 1990. 1.3.0: #113-Followup — alternative-Terms in concepts.xml getrennt von Primär-Term (altDE/altEN/altNormalized) statt last-wins-Overwrite. 1.4.0: #44/#115 variants.xml aus Korpus regeneriert via scripts/sync/extract-variants.py (+64.287 Formen, 192.472→256.759).
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


def check_working_tree(directory, allow_dirty):
    """Pre-flight check: warn (or fail) when directory has uncommitted or
    untracked authority files. Prevents accidentally bundling work-in-progress
    files into the published index. See #100."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain', '--', str(directory)],
            capture_output=True, text=True, check=True, cwd=PROJECT_ROOT
        )
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"⚠️  git status check skipped: {e}")
        return

    lines = [ln for ln in result.stdout.splitlines() if ln.strip()]
    untracked = [ln for ln in lines if ln.startswith('??')]
    modified = [ln for ln in lines if not ln.startswith('??')]

    if not lines:
        return

    print(f"⚠️  Working tree under {directory}/ is not clean:")
    print(f"   {len(untracked)} untracked, {len(modified)} modified/staged")
    for ln in lines[:10]:
        print(f"     {ln}")
    if len(lines) > 10:
        print(f"     ... +{len(lines) - 10} more")

    if allow_dirty:
        print("   --allow-dirty set, continuing anyway.")
    else:
        sys.exit(
            "Refusing to build a possibly-inconsistent index.\n"
            "Commit/stash the changes above, or pass --allow-dirty for local tests."
        )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Build MHDBDB authority index from authority-files/")
    parser.add_argument(
        '--allow-dirty', action='store_true',
        help="Build even if authority-files/ has untracked or modified files (use for local tests)."
    )
    args = parser.parse_args()

    print("=" * 60)
    print("MHDBDB Authority Index Builder")
    print("=" * 60)

    check_working_tree(AUTHORITY_DIR.relative_to(PROJECT_ROOT), args.allow_dirty)

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
