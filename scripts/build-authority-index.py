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
from tei_namespaces import get_namespaces

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
AUTHORITY_DIR = PROJECT_ROOT / 'authority-files'
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_FILE = DATA_DIR / 'authority-index.json.gz'

# TEI namespace
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


def _all_text(el):
    """Vollständiger Textinhalt eines Elements, auch über Kindelemente hinweg.

    `el.text` liest nur den ersten Textknoten. Für die kuratierten Prosa-Felder
    (<def>, <note>) erlaubt das Schema heute keine Kinder, aber sobald es das
    tut (Bibelstellen als <ref> liegt nahe), würde `el.text` den Rest still
    verschlucken.
    """
    return ''.join(el.itertext()).strip()


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

        # Get part of speech — an entry can carry multiple <pos> siblings
        # (#161, e.g. lemma_79188 "salve" = NOM + VRB). posAll keeps every
        # value; pos stays the first one for backwards compatibility.
        pos_els = entry.xpath('.//tei:pos', namespaces=ns)
        pos_all = []
        for pos_el in pos_els:
            pos_text = pos_el.text.strip() if pos_el.text else ''
            if pos_text and pos_text not in pos_all:
                pos_all.append(pos_text)
        pos = pos_all[0] if pos_all else ''

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

        # Herkunftssprache aus <etym type="borrowing"> (Schicht B, #28).
        # Bewusst getrennt von 'etymology' (Komposition): das eine sagt, woher
        # das Wort kommt, das andere, aus welchen mhd. Lemmata es gebaut ist.
        origin = None
        borrow_el = entry.xpath('.//tei:etym[@type="borrowing"]', namespaces=ns)
        if borrow_el:
            languages = []
            for lang_el in borrow_el[0].xpath('./tei:lang', namespaces=ns):
                name = _all_text(lang_el)
                if not name:
                    continue
                lang_data = {'name': name}
                if lang_el.get('norm'):
                    lang_data['code'] = lang_el.get('norm')
                languages.append(lang_data)
            attribution_el = borrow_el[0].xpath('./tei:note[@type="attribution"]', namespaces=ns)
            if languages:
                origin = {'languages': languages}
                if attribution_el:
                    attribution = _all_text(attribution_el[0])
                    if attribution:
                        origin['attribution'] = attribution
                        if attribution_el[0].get('resp'):
                            origin['resp'] = attribution_el[0].get('resp')

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

            sense_data = {
                'id': sense_id,
                'conceptIds': concept_ids
            }

            # Kuratierte Prosa-Angaben (optional, seit 2026-07-30). Nur setzen,
            # wenn vorhanden: 43.879 Lemmata mit leeren Feldern würden Index
            # und API ohne Nutzen aufblähen.
            def_el = sense_el.xpath('./tei:def', namespaces=ns)
            if def_el:
                definition = _all_text(def_el[0])
                if definition:
                    sense_data['definition'] = definition
                    if def_el[0].get('resp'):
                        sense_data['definitionResp'] = def_el[0].get('resp')

            comment_el = sense_el.xpath('./tei:note[@type="comment"]', namespaces=ns)
            if comment_el:
                comment = _all_text(comment_el[0])
                if comment:
                    sense_data['comment'] = comment
                    if comment_el[0].get('resp'):
                        sense_data['commentResp'] = comment_el[0].get('resp')

            senses.append(sense_data)

        # Normalize lemma for search
        normalized = normalize_mhg(lemma_text)

        lemma_record = {
            'id': lemma_id,
            'lemma': lemma_text,
            'normalized': normalized,
            'pos': pos,
            'posAll': pos_all,
            'senseCount': len(senses),
            'etymology': etym_components if etym_components else None,
            'senses': senses if senses else None
        }
        if origin:
            lemma_record['origin'] = origin
        lemmata.append(lemma_record)

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

        # itertext() + Whitespace-Kollaps statt .text, wie in parse_works seit
        # #228: dort trug ein ueber zwei Zeilen eingerueckter Name den Umbruch
        # bis in die API. In persons.xml gibt es heute weder Kindelemente noch
        # Umbrueche in persName, der gebaute Index bleibt byte-identisch. Der
        # Griff steht hier, damit die naechste handgepflegte Zeile nicht wieder
        # ueber dieselbe Kante faellt.
        preferred_name = ' '.join(''.join(name_el[0].itertext()).split())
        if not preferred_name:
            continue

        # Alternative name forms (#307). Deduplicated by exact text, document order.
        # persons.xml carries the same string twice whenever the German and English
        # forms coincide (34 of 134 entries, differing only in @xml:lang). The language
        # is not indexed: for a person both forms name the same individual, so the
        # alternative is a search key, not a display term. That differs from concepts,
        # where termDE/termEN are distinct labels and both get shown.
        # The parser deliberately does not key on @xml:lang. person_127 (added in
        # #228) carried none until #307 normalized it to "de"; keying on the
        # attribute would have dropped that form silently.
        alt_names = []
        for alt_el in person_el.xpath('./tei:persName[@type="alternative"]', namespaces=ns):
            alt_text = ' '.join(''.join(alt_el.itertext()).split())
            if alt_text and alt_text != preferred_name and alt_text not in alt_names:
                alt_names.append(alt_text)

        # Extract GND identifier
        gnd_el = person_el.xpath('.//tei:idno[@type="GND"]', namespaces=ns)
        gnd = gnd_el[0].text.strip() if gnd_el and gnd_el[0].text else None

        # Extract Wikidata identifier
        wikidata_el = person_el.xpath('.//tei:idno[@type="wikidata"]', namespaces=ns)
        wikidata = wikidata_el[0].text.strip() if wikidata_el and wikidata_el[0].text else None

        # Person→Work mapping is derived from works.xml <author @ref>
        # (populated after parse_works via _build_person_works_map)
        works = _person_works.get(person_id)

        person_entry = {
            'id': person_id,
            'preferredName': preferred_name,
            'gnd': gnd,
            'wikidata': wikidata,
            'works': works,
            'normalized': normalize_mhg(preferred_name)
        }
        if alt_names:
            # Index-parallel by contract: altNormalized[i] is the normalized form of
            # altNames[i]. The person explorer matches on the normalized list and
            # displays the readable form at the same position, so the two lists must
            # never be deduplicated independently.
            person_entry['altNames'] = alt_names
            person_entry['altNormalized'] = [normalize_mhg(n) for n in alt_names]
        persons.append(person_entry)

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

        # Get author - prefer text content over ref.
        # Nur direktes Kind (#293): jedes <bibl> traegt seit dem Zotero-Sync ein
        # <biblStruct> mit den <author> der EDITION. Eine Descendant-Suche traege
        # bei einem Werk ohne eigenen <author> still den Editionsautor als
        # Werksautor ein. Heute betrifft das 0 von 584 Eintraegen, alle haben ein
        # direktes Kind; die Enge kostet also nichts. Analog zu ./tei:title oben.
        author_el = work_el.xpath('./tei:author', namespaces=ns)
        if not author_el:
            author_el = work_el.xpath('./author', namespaces=ns)

        author_ref = author_el[0].get('ref') if author_el else None
        # itertext() plus Whitespace-Kollaps (#228), dieselbe Lesart wie in
        # build-corpus-index.py. works.xml traegt bei work_563 den Autornamen
        # ueber zwei eingerueckte Zeilen; .text liess den Umbruch samt
        # Einrueckung bis in api/works/work_563.json durch. XML-Einrueckung ist
        # beliebig, die Normalisierung gehoert deshalb zum Leser.
        author_text = (' '.join(''.join(author_el[0].itertext()).split())
                       if author_el else '') or None
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


def _direct_parents(closure):
    """
    Transitive reduction of the genre polyhierarchy (#361).

    genres.xml stores the full transitive closure: every <ptr type="broader">
    set names all ancestors, not just the nearest ones. A parent p of x is
    direct exactly when no other parent q of x already has p among its own
    ancestors. Everything else is a shortcut edge that the tree view must not
    draw, or the hierarchy collapses into a flat list.

    Returns id -> sorted list of direct parent ids. Result is a DAG, not a
    tree: 171 of 615 categories keep more than one direct parent, and that is
    the point of the typology (Predigtmaerlein is both Maere and Predigt).
    """
    direct = {}
    for cid, parents in closure.items():
        direct[cid] = sorted(
            p for p in parents
            if not any(q != p and p in closure.get(q, ()) for q in parents)
        )
    return direct


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
    closure = {}  # #361: genre_id -> all ancestors, as stored in genres.xml
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

        # #361: collect the stored ancestor set before any filtering below, so
        # the reduction sees the same graph that genres.xml describes.
        closure[category_id] = {
            (ptr.get('target') or '')[1:]
            for ptr in catdesc_el.findall('tei:ptr[@type="broader"]', namespaces=ns)
            if (ptr.get('target') or '').startswith('#')
        }

        # Find German and English terms — primary vs. alternative kept separate
        # so the alternative never overwrites the primary label (same last-wins
        # bug as in concepts, fixed there under #113-Followup; genres analog
        # affected 250 categories where <term type="alternative"> follows the
        # primary term).
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

        genre_entry = {
            'id': category_id,
            'termDE': term_de,
            'termEN': term_en,
            'normalized': normalize_mhg(term_de)
        }
        if alt_de:
            genre_entry['altDE'] = alt_de
            genre_entry['altNormalized'] = [normalize_mhg(t) for t in alt_de]
        if alt_en:
            genre_entry['altEN'] = alt_en
        genres.append(genre_entry)

    # #361: attach the direct parents. Computed over the full closure, then
    # restricted to genres that survived the filters above, so the tree view
    # never gets an id it cannot resolve.
    kept = {g['id'] for g in genres}
    direct = _direct_parents(closure)
    verwaist = sorted(
        p for cid in kept for p in direct.get(cid, ()) if p not in kept
    )
    if verwaist:
        raise SystemExit(
            "genres.xml: %d direct parent(s) point at categories that are not "
            "in the index, e.g. %s. Fix the data before building."
            % (len(verwaist), ', '.join(verwaist[:5]))
        )
    for genre in genres:
        parents = direct.get(genre['id'], [])
        if parents:
            genre['parents'] = parents

    roots = sum(1 for g in genres if not g.get('parents'))
    edges = sum(len(g.get('parents', ())) for g in genres)
    print(f"   Found {len(genres)} genres "
          f"({edges} direct parent edges, {roots} roots)")
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

    The genre hierarchy used to live here too, as a third map holding parent
    *names* and the full transitive closure. It was dropped in #361: the tree
    view needs ids and direct parents, and both now sit on the genre entries
    themselves (see parse_genres).
    """
    print("\n🗺️  Building performance Maps...")

    maps = {
        'conceptToLemmas': {},
        'genreToWorks': {}
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
        'version': '1.9.3',  # 1.2.0: Authority migration (genre ptrs, person-works derivation, Frauendienst split). 1.2.1: WZB-Lemmata + Varianten + Werk-Eintrag. 1.2.2: #104 FLG/FLG1-Werk-Titel + work_571 biblStruct auf Vollmann-Profe/Neumann 1990. 1.3.0: #113-Followup — alternative-Terms in concepts.xml getrennt von Primär-Term (altDE/altEN/altNormalized) statt last-wins-Overwrite. 1.4.0: #44/#115 variants.xml aus Korpus regeneriert via scripts/sync/extract-variants.py (+64.287 Formen, 192.472→256.759). 1.4.1: #125 deterministischer Build (generatedAt entfernt, gzip mtime=0). 1.4.2: #143 HH-Genre-Korrektur (Marienleben → Geistliche Rede, work_137). 1.4.3: #143 APO-Gattungs-Metadaten nach Terrahe (work_568: Prosaroman/Antikenroman/Liebes-Abenteuerroman/Exempel/Fürstenspiegel). 1.4.4: #115 Kategorie-A-Stub-Backfill (+125 Lemma-Stubs in lexicon.xml). 1.5.0: Audit #5 — parse_genres last-wins-Fix: alternative-Terms überschreiben den Primär-Term nicht mehr (250 Kategorien korrigiert), altDE/altEN/altNormalized analog concepts. 1.6.0: #161 posAll[] — alle <pos>-Werte eines Lemmas (Multi-POS wie lemma_79188 salve NOM+VRB), pos bleibt Erstwert. 1.6.1: #189 GWTK-Pilot — variants.xml +2 Typen (rotte/rotten unter lemma_4954) + GWTK-Formen-Zuwachs aus der Neu-Annotation. 1.6.2: #224 NFC-Unicode-Komposition im Normalizer — zerlegte Umlaute (o + U+0308) werden jetzt komponiert, bevor die Umlaut-Regeln greifen; korrigiert 'hugo von mühldorf' zu 'hugo von muehldorf' in persons.xml (die Quelldatei traegt dort ein zerlegtes ue). 1.6.3: #235 kaputte Tilden in URLs (kombinierendes U+0303 hinter einem Leerzeichen statt ASCII-Tilde) in 24 works.xml-Notizen repariert; die gleichen Notizen stehen im TEI-Header, dort ohne Indexwirkung. 1.6.4: #138 814 Strophenziffern aus dem HUG-Verstext entfernt (706 davon pos=DIG, 108 unannotiert); variants.xml verliert dadurch den Typ type_195524 'cxlvix', der nur in HUG vorkam. 1.6.5: #236 FR3-Metadaten auf den Supplementband 2000 umgestellt (ISBN 3-525-82504-8, Hrsg. Haustein/Stackmann, Reihenband 232) und Zotero-Title-Case 'Teil Ii'/'Teil Iii' repariert; variants.xml unveraendert. 1.7.0: kuratierte Lemma-Angaben im Index: lemma.origin (Herkunftssprache aus <etym type="borrowing">, Schicht B von #28) sowie sense.definition und sense.comment (Prosa aus <def> bzw. <note type="comment">), jeweils nur wenn im Lexikon vorhanden. Erster Eintrag: lemma_37818 Abba (aramaeische Gottesanrede, KZW 30.07.2026). 1.7.1: #228 works.xml-Autornamen werden wie im Korpus-Index mit itertext() und Whitespace-Kollaps gelesen; work_563 trug den Umbruch der XML-Einrueckung bis in api/works/work_563.json. 1.8.0: #307 altNames/altNormalized je Person aus persons.xml persName[@type="alternative"] (134 Formen bei 80 Personen, nach exaktem Text auf 100 dedupliziert); die beiden Listen sind index-parallel, xml:lang wird nicht indexiert. 1.8.1: #193 Baustein 1 — lemma_3036 Ingliart von Personenname auf Pferdename umklassifiziert (concept_21012000 Maennlich/Mann + concept_23112500 Personennamen raus, concept_14012100 Haustiere/Namen + concept_23221000 Pferd und Reiten/Namen rein, wie bei den neun anderen arthurischen Pferden). Belegt durch Pz. 389,26 'mit den kurzen oeren ingliart' und 398,14; Quelle Borek 2023. Der dritte Korpus-Token REN_242090_0 'ingligar von jelezie' steht in einem Ritter-Katalog und haengt vermutlich falsch an diesem Lemma; das ist ein aelterer Befund, liegt bei KZW und beruehrt die Klassifikation des Lemmas nicht. 1.9.0: #361 genre.parents[] — direkte Eltern als IDs, aus der transitiven Reduktion der in genres.xml gespeicherten vollen Hülle (3.175 Kanten → 615 Kategorien mit 0 bis 4 direkten Eltern, zwei Wurzeln, Baumtiefe 9). Ersetzt maps.genreHierarchy, das Eltern-*Namen* und die volle Hülle trug und dessen einziger Konsument die „UND“-Kette im Gattungs-Explorer war. 1.9.1: #369 Nachlauf — variants.xml verliert den Typ type_218598 'stât' unter lemma_5732. Er hing an einem einzigen Korpus-Token (SKT_502140_4), und das war ein Fehltag: 'mîn gedanc an ir vil hôhe stât' ist das Verb. Nach der Korrektur auf lemma_5710 ist der Typ unbelegt. Gleiche Mechanik wie 1.6.4 (type_195524 'cxlvix'). 1.9.2: #367 — variants.xml gewinnt zwei Typen unter lemma_7338 (waer): type_372363 fuer die Schreibung waeren (CHH) und type_372364 fuer woren (FR3). Neu gepraegt statt umgehaengt, weil eine bestehende Nummer sonst an zwei Lemmata haenge und extract-variants.py sie der haeufigeren Seite zuschlaege, also weiter dem Verb (KZW, #367). Kein Typ wird unbelegt: type_273621 faellt von 5.641 auf 5.603, type_273624 von 471 auf 470, type_273713 von 111 auf 110. 1.9.3: #216 Punkt 3, Nachtrag - variants.xml gewinnt type_372365 fuer die Schreibung frô unter lemma_7260 (RVBR). Dieselbe Mechanik und dieselbe Begruendung wie 1.9.2: neu gepraegt statt umgehaengt, denn frô ist bereits als type_25866 unter lemma_7250 (vrô 'froh') gefuehrt, und eine Nummer an zwei Lemmata schluege extract-variants.py der haeufigeren Seite zu. Kein Typ wird unbelegt.
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

    # Serialize to JSON (einmal encodieren — Duplikat zu build-corpus-index.py, bewusst)
    json_bytes = json.dumps(index, ensure_ascii=False, separators=(',', ':')).encode('utf-8')

    # Get uncompressed size
    uncompressed_size = len(json_bytes)

    # mtime=0: kein Zeitstempel im gzip-Header — Builds aus identischem
    # Quellstand sind byte-identisch (#125, Muster wie naming-index-Builder)
    with gzip.GzipFile(OUTPUT_FILE, mode='wb', mtime=0) as f:
        f.write(json_bytes)

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
