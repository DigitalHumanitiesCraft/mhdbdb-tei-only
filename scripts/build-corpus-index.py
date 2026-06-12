#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Corpus Index

Generates pre-built corpus index from tei/ directory (667 TEI files).
Output: data/corpus-index.json.gz (~3-5 MB compressed)

Index structure (v4.1.4 - DOCUMENT-LEVEL + LINE BOUNDARIES):
{
  "version": "4.1.4",
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
      "words": ["lemma_879", "lemma_123", "lemma_879", ...],  # all lemmatized <w> in <body> (only @lemmaRef-bearing)
      "lemmata": {
        "lemma_879": [0, 2, 15],  # Word positions
        "lemma_123": [1]
      },
      "lineStarts": [0, 8, 15, ...],   # word-index where each <l> starts (#47.3)
      "lineEnds":   [7, 14, 22, ...]   # word-index where each <l> ends (inclusive)
    }
  ],
  "lemmaIndex": {
    "lemma_879": ["ABG", "BRZ", "HZU2"],  # Texts containing this lemma
    "lemma_123": ["ABG"]
  }
}

Notes on lineStarts/lineEnds (added in v4.1.0 for #47.3):
- Same length as the number of <l> elements with at least one indexed word.
- Empty for prose texts without <l> elements (~10% of corpus).
- A lemma occurrence at position P is at Versanfang iff P in lineStarts,
  at Versende iff P in lineEnds.
- Words outside any <l> (e.g. inside <head>, <note>, mid-paragraph <fw>)
  match neither.
"""

import argparse
import json
import gzip
import subprocess
import sys
import os
import time
from pathlib import Path
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
    Extract word data using document-level indexing (v4.1.0).

    Returns: (words_list, lemmata_dict, word_count, line_starts, line_ends)
    where:
      words_list = ["lemma_879", "lemma_123", ...]  # ALL words in <body> in document order
      lemmata_dict = {"lemma_879": [0, 2, 15], ...}
      line_starts = [0, 8, 15, ...]  # word-index where each <l> starts
      line_ends   = [7, 14, 22, ...] # word-index where each <l> ends (inclusive)
    """
    try:
        tree = etree.parse(str(filepath))

        # Get body element
        TEI = '{http://www.tei-c.org/ns/1.0}'
        body = tree.find(f'.//{TEI}body')
        if body is None:
            return [], {}, 0, [], []

        words = []  # All lemma IDs in document order
        lemmata = defaultdict(list)
        word_count = 0

        line_starts = []
        line_ends = []
        # Stack tracks <l> nesting depth (in practice always 0 or 1, but defensive)
        # Each frame holds (first_w_idx, last_w_idx) for the currently-open <l>.
        l_stack = []

        # Single-pass iterwalk: start/end events for <w> and <l> together.
        # This avoids lxml's proxy-id instability between separate .iter() calls.
        for event, el in etree.iterwalk(body, events=('start', 'end'),
                                         tag=(f'{TEI}w', f'{TEI}l')):
            tag = el.tag

            if tag == f'{TEI}l':
                if event == 'start':
                    l_stack.append([None, None])  # [first_idx, last_idx]
                else:  # end
                    frame = l_stack.pop()
                    if frame[0] is not None:
                        line_starts.append(frame[0])
                        line_ends.append(frame[1])
                continue

            # tag == <w>, event == 'start' (we ignore <w>-end events)
            if event != 'start':
                continue

            lemma_ref = el.get('lemmaRef')
            if not lemma_ref:
                continue
            text_content = ''.join(el.itertext()).strip()
            if not text_content:
                continue

            lemma_id = lemma_ref.split('#')[1] if '#' in lemma_ref else lemma_ref

            word_idx = len(words)
            words.append(lemma_id)
            lemmata[lemma_id].append(word_idx)
            word_count += 1

            # If we're inside one or more <l>, update each open frame.
            # (Inner-most <l> defines Versanfang/Versende; outer frames are
            # extremely rare in TEI but cost nothing to track.)
            for frame in l_stack:
                if frame[0] is None:
                    frame[0] = word_idx
                frame[1] = word_idx

        return words, dict(lemmata), word_count, line_starts, line_ends

    except Exception as e:
        print(f"⚠️  Error extracting word data from {filepath.name}: {e}")
        return [], {}, 0, [], []


def process_tei_file(filepath):
    """Process single TEI file and return text data."""
    # Extract metadata
    metadata = extract_metadata(filepath)
    if not metadata:
        return None

    text_id = metadata['id']

    # Extract full word data + line boundaries (document-level)
    words, lemmata, word_count, line_starts, line_ends = extract_word_data(filepath, text_id)

    # Combine
    text_data = {
        **metadata,
        'wordCount': word_count,
        'words': words,
        'lemmata': lemmata,
        'lineStarts': line_starts,
        'lineEnds': line_ends
    }

    return text_data


def build_corpus_index():
    """Build complete corpus index from all TEI files."""
    print("\n🔨 Building corpus index...")
    print(f"TEI directory: {TEI_DIR}")

    # Get all TEI files
    # glob-Reihenfolge ist OS-abhängig — sortiert für deterministische Index-Bytes, #125
    tei_files = sorted(TEI_DIR.glob('*.tei.xml'))
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
        'version': '4.1.4',  # 4.0.0: document-level indexing. 4.0.1: WZB. 4.1.0: lineStarts/lineEnds für #47.3. 4.1.1: #23 Stanza-Wraps. 4.1.2: #104 Sigle-Titel-Differenzierung. 4.1.3: #110 WVV 478 Stanza-Wraps. 4.1.4: #125 deterministischer Build (generatedAt entfernt, sorted glob, gzip mtime=0).
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

    # mtime=0: kein Zeitstempel im gzip-Header — Builds aus identischem
    # Quellstand sind byte-identisch (#125, Muster wie naming-index-Builder)
    with gzip.GzipFile(OUTPUT_FILE, mode='wb', mtime=0) as f:
        f.write(json_data.encode('utf-8'))

    # Get compressed size
    compressed_size = OUTPUT_FILE.stat().st_size

    compression_ratio = (1 - compressed_size / uncompressed_size) * 100

    print(f"   Uncompressed: {uncompressed_size / (1024 * 1024):.2f} MB")
    print(f"   Compressed: {compressed_size / (1024 * 1024):.2f} MB")
    print(f"   Compression: {compression_ratio:.1f}%")
    print(f"\n✅ Corpus index saved successfully!")


def check_working_tree(directory, allow_dirty):
    """Pre-flight check: warn (or fail) when directory has uncommitted or
    untracked TEI files. Prevents accidentally bundling work-in-progress
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
    parser = argparse.ArgumentParser(description="Build MHDBDB corpus index from tei/")
    parser.add_argument(
        '--allow-dirty', action='store_true',
        help="Build even if tei/ has untracked or modified files (use for local tests)."
    )
    args = parser.parse_args()

    print("=" * 60)
    print("MHDBDB Corpus Index Builder")
    print("=" * 60)

    check_working_tree(TEI_DIR.relative_to(PROJECT_ROOT), args.allow_dirty)

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
