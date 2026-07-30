#!/usr/bin/env python3
"""Zahlen hinter den zwei Reader-Änderungen aus #250 messen und reproduzierbar halten.

Beide Änderungen hängen an Korpuseigenschaften, die sich mit jedem Ingest
verschieben. Die Zahlen stehen deshalb nicht nur als Kommentar im Code, sondern
kommen von hier.

TEIL A, Abschnitt „Editorische Eingriffe" im Metadatenpanel
-----------------------------------------------------------
Alle 667 Header führen ein <editorialDecl>, der Inhalt ist aber gemischt: die
Mehrheit der direkten <p>-Kinder erklärt nur, wie lokale Dateireferenzen im
Repository aufzulösen sind, je einmal deutsch und englisch. Das ist eine Aussage
über das Repository, nicht über den Text, und gehört nicht in die Leseansicht.

Strukturell allein ist das nicht trennbar (FR1-FR3 tragen ihre
Divergenz-Hinweise ebenfalls als direkte <p xml:lang="de">), deshalb der
Präfix-Test. Er greift nur am Absatzanfang, damit WZB seinen Mischabsatz behält.

Parität zu assets/js/rendering/tei-text-reader.js:

  EDITORIAL_DECL_BOILERPLATE_PREFIXES  -> Modulkonstante
  extractMetadata(), Schritt 1c
      querySelectorAll('editorialDecl p')  = alle Nachfahren, auch die in
                                             <normalization>
      verworfen wird: leerer Text, @xml:lang="en", Präfix-Treffer

TEIL B, Label über einer eigenen <head>-Überschrift
---------------------------------------------------
Seit #236 trägt jeder Frauenlob-Ton ein <head>; darüber stand weiterhin das
synthetische „Lied 5". Die naheliegende Lösung, das Label zu unterdrücken, wäre
falsch: dieses Skript zählt, in wie vielen Fällen der <head> die Nummer aus @n
mitführt. Solange das nirgends zutrifft, ist das Label die einzige sichtbare
Zählung des Abschnitts.

Parität zu assets/js/rendering/tei-text-reader.js:

  divHasOwnHead(div)      nur DIREKTE <head>-Kinder
  divLabels               die sieben typisierten divs mit Label

TEIL C, <head> als erstes Element-Kind
--------------------------------------
Das CSS zieht die Überschrift per Nachbarselektor an ihr Label
(.tei-div-header-above-head + .section-head). Der greift nur, wenn der <head>
als erstes Kind gerendert wird und das h3 damit direkt auf das Label folgt.
Teil C misst, für wie viele der Teil-B-Fälle das gilt.

Usage:
    python scripts/audit/count-editorial-notes-and-div-heads.py
    python scripts/audit/count-editorial-notes-and-div-heads.py --text FR3
"""
import argparse
import glob
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

TEI = 'http://www.tei-c.org/ns/1.0'
XML_LANG = '{http://www.w3.org/XML/1998/namespace}lang'

# Parität: EDITORIAL_DECL_BOILERPLATE_PREFIXES in tei-text-reader.js
BOILERPLATE_PREFIXES = ('Lokale Dateireferenzen', 'Local file references')

# Parität: divLabels in tei-text-reader.js, case 'div'
DIV_LABELS = {
    'song': 'Lied', 'chapter': 'Kapitel', 'recipe': 'Rezept',
    'number': 'Nr.', 'section': 'Abschnitt',
    'colophon': 'Kolophon', 'parallel': 'Parallelüberlieferung',
}


def normalize(el):
    """Textinhalt wie textContent.replace(/\\s+/g,' ').trim() im Browser."""
    return ' '.join(''.join(el.itertext()).split())


def editorial_notes(tree):
    """Absätze des editorialDecl in drei Gruppen, in Dokumentreihenfolge.

    Die dritte Gruppe ist die interessante: englischsprachige Absätze, die NICHT
    das Boilerplate sind. Der Reader verwirft sie, weil die Oberfläche deutsch
    ist. Solange die Gruppe leer bleibt, kostet das keine inhaltliche Angabe;
    füllt sie sich, ist die Sprachregel zu überdenken. Ohne diese Trennung
    verschwände der Fall in einer Sammelzahl.
    """
    decl = tree.find(f'.//{{{TEI}}}editorialDecl')
    if decl is None:
        return [], [], []
    kept, boilerplate, english_only = [], [], []
    for p in decl.iter(f'{{{TEI}}}p'):
        text = normalize(p)
        if not text:
            continue
        if text.startswith(BOILERPLATE_PREFIXES):
            boilerplate.append(text)
        elif p.get(XML_LANG) == 'en':
            english_only.append(text)
        else:
            kept.append(text)
    return kept, boilerplate, english_only


def labelled_divs_with_head(tree):
    """(div_type, @n, head_text, head_ist_erstes_kind) je typisiertem div mit eigenem <head>."""
    out = []
    for div in tree.iter(f'{{{TEI}}}div'):
        div_type = div.get('type', '')
        if div_type not in DIV_LABELS:
            continue
        heads = [c for c in div if c.tag == f'{{{TEI}}}head']
        if not heads:
            continue
        children = [c for c in div if isinstance(c.tag, str)]
        out.append((
            div_type,
            (div.get('n') or '').strip(),
            ' '.join(normalize(h) for h in heads),
            bool(children) and children[0].tag == f'{{{TEI}}}head',
        ))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--text', help='eine Sigle im Detail')
    ap.add_argument('--corpus', default='tei', help='Korpusverzeichnis')
    args = ap.parse_args()
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    files = sorted(glob.glob(str(Path(args.corpus) / '*.tei.xml')))
    if not files:
        sys.exit(f'Keine TEI-Dateien in {args.corpus}/')

    if args.text:
        path = Path(args.corpus) / f'{args.text}.tei.xml'
        if not path.exists():
            sys.exit(f'{path} gibt es nicht')
        tree = etree.parse(str(path))
        kept, boilerplate, english_only = editorial_notes(tree)
        print(f'{args.text}: {len(kept)} Absätze im Abschnitt, '
              f'{len(boilerplate)} Boilerplate, {len(english_only)} nur englisch\n')
        for note in kept:
            print(f'  + {note}')
        for note in boilerplate:
            print(f'  - [Boilerplate] {note[:90]}')
        for note in english_only:
            print(f'  - [englisch] {note[:90]}')
        divs = labelled_divs_with_head(tree)
        print(f'\n{len(divs)} typisierte div mit eigenem <head>:')
        for div_type, n, head, first in divs[:20]:
            flag = '' if first else '   (head nicht erstes Kind)'
            print(f'  {div_type} n={n!r}: {head[:70]!r}{flag}')
        return

    # --- Teil A ---
    dist = Counter()
    empty = []
    boilerplate_total = 0
    english_total = []
    for f in files:
        kept, boilerplate, english_only = editorial_notes(etree.parse(f))
        dist[len(kept)] += 1
        boilerplate_total += len(boilerplate)
        sig = Path(f).name.split('.')[0]
        english_total.extend((sig, text) for text in english_only)
        if not kept:
            empty.append(sig)
    print(f'TEIL A: editorialDecl in {len(files)} Texten')
    print(f'  verworfenes Boilerplate: {boilerplate_total}')
    print(f'  verworfen, weil nur englisch und KEIN Boilerplate: {len(english_total)}')
    for sig, text in english_total[:5]:
        print(f'      {sig}: {text[:90]}')
    if english_total:
        print('      -> die Sprachregel kostet hier inhaltliche Angaben, bitte pruefen')
    print(f'  Texte ohne jeden Absatz danach: {len(empty)}'
          + (f' -> {", ".join(empty)}' if empty else ''))
    print('  Absätze je Text: ' + ', '.join(
        f'{k}: {dist[k]}' for k in sorted(dist)))

    # --- Teil B und C ---
    per_type = defaultdict(Counter)
    texts = Counter()
    total_labelled = Counter()
    first_child = Counter()
    for f in files:
        tree = etree.parse(f)
        sig = Path(f).name.split('.')[0]
        for div in tree.iter(f'{{{TEI}}}div'):
            if div.get('type', '') in DIV_LABELS:
                total_labelled[div.get('type')] += 1
        for div_type, n, head, is_first in labelled_divs_with_head(tree):
            texts[sig] += 1
            first_child[is_first] += 1
            if not n:
                per_type[div_type]['ohne @n'] += 1
            elif n in head:
                per_type[div_type]['@n im head enthalten'] += 1
            else:
                per_type[div_type]['@n fehlt im head'] += 1

    with_head = sum(sum(c.values()) for c in per_type.values())
    print(f'\nTEIL B: typisierte div mit eigenem <head>: '
          f'{with_head} von {sum(total_labelled.values())} in {len(texts)} Texten')
    for div_type in sorted(per_type):
        counts = per_type[div_type]
        print(f'  {div_type:9s} {sum(counts.values()):5d} von {total_labelled[div_type]:5d}'
              f'   ' + ', '.join(f'{k}: {v}' for k, v in counts.most_common()))
    carries = sum(c['@n im head enthalten'] for c in per_type.values())
    has_n = sum(sum(c.values()) - c['ohne @n'] for c in per_type.values())
    print(f'  davon mit @n: {has_n}, und in {carries} Fällen steht die Nummer im <head>')
    if carries == 0:
        print('  -> Label unterdrücken würde die einzige sichtbare Zählung entfernen')
    print(f'\nTEIL C: <head> ist erstes Element-Kind: '
          f'{first_child[True]} von {with_head} '
          f'(Nachbarselektor im CSS greift), sonst {first_child[False]}')
    print('  Top-Texte: ' + ', '.join(f'{s} {c}' for s, c in texts.most_common(8)))


if __name__ == '__main__':
    main()
