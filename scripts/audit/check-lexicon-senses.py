#!/usr/bin/env python3
"""Pre-flight check: every <entry> in lexicon.xml must have at least one <sense>.

Run before any commit that touches authority-files/lexicon.xml.

Usage:
    py scripts/audit/check-lexicon-senses.py [--lexicon <path>]

Exits 0 on success, 1 on violations.
"""

import sys
import argparse
from pathlib import Path

try:
    from lxml import etree
except ImportError:
    sys.exit("ERROR: lxml not installed — run: pip install lxml")

NS_TEI = "http://www.tei-c.org/ns/1.0"
NS_XML  = "http://www.w3.org/XML/1998/namespace"

PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_LEX  = PROJECT_ROOT / "authority-files" / "lexicon.xml"


def check(lex_path: Path) -> list[str]:
    ns = {"tei": NS_TEI}
    doc = etree.parse(str(lex_path))
    bad = []
    for entry in doc.iter(f"{{{NS_TEI}}}entry"):
        if entry.find("tei:sense", ns) is None:
            xml_id = entry.get(f"{{{NS_XML}}}id", "<no id>")
            orth_el = entry.find(f".//{{{NS_TEI}}}orth")
            orth = orth_el.text.strip() if orth_el is not None and orth_el.text else "?"
            bad.append(f"  {xml_id} ({orth})")
    return bad


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check all lexicon.xml entries have at least one <sense>")
    parser.add_argument("--lexicon", "-l", default=str(DEFAULT_LEX), help="Path to lexicon.xml")
    args = parser.parse_args()

    lex_path = Path(args.lexicon)
    if not lex_path.exists():
        sys.exit(f"ERROR: lexicon not found: {lex_path}")

    violations = check(lex_path)
    if violations:
        print(f"FAIL — {len(violations)} entr{'y' if len(violations)==1 else 'ies'} without <sense> in {lex_path.name}:")
        for v in violations:
            print(v)
        sys.exit(1)

    print(f"OK — all entries in {lex_path.name} have at least one <sense>")
