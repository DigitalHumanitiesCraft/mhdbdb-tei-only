#!/usr/bin/env python3
"""
Split large TEI files into readable markdown chunks for LLM-based PoS validation.

This script extracts <w> elements from a TEI file and creates human-readable
markdown files with full context for linguistic analysis.

Usage:
    python scripts/split-tei-for-validation.py tei/ABG.tei.xml
    python scripts/split-tei-for-validation.py tei/ABG.tei.xml --chunk-size 50 --context-size 10
"""

import argparse
import sys
import io
from pathlib import Path
from lxml import etree

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# TEI namespace
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

# Punctuation that should NOT be followed by a space
NO_SPACE_AFTER = {'<', '(', '[', '{', '„'}

def extract_text_with_punctuation(root):
    """
    Extract text content including punctuation from <seg type="pc"> elements.
    Returns list of tuples: (text, is_word, xml_id) for sequential rendering.
    """
    text_elements = []

    # Get all <w> and <seg type="pc"> elements in document order
    for elem in root.xpath('.//tei:w | .//tei:seg[@type="pc"]', namespaces=NS):
        if elem.tag == f"{{{NS['tei']}}}w":
            text_elements.append({
                'text': "".join(elem.itertext()),
                'is_word': True,
                'xml_id': elem.get('{http://www.w3.org/XML/1998/namespace}id'),
            })
        elif elem.tag == f"{{{NS['tei']}}}seg" and elem.get('type') == 'pc':
            # Punctuation segment
            text_elements.append({
                'text': elem.text or '',
                'is_word': False,
                'xml_id': elem.get('{http://www.w3.org/XML/1998/namespace}id'),
            })

    return text_elements

def extract_words(tei_file):
    """Extract all <w> elements with their metadata and surrounding text."""
    tree = etree.parse(tei_file)
    root = tree.getroot()

    # Extract words with metadata
    words = []
    for w in root.xpath('.//tei:w', namespaces=NS):
        pos_value = w.get('pos', '')
        has_compound = ' ' in pos_value
        is_missing = not pos_value or pos_value.strip() == ''
        
        word_data = {
            'xml_id': w.get('{http://www.w3.org/XML/1998/namespace}id'),
            # FIXED: Use itertext() to handle nested tags like <hi>, <lb/>, etc.
            'text': "".join(w.itertext()),
            'pos': pos_value,
            'lemmaRef': w.get('lemmaRef', ''),
            'line_number': w.sourceline,
            'has_compound_pos': has_compound,
            'is_missing_pos': is_missing,
            'needs_validation': has_compound or is_missing
        }
        words.append(word_data)

    # Extract full text sequence with punctuation for context display
    text_elements = extract_text_with_punctuation(root)

    return words, text_elements

def create_chunks(words, text_elements, chunk_size=500):
    """Create chunks of words for validation. ALL words are targets."""
    if not words:
        print("No words found - nothing to validate.")
        return []

    chunks = []
    chunk_num = 0
    total_words = len(words)

    i = 0
    while i < total_words:
        chunk_num += 1

        # Get word range for this chunk
        start_idx = i
        end_idx = min(i + chunk_size, total_words)

        # Extract words for this chunk
        chunk_words = words[start_idx:end_idx]

        # Count special cases for statistics
        compound_count = sum(1 for w in chunk_words if w['has_compound_pos'])
        missing_count = sum(1 for w in chunk_words if w['is_missing_pos'])

        # Mark all words as targets (they all need validation)
        for w in chunk_words:
            w['is_target'] = True

        chunk = {
            'chunk_number': chunk_num,
            'word_count': len(chunk_words),
            'compound_count': compound_count,
            'missing_count': missing_count,
            'words': chunk_words,
            'text_elements': text_elements  # Pass all text elements for context rendering
        }

        chunks.append(chunk)
        i = end_idx

    return chunks

def format_chunk_as_markdown(chunk, total_chunks, sigle):
    """Format chunk as human-readable markdown for LLM analysis."""
    md = []

    # Header
    md.append(f"# {sigle} - Chunk {chunk['chunk_number']:03d}/{total_chunks:03d}")
    md.append(f"Words to validate: {chunk['word_count']} (⚠️ {chunk['compound_count']} compound | ❓ {chunk['missing_count']} missing)")
    md.append("")

    # Context text (continuous reading with punctuation)
    md.append("## CONTEXT TEXT")
    # Build text from text_elements, filtering to words in this chunk
    chunk_word_ids = {w['xml_id'] for w in chunk['words']}

    # Find the range of text elements that correspond to this chunk
    first_word_id = chunk['words'][0]['xml_id']
    last_word_id = chunk['words'][-1]['xml_id']

    # Find indices in text_elements
    start_idx = None
    end_idx = None
    for i, te in enumerate(chunk['text_elements']):
        if te['is_word'] and te['xml_id'] == first_word_id:
            start_idx = i
        if te['is_word'] and te['xml_id'] == last_word_id:
            end_idx = i + 1
            break

    # Build context text with punctuation and proper spacing
    if start_idx is not None and end_idx is not None:
        context_parts = []
        for i, te in enumerate(chunk['text_elements'][start_idx:end_idx]):
            # Add space before words (but not before the first element or after punctuation)
            if te['is_word'] and i > 0:
                # Check if previous element was punctuation
                prev_te = chunk['text_elements'][start_idx + i - 1]
                if prev_te['is_word']:  # Previous was a word, add space
                    context_parts.append(' ')
                else:  # Previous was punctuation
                    # Add space unless it's an opening punctuation mark
                    if prev_te['text'] not in NO_SPACE_AFTER:
                        context_parts.append(' ')
            
            # Add space before opening punctuation (if previous element wasn't also opening punctuation)
            elif not te['is_word'] and i > 0:
                if te['text'] in NO_SPACE_AFTER:
                    prev_te = chunk['text_elements'][start_idx + i - 1]
                    # Don't add space if previous was also opening punctuation (e.g. "([")
                    if prev_te['is_word'] or prev_te['text'] not in NO_SPACE_AFTER:
                        context_parts.append(' ')

            context_parts.append(te['text'])
        text_preview = "".join(context_parts)
    else:
        # Fallback to simple word joining if indices not found
        text_preview = " ".join(w['text'] for w in chunk['words'])

    md.append(text_preview)
    md.append("")

    # Word list with annotations
    md.append("## WORDS TO VALIDATE")
    md.append("(⚠️ = MUST disambiguate compound tag | ✓ = validate single tag | ❓ = missing PoS tag)")
    md.append("")

    for i, word in enumerate(chunk['words'], 1):
        if word['is_missing_pos']:
            marker = "❓"  # Missing tag - needs assignment
        elif word['has_compound_pos']:
            marker = "⚠️"  # Compound tag - needs disambiguation
        else:
            marker = "✓"  # Single tag - verify or correct
        md.append(f"{i}. {marker} {word['text']} ({word['pos']}) - {word['xml_id']}")

    md.append("")
    md.append("---")
    md.append("")
    md.append("**Follow the workflow rules in `.agent/workflows/pos-disambiguator.md`**")
    md.append("")
    md.append("Save your results as: `" + sigle + f"-chunk-{chunk['chunk_number']:03d}-result.md`")

    return "\n".join(md)

def save_chunks(chunks, output_dir, sigle):
    """Save chunks to markdown files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True, parents=True)

    total_chunks = len(chunks)

    for chunk in chunks:
        chunk_file = output_dir / f"{sigle}-chunk-{chunk['chunk_number']:03d}.md"

        md_content = format_chunk_as_markdown(chunk, total_chunks, sigle)

        with open(chunk_file, 'w', encoding='utf-8') as f:
            f.write(md_content)

        print(f"[OK] Created {chunk_file} ({chunk['word_count']} words, ⚠️ {chunk['compound_count']} compound, ❓ {chunk['missing_count']} missing)")

    # Save manifest
    manifest_file = output_dir / f"{sigle}-manifest.txt"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        f.write(f"SIGLE: {sigle}\n")
        f.write(f"Total chunks: {total_chunks}\n")
        f.write(f"\nChunk files:\n")
        for chunk in chunks:
            f.write(f"  {sigle}-chunk-{chunk['chunk_number']:03d}.md\n")

    print(f"\n[OK] Created manifest: {manifest_file}")

    return total_chunks

def main():
    parser = argparse.ArgumentParser(description='Split TEI file into markdown chunks for PoS validation')
    parser.add_argument('tei_file', help='Path to TEI file (e.g., tei/ABG.tei.xml)')
    parser.add_argument('--chunk-size', type=int, default=500, help='Number of words per chunk (default: 500)')
    parser.add_argument('--output-dir', default='temp/disambiguation', help='Output directory for chunks (default: temp/disambiguation)')

    args = parser.parse_args()

    # Extract SIGLE from filename
    tei_path = Path(args.tei_file)
    sigle = tei_path.stem

    print(f"Processing {tei_path}...")
    print(f"SIGLE: {sigle}")
    print(f"Chunk size: {args.chunk_size} words per chunk")
    print()

    # Extract words and text elements (with punctuation)
    words, text_elements = extract_words(tei_path)
    total_words = len(words)
    compound_count = sum(1 for w in words if w['has_compound_pos'])
    missing_count = sum(1 for w in words if w['is_missing_pos'])

    print(f"Total words: {total_words}")
    print(f"  ⚠️ Compound tags: {compound_count}")
    print(f"  ❓ Missing tags: {missing_count}")
    print()

    if total_words == 0:
        print("No words found. Exiting.")
        return 0

    # Create chunks
    chunks = create_chunks(words, text_elements, chunk_size=args.chunk_size)

    if not chunks:
        return 0

    print(f"Created {len(chunks)} chunks")
    print()

    # Save chunks
    total_chunks = save_chunks(chunks, args.output_dir, sigle)

    print()
    print("=" * 60)
    print("READY FOR LLM PROCESSING")
    print("=" * 60)
    print(f"Total chunks: {total_chunks}")
    print(f"Output directory: {args.output_dir}")
    print()
    print("Next steps:")
    print(f"1. Process each chunk with the pos-disambiguator agent")
    print(f"2. Agent saves results as {sigle}-chunk-XXX-result.md")
    print(f"3. Run merge script to assemble final TEI file")

    return 0

if __name__ == '__main__':
    sys.exit(main())