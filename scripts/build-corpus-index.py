#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Corpus Index

Generates pre-built corpus index from tei/ directory (667 TEI files).
Output: data/corpus-index.json.gz (~3-5 MB compressed)

Index structure (v4.0.1 - DOCUMENT-LEVEL):
{
  "version": "4.0.1",
  "generatedAt": "2025-01-01T00:00:00Z",
  "totalTexts": 667,
  "totalLemmata": 45000,
  "texts": [
    {
      "id": "ABG",
      "filename": "ABG.tei.xml",
      "title": "Von der Abgeschiedenheit",
      "author": "Meister Eckhart",
      "authorRef": "#person_445",
      "workRef": "#work_89",
      "genre": "genre_x",
      "wordCount": 1500,
      "words": ["lemma_879", "lemma_123", "lemma_879", ...],  # ALL words in <body>
      "lemmata": {
        "lemma_879": [0, 2, 15],  # Word positions
        "lemma_123": [1]
      }
    }
  ],
  "lemmaIndex": {
    "lemma_879": ["ABG", "BRZ", "HZU2"],  # Texts containing this lemma
    "lemma_123": ["ABG"]
  }
}
"""

import json
import gzip
import sys
import os
import time
from pathlib import Path
from datetime import datetime
from collections import defaultdict

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
TEI_DIR = PROJECT_ROOT / 'tei'
DATA_DIR = PROJECT_ROOT / 'data'
OUTPUT_FILE = DATA_DIR / 'corpus-index.json.gz'

# TEI namespace
TEI_NS = {'tei': 'http://www.tei-c.org/ns/1.0'}


def get_namespaces(tree):
    """
    Detect and return all namespaces in document (Critical Fix #2).
    """
    nsmap = tree.getroot().nsmap.copy()

    if None in nsmap:
        nsmap['tei'] = nsmap[None]
        del nsmap[None]

    if 'tei' not in nsmap:
        nsmap['tei'] = 'http://www.tei-c.org/ns/1.0'

    return nsmap


def extract_metadata(filepath):
    """Extract metadata from TEI file."""
    try:
        tree = etree.parse(str(filepath))
        ns = get_namespaces(tree)

        # Get sigle from filename or XML
        filename = filepath.name
        sigle = filename.replace('.tei.xml', '')

        # Try to get sigle from idno
        sigle_nodes = tree.xpath('//tei:idno[@type="sigle"]/text()', namespaces=ns)
        if sigle_nodes:
            sigle = sigle_nodes[0].strip()

        # Get title
        title_nodes = tree.xpath('//tei:titleStmt/tei:title/text()', namespaces=ns)
        title = title_nodes[0].strip() if title_nodes else sigle

        # Get author
        author = ''
        authorRef = ''
        author_nodes = tree.xpath('//tei:titleStmt/tei:author', namespaces=ns)
        if author_nodes:
            author_el = author_nodes[0]
            author = author_el.text.strip() if author_el.text else ''
            authorRef = author_el.get('ref', '')

        # Get work reference
        workRef = ''
        ms_id_nodes = tree.xpath('//tei:msIdentifier', namespaces=ns)
        if ms_id_nodes:
            workRef = ms_id_nodes[0].get('corresp', '')

        # Get genre (if available - may not be in all files)
        genre = ''
        # Genre might be in different places, try a few options
        genre_nodes = tree.xpath('//tei:keywords/tei:term[@type="genre"]/text()', namespaces=ns)
        if not genre_nodes:
            genre_nodes = tree.xpath('//tei:term[@type="genre"]/text()', namespaces=ns)
        if genre_nodes:
            genre = genre_nodes[0].strip()

        return {
            'id': sigle,
            'filename': filename,
            'title': title,
            'author': author,
            'authorRef': authorRef,
            'workRef': workRef,
            'genre': genre
        }

    except Exception as e:
        print(f"⚠️  Error extracting metadata from {filepath.name}: {e}")
        return None


def extract_word_data(filepath, text_id):
    """
    Extract word data using document-level indexing (v4.0.0).

    Returns: (words_list, lemmata_dict, word_count)
    where:
      words_list = ["lemma_879", "lemma_123", ...]  # ALL words in <body> in document order
      lemmata_dict = {"lemma_879": [0, 2, 15], ...}
    """
    try:
        tree = etree.parse(str(filepath))
        ns = get_namespaces(tree)

        # Get body element
        TEI = '{http://www.tei-c.org/ns/1.0}'
        body = tree.find(f'.//{TEI}body')
        if body is None:
            return [], {}, 0

        # Get ALL words in <body> in document order
        # Uses iter() with Clark notation — orders of magnitude faster than
        # xpath() with namespace mapping on large files (PL1: 0.2s vs timeout)
        word_els = [w for w in body.iter(f'{TEI}w') if w.get('lemmaRef')]

        words = []  # All lemma IDs in document order
        lemmata = defaultdict(list)
        word_count = 0

        for word_el in word_els:
            lemma_ref = word_el.get('lemmaRef')
            text_content = ''.join(word_el.itertext()).strip()

            if not text_content:
                continue

            # Extract lemma ID
            # Format: "lexicon.xml#lemma_879" -> "lemma_879"
            if '#' in lemma_ref:
                lemma_id = lemma_ref.split('#')[1]
            else:
                lemma_id = lemma_ref

            # Store word data (just lemma ID)
            word_idx = len(words)
            words.append(lemma_id)

            # Record position in lemma index
            lemmata[lemma_id].append(word_idx)
            word_count += 1

        return words, dict(lemmata), word_count

    except Exception as e:
        print(f"⚠️  Error extracting word data from {filepath.name}: {e}")
        return [], {}, 0


def process_tei_file(filepath):
    """Process single TEI file and return text data."""
    # Extract metadata
    metadata = extract_metadata(filepath)
    if not metadata:
        return None

    text_id = metadata['id']

    # Extract full word data (document-level)
    words, lemmata, word_count = extract_word_data(filepath, text_id)

    # Combine
    text_data = {
        **metadata,
        'wordCount': word_count,
        'words': words,
        'lemmata': lemmata
    }

    return text_data


def build_corpus_index():
    """Build complete corpus index from all TEI files."""
    print("\n🔨 Building corpus index...")
    print(f"TEI directory: {TEI_DIR}")

    # Get all TEI files
    tei_files = list(TEI_DIR.glob('*.tei.xml'))
    total_files = len(tei_files)

    print(f"Found {total_files} TEI files")

    if total_files == 0:
        print("❌ ERROR: No TEI files found!")
        sys.exit(1)

    # Process all files
    texts = []
    lemma_index = defaultdict(list)  # lemma_id -> list of text IDs

    start_time = time.time()

    for idx, filepath in enumerate(tei_files, 1):
        if idx % 10 == 0 or idx == total_files:
            elapsed = time.time() - start_time
            rate = idx / elapsed if elapsed > 0 else 0
            remaining = (total_files - idx) / rate if rate > 0 else 0
            print(f"   Processing {idx}/{total_files} ({rate:.1f} files/sec, ~{remaining:.0f}s remaining)...")

        text_data = process_tei_file(filepath)
        if not text_data:
            continue

        texts.append(text_data)

        # Build lemma index (reverse index: lemma -> texts)
        for lemma_id in text_data['lemmata'].keys():
            lemma_index[lemma_id].append(text_data['id'])

    # Sort texts by ID
    texts.sort(key=lambda t: t['id'])

    # Convert lemma_index to regular dict
    lemma_index = dict(lemma_index)

    # Build final index
    index = {
        'version': '4.0.1',  # 4.0.0: document-level indexing (removed paragraph logic). 4.0.1: WZB hinzugefügt
        'generatedAt': datetime.now().isoformat() + 'Z',
        'totalTexts': len(texts),
        'totalLemmata': len(lemma_index),
        'texts': texts,
        'lemmaIndex': lemma_index
    }

    # Statistics
    total_words = sum(t['wordCount'] for t in texts)
    avg_words = total_words // len(texts) if texts else 0

    print(f"\n📊 Statistics:")
    print(f"   Total texts: {len(texts):,}")
    print(f"   Total unique lemmata: {len(lemma_index):,}")
    print(f"   Total words: {total_words:,}")
    print(f"   Average words per text: {avg_words:,}")

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
    print(f"\n✅ Corpus index saved successfully!")


def main():
    """Main entry point."""
    print("=" * 60)
    print("MHDBDB Corpus Index Builder")
    print("=" * 60)

    try:
        # Build index
        index = build_corpus_index()

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
