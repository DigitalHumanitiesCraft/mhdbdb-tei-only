#!/usr/bin/env python3
"""
Enhance works.xml with Editor Metadata from Zotero API

Fetches bibliographic data from the MHDBDB Zotero collection via API
and updates authority-files/works.xml with <biblStruct> elements containing
editor information.

This script implements Issue #19: Add <editor> metadata from Zotero to TEI headers.

Workflow:
1. Fetch items from Zotero API (group 5043625, collection 7JU362QV)
2. Extract editor data from JSON response
3. Match items by callNumber (sigle) to works in works.xml
4. Replace/update <biblStruct> elements with editor metadata
5. Handle xml:id conflicts automatically

The script can be run multiple times safely - it removes any existing biblStruct
elements before adding new ones, preventing duplicates.

Usage:
    # Fetch from API and update works.xml
    python scripts/data-wrangling/enhance_works_with_zotero.py

    # Preview changes without modifying files
    python scripts/data-wrangling/enhance_works_with_zotero.py --dry-run

    # Save API response for offline use
    python scripts/data-wrangling/enhance_works_with_zotero.py --cache

    # Use cached data (offline mode)
    python scripts/data-wrangling/enhance_works_with_zotero.py --offline

After running:
    python scripts/data-wrangling/sync_tei_headers.py --works  # Sync to TEI headers
    python scripts/build-authority-index.py                    # Rebuild index

API Details:
- Group ID: 5043625 (Mittelhochdeutsche Begriffsdatenbank)
- Collection ID: 7JU362QV
- Endpoint: https://api.zotero.org/groups/{group_id}/collections/{collection_id}/items
- Authentication: Not required (public group)
- Pagination: 100 items per request
"""

from lxml import etree
from collections import defaultdict
import logging
import argparse
import requests
import time
import json
import re
from pathlib import Path
from typing import Dict, List, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Zotero API configuration
ZOTERO_API_BASE = "https://api.zotero.org"
ZOTERO_GROUP_ID = "5043625"
ZOTERO_COLLECTION_ID = "7JU362QV"
ZOTERO_CACHE_FILE = Path("scripts/data-wrangling/.zotero_cache.json")

# Rate limiting
REQUEST_DELAY = 0.3  # seconds between requests (~3 requests/second)
MAX_RETRIES = 3
RETRY_BACKOFF = 2  # exponential backoff multiplier


def fetch_zotero_data_from_api(group_id: str, collection_id: str) -> List[dict]:
    """
    Fetch all items from Zotero API with pagination.

    Args:
        group_id: Zotero group ID
        collection_id: Zotero collection ID

    Returns:
        List of item dictionaries from API

    Raises:
        requests.RequestException: On network errors
        ValueError: On invalid API response
    """
    url = f"{ZOTERO_API_BASE}/groups/{group_id}/collections/{collection_id}/items"
    items = []
    start = 0
    limit = 100

    logger.info(f"Fetching items from Zotero API: {url}")

    retry_count = 0
    while True:
        try:
            # Make request with pagination
            response = requests.get(
                url,
                params={'limit': limit, 'start': start},
                headers={'User-Agent': 'MHDBDB-TEI-Works-Update/2.0'}
            )

            # Handle rate limiting (429 Too Many Requests)
            if response.status_code == 429:
                if retry_count >= MAX_RETRIES:
                    raise requests.RequestException(f"Rate limit exceeded after {MAX_RETRIES} retries")

                wait_time = RETRY_BACKOFF ** retry_count
                logger.warning(f"Rate limited, waiting {wait_time}s before retry...")
                time.sleep(wait_time)
                retry_count += 1
                continue

            # Check for errors
            if response.status_code != 200:
                raise requests.RequestException(
                    f"API request failed with status {response.status_code}: {response.text}"
                )

            # Reset retry count on success
            retry_count = 0

            # Parse JSON
            batch = response.json()

            if not isinstance(batch, list):
                raise ValueError(f"Expected list from API, got {type(batch)}")

            items.extend(batch)
            logger.info(f"Fetched {len(batch)} items (total: {len(items)})")

            # Check if more pages exist
            if len(batch) < limit:
                logger.info(f"Finished fetching all {len(items)} items")
                break

            # Move to next page
            start += limit

            # Rate limiting delay
            time.sleep(REQUEST_DELAY)

        except requests.RequestException as e:
            logger.error(f"Network error while fetching from API: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from API: {e}")
            raise ValueError(f"Invalid JSON from API: {e}")

    return items


def cache_zotero_data(items: List[dict], cache_file: Path):
    """
    Save API response to cache file for offline use.

    Args:
        items: List of Zotero items from API
        cache_file: Path to cache file
    """
    from datetime import datetime

    cache_data = {
        'timestamp': datetime.now().isoformat(),
        'item_count': len(items),
        'items': items
    }

    cache_file.parent.mkdir(parents=True, exist_ok=True)

    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cache_data, f, indent=2)

    logger.info(f"Cached {len(items)} items to {cache_file}")


def load_cached_data(cache_file: Path) -> Optional[List[dict]]:
    """
    Load items from cache file.

    Args:
        cache_file: Path to cache file

    Returns:
        List of cached items, or None if cache doesn't exist
    """
    if not cache_file.exists():
        logger.warning(f"Cache file not found: {cache_file}")
        return None

    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)

        items = cache_data.get('items', [])
        timestamp = cache_data.get('timestamp', 'unknown')

        logger.info(f"Loaded {len(items)} items from cache (timestamp: {timestamp})")
        return items

    except (json.JSONDecodeError, IOError) as e:
        logger.error(f"Error loading cache: {e}")
        return None


def convert_to_title_case(text: str) -> str:
    """
    Convert German bibliographic titles to Title Case.

    Rules:
    - Capitalize first word
    - Capitalize all words except common German articles, prepositions, and conjunctions
    - Always capitalize nouns (heuristic: if already capitalized in source, keep it)
    - Preserve text after colons/subtitles

    Args:
        text: Title in sentence case

    Returns:
        Title in Title Case
    """
    if not text:
        return text

    # German lowercase words (articles, prepositions, conjunctions)
    lowercase_words = {
        'der', 'die', 'das', 'den', 'dem', 'des',  # articles
        'ein', 'eine', 'einer', 'einen', 'einem', 'eines',  # indefinite articles
        'und', 'oder', 'aber', 'als',  # conjunctions
        'in', 'im', 'an', 'am', 'auf', 'aus', 'bei', 'für', 'mit', 'nach',  # prepositions
        'von', 'vom', 'zu', 'zum', 'zur', 'über',
        'durch', 'gegen', 'ohne', 'um', 'bis',
    }

    # Split by spaces while preserving special characters
    words = text.split()
    result = []

    for i, word in enumerate(words):
        # Check if word ends with punctuation
        trailing_punct = ''
        clean_word = word

        # Extract trailing punctuation
        match = re.match(r'^(.+?)([.,;:!?\)\]\}]+)$', word)
        if match:
            clean_word = match.group(1)
            trailing_punct = match.group(2)

        # First word or word after colon/dash is always capitalized
        if i == 0 or (i > 0 and words[i-1].endswith((':',  '–', '—'))):
            result.append(clean_word.capitalize() + trailing_punct)
        # Check if lowercase word (and not already capitalized = likely not a noun)
        elif clean_word.lower() in lowercase_words and not clean_word[0].isupper():
            result.append(clean_word.lower() + trailing_punct)
        # Otherwise capitalize
        else:
            result.append(clean_word.capitalize() + trailing_punct)

    return ' '.join(result)


def api_item_to_biblstruct(item_data: dict, sigle: str, notes: List[str] = None) -> Optional[etree._Element]:
    """
    Convert Zotero API JSON item to TEI <biblStruct> element.

    Mimics the structure from Zotero's XML export to maintain compatibility
    with existing works.xml format. Converts titles to Title Case.

    Args:
        item_data: Zotero item data from API
        sigle: Sigle/callNumber for this item
        notes: List of note texts attached to this item

    Returns:
        TEI <biblStruct> element (always returns element, never None)
    """
    if notes is None:
        notes = []
    TEI_NS_URI = "http://www.tei-c.org/ns/1.0"

    # Extract creators
    creators = item_data.get('creators', [])

    # Filter editors and authors
    editors = [c for c in creators if c.get('creatorType') == 'editor']
    authors = [c for c in creators if c.get('creatorType') == 'author']

    # Note: We no longer require editors - update ALL items with Zotero data
    # Previously returned None if no editors, but now we process all items

    # Build <biblStruct> element
    biblstruct = etree.Element(f"{{{TEI_NS_URI}}}biblStruct")

    # Set type from itemType
    item_type = item_data.get('itemType', 'unknown')
    biblstruct.set('type', item_type)

    # Generate xml:id (sigle_sigle format, e.g., TKA_TKA)
    biblstruct.set('{http://www.w3.org/XML/1998/namespace}id', f"{sigle}_{sigle}")

    # Add corresp URL (Zotero item URL)
    key = item_data.get('key', '')
    if key:
        biblstruct.set('corresp', f"http://zotero.org/groups/5043625/items/{key}")

    biblstruct.set('key', sigle)

    # Add <analytic> section for articles/bookSections
    if item_type in ['journalArticle', 'bookSection', 'conferencePaper']:
        analytic = etree.SubElement(biblstruct, f"{{{TEI_NS_URI}}}analytic")

        # Title (article/chapter title)
        if 'title' in item_data and item_data['title']:
            title = etree.SubElement(analytic, f"{{{TEI_NS_URI}}}title")
            title.set('level', 'a')
            title.text = convert_to_title_case(item_data['title'])

        # Authors
        for author_data in authors:
            author = etree.SubElement(analytic, f"{{{TEI_NS_URI}}}author")
            if 'firstName' in author_data and 'lastName' in author_data:
                name_text = f"{author_data.get('firstName', '')} {author_data.get('lastName', '')}".strip()
                name = etree.SubElement(author, f"{{{TEI_NS_URI}}}name")
                name.text = name_text
            elif 'name' in author_data:
                name = etree.SubElement(author, f"{{{TEI_NS_URI}}}name")
                name.text = author_data['name']

    # Create <monogr> section
    monogr = etree.SubElement(biblstruct, f"{{{TEI_NS_URI}}}monogr")

    # Title (book/journal title)
    if item_type in ['journalArticle']:
        # For journal articles, use publicationTitle
        if 'publicationTitle' in item_data and item_data['publicationTitle']:
            title = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}title")
            title.set('level', 'j')
            title.text = convert_to_title_case(item_data['publicationTitle'])
    elif item_type in ['bookSection']:
        # For book sections, use bookTitle
        if 'bookTitle' in item_data and item_data['bookTitle']:
            title = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}title")
            title.set('level', 'm')
            title.text = convert_to_title_case(item_data['bookTitle'])
    else:
        # For books and other types, use title
        if 'title' in item_data and item_data['title']:
            title = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}title")
            title.text = convert_to_title_case(item_data['title'])

    # For books (not bookSections/articles), add authors to monogr
    if item_type in ['book']:
        for author_data in authors:
            author = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}author")
            if 'firstName' in author_data and 'lastName' in author_data:
                name_text = f"{author_data.get('firstName', '')} {author_data.get('lastName', '')}".strip()
                name = etree.SubElement(author, f"{{{TEI_NS_URI}}}name")
                name.text = name_text
            elif 'name' in author_data:
                name = etree.SubElement(author, f"{{{TEI_NS_URI}}}name")
                name.text = author_data['name']

    # ISBN
    if 'ISBN' in item_data and item_data['ISBN']:
        idno = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}idno")
        idno.set('type', 'ISBN')
        idno.text = item_data['ISBN']

    # callNumber as idno
    if 'callNumber' in item_data and item_data['callNumber']:
        idno = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}idno")
        idno.set('type', 'callNumber')
        idno.text = item_data['callNumber']

    # Editors
    for editor_data in editors:
        editor = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}editor")

        if 'firstName' in editor_data and 'lastName' in editor_data:
            forename = etree.SubElement(editor, f"{{{TEI_NS_URI}}}forename")
            forename.text = editor_data['firstName']

            surname = etree.SubElement(editor, f"{{{TEI_NS_URI}}}surname")
            surname.text = editor_data['lastName']
        elif 'name' in editor_data:
            editor.text = editor_data['name']

    # Edition
    if 'edition' in item_data and item_data['edition']:
        edition = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}edition")
        edition.text = str(item_data['edition'])

    # Imprint section
    imprint = etree.SubElement(monogr, f"{{{TEI_NS_URI}}}imprint")

    if 'place' in item_data and item_data['place']:
        pubPlace = etree.SubElement(imprint, f"{{{TEI_NS_URI}}}pubPlace")
        pubPlace.text = item_data['place']

    # Pages (biblScope unit="page")
    if 'pages' in item_data and item_data['pages']:
        biblScope = etree.SubElement(imprint, f"{{{TEI_NS_URI}}}biblScope")
        biblScope.set('unit', 'page')
        biblScope.text = item_data['pages']

    # Volume (biblScope unit="volume")
    if 'volume' in item_data and item_data['volume']:
        biblScope = etree.SubElement(imprint, f"{{{TEI_NS_URI}}}biblScope")
        biblScope.set('unit', 'volume')
        biblScope.text = str(item_data['volume'])

    # Issue (biblScope unit="issue") for journal articles
    if 'issue' in item_data and item_data['issue']:
        biblScope = etree.SubElement(imprint, f"{{{TEI_NS_URI}}}biblScope")
        biblScope.set('unit', 'issue')
        biblScope.text = str(item_data['issue'])

    if 'publisher' in item_data and item_data['publisher']:
        publisher = etree.SubElement(imprint, f"{{{TEI_NS_URI}}}publisher")
        publisher.text = item_data['publisher']

    if 'date' in item_data and item_data['date']:
        date = etree.SubElement(imprint, f"{{{TEI_NS_URI}}}date")
        date.text = str(item_data['date'])

    # Series section (if applicable)
    if 'series' in item_data and item_data['series']:
        series = etree.SubElement(biblstruct, f"{{{TEI_NS_URI}}}series")
        series_title = etree.SubElement(series, f"{{{TEI_NS_URI}}}title")
        series_title.set('level', 's')
        series_title.text = convert_to_title_case(item_data['series'])

        # Series number (biblScope unit="series_number")
        if 'seriesNumber' in item_data and item_data['seriesNumber']:
            biblScope = etree.SubElement(series, f"{{{TEI_NS_URI}}}biblScope")
            biblScope.set('unit', 'series_number')
            biblScope.text = str(item_data['seriesNumber'])

    # Note section (from Zotero notes)
    if notes:
        # Concatenate all notes for this item
        note_text = ' '.join(notes).strip()
        if note_text:
            note = etree.SubElement(biblstruct, f"{{{TEI_NS_URI}}}note")
            note.text = note_text

    return biblstruct


def extract_zotero_data(items: List[dict]) -> Dict[str, List[etree._Element]]:
    """
    Extract biblStruct elements indexed by callNumber from Zotero API items.

    Also builds a map of parent items to their notes for inclusion in biblStruct.

    Args:
        items: List of Zotero items from API

    Returns:
        Dictionary mapping callNumber (sigle) to list of biblStruct elements
    """
    zotero_data = defaultdict(list)

    logger.info(f"Processing {len(items)} items from Zotero")

    # First pass: build parent → notes mapping
    notes_map = {}
    for item in items:
        data = item.get('data', {})
        if data.get('itemType') == 'note':
            parent_key = data.get('parentItem')
            if parent_key:
                if parent_key not in notes_map:
                    notes_map[parent_key] = []
                notes_map[parent_key].append(data.get('note', ''))

    logger.info(f"Found {len(notes_map)} items with notes")

    # Second pass: process bibliographic items
    items_processed = 0
    items_with_call_number = 0

    for item in items:
        data = item.get('data', {})

        # Skip non-bibliographic items
        if data.get('itemType') in ['note', 'attachment']:
            continue

        # Get callNumber (sigle)
        call_number = data.get('callNumber', '').strip()

        if not call_number:
            continue

        items_with_call_number += 1

        # Get notes for this item
        item_key = item.get('key', '')
        item_notes = notes_map.get(item_key, [])

        # Convert to biblStruct (now always returns a biblStruct, never None)
        biblstruct = api_item_to_biblstruct(data, call_number, item_notes)

        zotero_data[call_number].append(biblstruct)
        items_processed += 1
        logger.debug(f"Added biblStruct for callNumber: {call_number}")

    logger.info(f"Processed {items_with_call_number} items with callNumber")
    logger.info(f"Generated {items_processed} biblStruct elements")
    logger.info(f"Indexed {len(zotero_data)} unique callNumbers")

    return dict(zotero_data)


def parse_xml_file(filename):
    """Parse XML file with namespace handling."""
    try:
        # Use remove_blank_text=True to enable pretty-printing on write
        parser = etree.XMLParser(recover=True, remove_blank_text=True)
        tree = etree.parse(filename, parser)
        return tree
    except Exception as e:
        logger.error(f"Error parsing {filename}: {e}")
        raise


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
        base_id = f"biblStruct_{sigle}" if sigle else "biblStruct_unknown"
    else:
        base_id = original_id

    if base_id not in used_ids:
        used_ids.add(base_id)
        return base_id

    if sigle and f"{base_id}_{sigle}" not in used_ids:
        unique_id = f"{base_id}_{sigle}"
        used_ids.add(unique_id)
        return unique_id

    counter = 1
    while f"{base_id}_{counter}" in used_ids:
        counter += 1

    unique_id = f"{base_id}_{counter}"
    used_ids.add(unique_id)
    return unique_id


def replace_editions_with_biblstructs(works_tree, zotero_data, dry_run=False):
    """
    Replace bibl type='edition' elements with matching biblStruct elements.

    Args:
        works_tree: Parsed works.xml tree
        zotero_data: Dictionary of callNumber -> biblStruct elements
        dry_run: If True, don't modify the tree

    Returns:
        Tuple of (total_replacements, works_with_replacements, missing_sigles)
    """
    ns = {'tei': 'http://www.tei-c.org/ns/1.0'}

    used_xml_ids = set()

    # Collect existing xml:id values
    existing_ids = works_tree.xpath('//@xml:id', namespaces={'xml': 'http://www.w3.org/XML/1998/namespace'})
    for existing_id in existing_ids:
        used_xml_ids.add(existing_id)

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

        # Extract sigles
        sigles = extract_work_sigles(work)
        if not sigles:
            logger.warning(f"No sigles found for work {work_id}")
            continue

        logger.debug(f"Work {work_id} has sigles: {sigles}")

        # Check if we have Zotero matches for this work
        has_zotero_match = any(sigle in zotero_data for sigle in sigles)

        # Remove existing biblStruct elements FIRST (before creating new ones)
        # This frees up their xml:ids for reuse
        if has_zotero_match:
            existing_biblstructs = work.xpath('.//tei:biblStruct', namespaces=ns)
            if existing_biblstructs and not dry_run:
                logger.debug(f"Removing {len(existing_biblstructs)} existing biblStruct elements from {work_id}")
                for existing_bs in existing_biblstructs:
                    # Remove xml:id from used_ids set so it can be reused
                    old_id = existing_bs.get('{http://www.w3.org/XML/1998/namespace}id')
                    if old_id and old_id in used_xml_ids:
                        used_xml_ids.remove(old_id)
                    existing_bs.getparent().remove(existing_bs)
                total_removed += len(existing_biblstructs)

        # NOW create new biblStruct elements from Zotero
        matching_biblstructs = []
        matched_sigles = set()

        for sigle in sigles:
            if sigle in zotero_data:
                for biblstruct in zotero_data[sigle]:
                    biblstruct_copy = etree.fromstring(etree.tostring(biblstruct))

                    # Fix xml:id conflicts (should not happen now since we freed IDs above)
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

        if matching_biblstructs and not dry_run:
            works_with_replacements += 1

            if edition_elements:
                # Replace existing edition elements
                logger.debug(f"Replacing {len(edition_elements)} edition elements with {len(matching_biblstructs)} biblStruct elements")

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
                # No existing edition elements, add at end
                logger.debug(f"No existing edition elements, adding {len(matching_biblstructs)} biblStruct elements at end")
                for biblstruct in matching_biblstructs:
                    work.append(biblstruct)
                    total_replacements += 1

        elif matching_biblstructs and dry_run:
            works_with_replacements += 1
            total_replacements += len(matching_biblstructs)

        elif edition_elements:
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
        for missing in missing_sigles[:10]:  # Show first 10
            logger.warning(f"  {missing}")
        if len(missing_sigles) > 10:
            logger.warning(f"  ... and {len(missing_sigles) - 10} more")

    return total_replacements, works_with_replacements, missing_sigles


def main():
    """Main function to orchestrate the Zotero API workflow."""
    parser = argparse.ArgumentParser(
        description='Enhance works.xml with editor metadata from Zotero API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch from API and update works.xml
  python scripts/data-wrangling/enhance_works_with_zotero.py

  # Preview changes without modifying files
  python scripts/data-wrangling/enhance_works_with_zotero.py --dry-run

  # Save API response for offline use
  python scripts/data-wrangling/enhance_works_with_zotero.py --cache

  # Use cached data (offline mode)
  python scripts/data-wrangling/enhance_works_with_zotero.py --offline

After running:
  python scripts/data-wrangling/sync_tei_headers.py --works
  python scripts/build-authority-index.py
        """
    )

    parser.add_argument('--cache', action='store_true',
                       help='Save API response to cache file')
    parser.add_argument('--offline', action='store_true',
                       help='Use cached data instead of fetching from API')
    parser.add_argument('--dry-run', action='store_true',
                       help='Preview changes without modifying files')

    args = parser.parse_args()

    works_file = 'authority-files/works.xml'

    try:
        # Display mode
        if args.dry_run:
            logger.info("=" * 60)
            logger.info("DRY RUN MODE - No files will be modified")
            logger.info("=" * 60)

        # Fetch or load data
        items = None

        if args.offline:
            logger.info("OFFLINE MODE - Using cached data")
            items = load_cached_data(ZOTERO_CACHE_FILE)
            if items is None:
                logger.error("No cache file found. Run without --offline first to fetch data.")
                return False
        else:
            logger.info("Fetching data from Zotero API...")
            items = fetch_zotero_data_from_api(ZOTERO_GROUP_ID, ZOTERO_COLLECTION_ID)

            if args.cache:
                cache_zotero_data(items, ZOTERO_CACHE_FILE)

        # Extract bibliographic data
        logger.info("Extracting bibliographic data from items...")
        zotero_data = extract_zotero_data(items)

        # Parse works.xml
        logger.info(f"Parsing {works_file}...")
        works_tree = parse_xml_file(works_file)

        # Replace editions with biblStruct elements
        logger.info("Replacing edition elements with biblStruct elements...")
        total_replacements, works_with_replacements, missing_sigles = replace_editions_with_biblstructs(
            works_tree, zotero_data, dry_run=args.dry_run
        )

        # Write modified XML
        if not args.dry_run:
            logger.info(f"Writing modified XML back to {works_file}...")
            works_tree.write(works_file, encoding='utf-8', xml_declaration=True, pretty_print=True)

        # Final summary
        logger.info("=" * 60)
        logger.info("Process completed successfully!")
        logger.info(f"Final summary:")
        logger.info(f"- {total_replacements} {'would be' if args.dry_run else ''} biblStruct elements added")
        logger.info(f"- {works_with_replacements} works {'would be' if args.dry_run else ''} modified")
        logger.info(f"- {len(missing_sigles)} sigles without matches")

        if not args.dry_run:
            logger.info("")
            logger.info("NEXT STEPS:")
            logger.info("  1. python scripts/data-wrangling/sync_tei_headers.py --works")
            logger.info("  2. python scripts/build-authority-index.py")

        logger.info("=" * 60)

        return True

    except Exception as e:
        logger.error(f"Error during processing: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
