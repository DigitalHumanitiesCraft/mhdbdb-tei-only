#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Position-parity test helper (#131, CONTRACTS §B "Position Counting").

Runs the REAL extract_word_data() from scripts/build-corpus-index.py against a
single TEI file and prints JSON {wordCount, lemmata} on stdout, so the Playwright
spec testing/tests/position-parity.spec.js can compare Python build-time word
positions against the JS runtime reader (tei-text-reader.js).

This deliberately imports the production build function instead of
re-implementing the counting rule — testing a copy would not catch drift in the
real code. build-corpus-index.py is hyphenated (not importable by name), so it is
loaded via importlib; its `if __name__ == '__main__'` guard keeps the import
side-effect free.

Usage:
    python3.13 extract_word_positions.py <tei_file_path> [text_id]

Output (stdout, UTF-8 JSON):
    {"wordCount": 142, "lemmata": {"lemma_1": [0, 2], ...}}
(The full words[] list extract_word_data also returns is omitted — unused by the
spec, and ~wordCount entries of needless payload.)
"""
import sys
import json
import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = REPO_ROOT / "scripts" / "build-corpus-index.py"


def load_extract_word_data():
    """Load the real extract_word_data() from the hyphenated build script."""
    spec = importlib.util.spec_from_file_location("build_corpus_index", BUILD_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.extract_word_data


def main():
    if len(sys.argv) < 2:
        print("usage: extract_word_positions.py <tei_file_path> [text_id]", file=sys.stderr)
        sys.exit(2)

    tei_path = Path(sys.argv[1])
    text_id = sys.argv[2] if len(sys.argv) > 2 else tei_path.stem

    if not tei_path.exists():
        print(f"TEI file not found: {tei_path}", file=sys.stderr)
        sys.exit(2)

    extract_word_data = load_extract_word_data()
    _words, lemmata, word_count, _line_starts, _line_ends = extract_word_data(tei_path, text_id)

    json.dump(
        {"wordCount": word_count, "lemmata": lemmata},
        sys.stdout,
        ensure_ascii=False,
    )


if __name__ == "__main__":
    main()
