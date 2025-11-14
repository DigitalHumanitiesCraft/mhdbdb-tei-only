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
from pathlib import Path
from lxml import etree

# TEI namespace
NS = {'tei': 'http://www.tei-c.org/ns/1.0'}

def extract_words(tei_file):
    """Extract all <w> elements with their metadata and surrounding text."""
    tree = etree.parse(tei_file)
    root = tree.getroot()

    words = []
    for w in root.xpath('.//tei:w', namespaces=NS):
        pos_value = w.get('pos', '')
        word_data = {
            'xml_id': w.get('{http://www.w3.org/XML/1998/namespace}id'),
            'text': w.text or '',
            'pos': pos_value,
            'lemmaRef': w.get('lemmaRef', ''),
            'line_number': w.sourceline,
            'has_compound_pos': ' ' in pos_value,
        }
        words.append(word_data)

    return words

def create_chunks(words, chunk_size=50, context_size=10):
    """Create overlapping chunks focused on compound PoS tags."""
    compound_indices = [i for i, w in enumerate(words) if w['has_compound_pos']]

    if not compound_indices:
        print("No compound PoS tags found - nothing to validate.")
        return []

    chunks = []
    chunk_num = 0

    i = 0
    while i < len(compound_indices):
        chunk_num += 1

        # Get compound tag indices for this chunk
        target_start_idx = i
        target_end_idx = min(i + chunk_size, len(compound_indices))

        # Get actual positions in full word list
        first_target_pos = compound_indices[target_start_idx]
        last_target_pos = compound_indices[target_end_idx - 1]

        # Add context words before and after
        context_start = max(0, first_target_pos - context_size)
        context_end = min(len(words), last_target_pos + context_size + 1)

        # Extract words for this chunk
        chunk_words = words[context_start:context_end]

        # Mark which words need disambiguation vs just validation
        for w in chunk_words:
            w_pos = words.index(w)
            w['is_compound_target'] = w_pos >= first_target_pos and w_pos <= last_target_pos and w['has_compound_pos']

        chunk = {
            'chunk_number': chunk_num,
            'compound_count': target_end_idx - target_start_idx,
            'total_words': len(chunk_words),
            'words': chunk_words
        }

        chunks.append(chunk)
        i = target_end_idx

    return chunks

def format_chunk_as_markdown(chunk, total_chunks, sigle):
    """Format chunk as human-readable markdown for LLM analysis."""
    md = []

    # Header
    md.append(f"# {sigle} - Chunk {chunk['chunk_number']:03d}/{total_chunks:03d}")
    md.append(f"Compound tags to disambiguate: {chunk['compound_count']} | Total words to validate: {chunk['total_words']}")
    md.append("")

    # Context text (continuous reading)
    md.append("## CONTEXT TEXT")
    text_preview = " ".join(w['text'] for w in chunk['words'])
    md.append(text_preview)
    md.append("")

    # Word list with annotations
    md.append("## WORDS TO VALIDATE")
    md.append("(⚠️ = MUST disambiguate compound tag | ✓ = validate single tag | ❓ = missing PoS tag)")
    md.append("")

    for i, word in enumerate(chunk['words'], 1):
        if word['is_compound_target']:
            marker = "⚠️"
        elif not word['pos'] or word['pos'].strip() == '':
            marker = "❓"
        else:
            marker = "✓"
        md.append(f"{i}. {marker} {word['text']} ({word['pos']}) - {word['xml_id']}")

    md.append("")
    md.append("---")
    md.append("")
    md.append("## INSTRUCTIONS FOR LLM")
    md.append("")
    md.append("Validate ALL words above using Middle High German grammar and context:")
    md.append("")
    md.append("1. For ⚠️ compound tags: Disambiguate to single PoS tag")
    md.append("2. For ✓ single tags: Verify correctness or suggest correction")
    md.append("3. For ❓ missing tags: Assign appropriate PoS tag based on context")
    md.append("4. Assess confidence: high/low")
    md.append("5. Provide brief reason")
    md.append("")
    md.append("Output format (one line per word):")
    md.append("```")
    md.append("xml_id | old_pos → new_pos | confidence | reason")
    md.append("```")
    md.append("")
    md.append("Save your results as: " + sigle + f"-chunk-{chunk['chunk_number']:03d}-result.md")

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

        print(f"[OK] Created {chunk_file} ({chunk['compound_count']} compound tags, {chunk['total_words']} total words)")

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
    parser.add_argument('--chunk-size', type=int, default=50, help='Number of compound tags per chunk (default: 50)')
    parser.add_argument('--context-size', type=int, default=10, help='Number of context words before/after (default: 10)')
    parser.add_argument('--output-dir', default='temp/disambiguation', help='Output directory for chunks (default: temp/disambiguation)')

    args = parser.parse_args()

    # Extract SIGLE from filename
    tei_path = Path(args.tei_file)
    sigle = tei_path.stem

    print(f"Processing {tei_path}...")
    print(f"SIGLE: {sigle}")
    print(f"Chunk size: {args.chunk_size} compound tags per chunk")
    print(f"Context size: {args.context_size} words before/after")
    print()

    # Extract words
    words = extract_words(tei_path)
    total_words = len(words)
    compound_tags = sum(1 for w in words if w['has_compound_pos'])

    print(f"Total words: {total_words}")
    print(f"Words with compound PoS tags: {compound_tags}")
    print()

    if compound_tags == 0:
        print("No compound tags found. Exiting.")
        return 0

    # Create chunks
    chunks = create_chunks(words, chunk_size=args.chunk_size, context_size=args.context_size)

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
