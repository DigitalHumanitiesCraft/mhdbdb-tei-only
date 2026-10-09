#!/usr/bin/env python3
"""Bibliografie der Textreihentypologie: Zotero-Gruppe -> statisches HTML (#93).

Die alte Seite (marketext.at/Textreihentypologie) lud die Bibliografie zur Laufzeit
per Zotpress aus der oeffentlichen Zotero-Gruppe 4876216 nach. Die Unterseite
textreihen/ hat kein Backend und keine Laufzeit-Abhaengigkeit: dieses Skript holt
die Haupteintraege einmal, formatiert sie mit dem Zotero-Stil (Harvard, wie die alte
Seite) und schreibt sie zwischen die Marker BIB:START/BIB:END in
textreihen/bibliography.html. Der Rohstand liegt als Schnappschuss in
textreihen/data/zotero-schnappschuss.json, damit der Build ohne Netz reproduzierbar ist.

Aktualisieren, wenn sich die Zotero-Gruppe aendert:
  python scripts/build-textreihen-bibliography.py            # holt neu, schreibt Schnappschuss + Seite
  python scripts/build-textreihen-bibliography.py --offline  # baut nur aus dem Schnappschuss
  python scripts/build-textreihen-bibliography.py --check    # exit 1, wenn die Seite vom Schnappschuss abweicht
"""

import argparse
import html
import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGE = REPO_ROOT / "textreihen" / "bibliography.html"
SNAPSHOT = REPO_ROOT / "textreihen" / "data" / "zotero-schnappschuss.json"

GROUP = 4876216
API = f"https://api.zotero.org/groups/{GROUP}/items/top"
STYLE = "harvard-cite-them-right"
LOCALE = "en-US"
PAGE_SIZE = 100
SKIP_TYPES = {"note", "attachment"}
ENTRY_RE = re.compile(r'<div class="csl-entry">(.*)</div>', re.S)
URL_RE = re.compile(r"(?<![\"'>=])(https?://[^\s<]+[^\s<.,;:)\]])")
BLOCK_RE = re.compile(r"<!-- BIB:START -->.*?<!-- BIB:END -->", re.S)


def fetch_all():
    items, start = [], 0
    while True:
        q = urllib.parse.urlencode({
            "format": "json", "include": "data,bib", "style": STYLE, "locale": LOCALE,
            "limit": PAGE_SIZE, "start": start,
        })
        req = urllib.request.Request(f"{API}?{q}", headers={"Zotero-API-Version": "3"})
        with urllib.request.urlopen(req, timeout=60) as r:
            batch = json.load(r)
        items.extend(batch)
        if len(batch) < PAGE_SIZE:
            return items
        start += PAGE_SIZE


def reduce_items(raw):
    """Nur, was die Seite braucht. Unbekannte Eintragsformen sind ein harter Fehler."""
    out, skipped = [], 0
    for it in raw:
        d = it["data"]
        if d["itemType"] in SKIP_TYPES:
            skipped += 1
            continue
        m = ENTRY_RE.search(it.get("bib") or "")
        if not m:
            raise SystemExit(f"Eintrag {it['key']} hat keinen Bibliografie-Block")
        out.append({
            "key": it["key"],
            "version": it["version"],
            "itemType": d["itemType"],
            # ohne Autor*in (Wiki-Artikel, Webseiten) sortiert der Titel; sonst stuenden sie alle vor "Achnitz"
            "sort": (it.get("meta", {}).get("creatorSummary") or d.get("title") or "").lower(),
            "date": it.get("meta", {}).get("parsedDate") or "",
            "title": d.get("title") or "",
            "tags": sorted({t["tag"] for t in d.get("tags", [])}),
            "bib": m.group(1).strip(),
        })
    out.sort(key=lambda e: (e["sort"], e["date"], e["title"].lower(), e["key"]))
    return out, skipped


def linkify(bib):
    # Der Zotero-Stil liefert Adressen als Klartext. Sie werden zu Links, ausser sie stehen schon in einem.
    if "<a " in bib:
        return bib
    return URL_RE.sub(lambda m: f'<a href="{m.group(1)}" target="_blank" rel="noopener">{m.group(1)}</a>', bib)


def render(entries):
    tags = sorted({t for e in entries for t in e["tags"]}, key=str.lower)
    lines = [f'<!-- BIB:START -->',
             f'<p class="tr-bib-count" id="bibCount" data-total="{len(entries)}">{len(entries)} Einträge</p>',
             '<ol class="tr-bib-list" id="bibList">']
    for e in entries:
        data_tags = html.escape("|".join(e["tags"]), quote=True)
        lines.append(f'<li class="tr-bib-entry" id="bib-{e["key"]}" data-tags="{data_tags}">{linkify(e["bib"])}</li>')
    lines.append("</ol>")
    lines.append("<!-- BIB:END -->")
    return "\n".join(lines), tags


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--offline", action="store_true", help="aus dem Schnappschuss bauen, kein Netz")
    ap.add_argument("--check", action="store_true", help="nur prüfen, nichts schreiben (impliziert --offline)")
    args = ap.parse_args()

    if args.offline or args.check:
        entries = json.loads(SNAPSHOT.read_text(encoding="utf-8"))["entries"]
        skipped = 0
    else:
        entries, skipped = reduce_items(fetch_all())
        snap = {"group": GROUP, "style": STYLE, "locale": LOCALE, "entries": entries}
        SNAPSHOT.write_text(json.dumps(snap, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    block, tags = render(entries)
    text = PAGE.read_text(encoding="utf-8")
    if not BLOCK_RE.search(text):
        raise SystemExit(f"{PAGE.name}: Marker BIB:START/BIB:END fehlen")
    new = BLOCK_RE.sub(lambda m: block, text, count=1)
    if args.check:
        if new != text:
            print("textreihen/bibliography.html weicht vom Schnappschuss ab")
            return 1
        print(f"OK: {len(entries)} Einträge, {len(tags)} Schlagwörter, Seite stimmt mit dem Schnappschuss überein")
        return 0
    if new != text:
        PAGE.write_text(new, encoding="utf-8", newline="")
    print(f"{len(entries)} Einträge ({skipped} Notizen/Anhänge übersprungen), {len(tags)} Schlagwörter, Seite {'geändert' if new != text else 'unverändert'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
