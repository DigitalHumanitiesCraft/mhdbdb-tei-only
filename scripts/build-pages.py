#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build Pages — inject the shared navigation + footer into every site HTML page.

Single source of truth:
  includes/_nav.html     -> page region between <!-- NAV:START key=... --> / <!-- NAV:END -->
  includes/_footer.html  -> page region between <!-- FOOTER:START --> / <!-- FOOTER:END -->

{{ROOT}} in the partials is replaced per page ('' for root pages, '../' for pages
one directory deep). The active nav item (the <a data-nav="..."> matching the page
key) gets aria-current="page" + text-slate-900 font-semibold.

First run is self-migrating: a page that has no NAV markers yet but does have a
<header>...</header> block has that block replaced by the markered nav (same for
<footer>...</footer>). Thereafter only the marked region is rewritten, so the build
is idempotent (a second run produces no diff).

Line endings are preserved per file (LF stays LF, CRLF stays CRLF) so the build
never produces a spurious whole-file diff on Windows checkouts.

Usage:
  python scripts/build-pages.py            # rewrite changed pages, print summary
  python scripts/build-pages.py --check    # exit 1 if any page is out of sync (CI gate), no writes
"""

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
INCLUDES = REPO_ROOT / "includes"

# page path (relative to repo root) -> (active nav key or None, {{ROOT}} prefix)
PAGES = {
    "index.html": ("start", ""),
    "korpus.html": ("korpus", ""),
    "impressum.html": (None, ""),
    "barrierefreiheit.html": (None, ""),
    "hilfe.html": ("hilfe", ""),
    "hilfe-daten.html": ("hilfe", ""),
    "hilfe-daten-beitragen.html": ("hilfe", ""),
    "hilfe-korpussuche.html": ("hilfe", ""),
    "hilfe-playground.html": ("hilfe", ""),
    "hilfe-schema.html": ("hilfe", ""),
    "lemma/index.html": (None, "../"),
    "playground/index.html": ("playground", "../"),
}

NAV_START_RE = re.compile(r"<!-- NAV:START[^>]*-->", re.I)
NAV_BLOCK_RE = re.compile(r"<!-- NAV:START[^>]*-->.*?<!-- NAV:END -->", re.S | re.I)
FOOTER_BLOCK_RE = re.compile(r"<!-- FOOTER:START -->.*?<!-- FOOTER:END -->", re.S | re.I)
HEADER_MIGRATE_RE = re.compile(r"[ \t]*<header\b.*?</header>", re.S | re.I)
FOOTER_MIGRATE_RE = re.compile(r"[ \t]*<footer\b.*?</footer>", re.S | re.I)
LEADING_COMMENT_RE = re.compile(r"\s*<!--.*?-->\s*", re.S)


def strip_leading_comment(text):
    m = LEADING_COMMENT_RE.match(text)
    return text[m.end():] if m else text


def load_partials():
    nav = strip_leading_comment((INCLUDES / "_nav.html").read_text(encoding="utf-8").replace("\r\n", "\n")).strip()
    footer = strip_leading_comment((INCLUDES / "_footer.html").read_text(encoding="utf-8").replace("\r\n", "\n")).strip()
    # Guard: a partial body must never contain marker text, or injection would
    # produce nested/duplicate markers and break idempotency.
    for name, body, tokens in (("_nav.html", nav, ("NAV:START", "NAV:END")),
                               ("_footer.html", footer, ("FOOTER:START", "FOOTER:END"))):
        for tok in tokens:
            if tok in body:
                raise SystemExit(f"includes/{name}: body contains marker text '{tok}' "
                                 f"— partials must not contain NAV/FOOTER marker comments")
    return nav, footer


def render_nav(nav, root, active_key):
    out = nav.replace("{{ROOT}}", root)
    if active_key:
        def mark(m):
            tag = m.group(0)
            tag = tag.replace("text-slate-600", "text-slate-900 font-semibold")
            tag = tag.replace("<a ", '<a aria-current="page" ', 1)
            return tag
        out = re.compile(r'<a\b[^>]*\bdata-nav="' + re.escape(active_key) + r'"[^>]*>').sub(mark, out)
    return out


def build_page(text, active_key, root, nav, footer):
    """Return the page text with the nav/footer regions (re)generated. text uses \\n."""
    key_attr = f" key={active_key}" if active_key else ""
    nav_block = f"<!-- NAV:START{key_attr} -->\n{render_nav(nav, root, active_key)}\n<!-- NAV:END -->"
    footer_block = f"<!-- FOOTER:START -->\n{footer.replace('{{ROOT}}', root)}\n<!-- FOOTER:END -->"

    if NAV_START_RE.search(text):
        text = NAV_BLOCK_RE.sub(lambda m: nav_block, text, count=1)
    elif HEADER_MIGRATE_RE.search(text):
        text = HEADER_MIGRATE_RE.sub(lambda m: nav_block, text, count=1)
    else:
        raise ValueError("no NAV markers and no <header> to migrate")

    if FOOTER_BLOCK_RE.search(text):
        text = FOOTER_BLOCK_RE.sub(lambda m: footer_block, text, count=1)
    elif FOOTER_MIGRATE_RE.search(text):
        text = FOOTER_MIGRATE_RE.sub(lambda m: footer_block, text, count=1)
    else:
        raise ValueError("no FOOTER markers and no <footer> to migrate")

    return text


def main():
    ap = argparse.ArgumentParser(description="Inject shared nav/footer partials into site pages.")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if any page is out of sync with the partials; do not write")
    args = ap.parse_args()

    nav, footer = load_partials()
    changed, drift, errors = [], [], []

    for rel, (active_key, root) in PAGES.items():
        path = REPO_ROOT / rel
        if not path.exists():
            errors.append(f"{rel}: file missing")
            continue
        raw = path.read_text(encoding="utf-8")
        newline = "\r\n" if "\r\n" in raw else "\n"
        norm = raw.replace("\r\n", "\n")
        try:
            built = build_page(norm, active_key, root, nav, footer)
        except ValueError as exc:
            errors.append(f"{rel}: {exc}")
            continue
        if built != norm:
            if args.check:
                drift.append(rel)
            else:
                path.write_bytes(built.replace("\n", newline).encode("utf-8"))
                changed.append(rel)

    if errors:
        for e in errors:
            print(f"ERROR {e}", file=sys.stderr)
        return 2

    if args.check:
        if drift:
            print(f"OUT OF SYNC ({len(drift)} of {len(PAGES)} pages):")
            for d in drift:
                print(f"  {d}")
            print("Run `python scripts/build-pages.py` and commit the result.")
            return 1
        print(f"OK — all {len(PAGES)} pages in sync with includes/_nav.html + includes/_footer.html")
        return 0

    if changed:
        print(f"{len(changed)} page(s) updated:")
        for c in changed:
            print(f"  {c}")
    else:
        print(f"0 pages updated — all {len(PAGES)} already in sync")
    return 0


if __name__ == "__main__":
    sys.exit(main())
