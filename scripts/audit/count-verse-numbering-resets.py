#!/usr/bin/env python3
"""Reichweite der #138-Verszaehlung messen: welche <div> setzen die sichtbare
Randnummerierung zurueck, und wie viele Randnummern kommen dadurch hinzu.

Hintergrund: der Reader zeigt eine Randnummer an der ersten numerisch
nummerierten <l> (Anker) und danach an jeder <l>, deren @n durch 5 teilbar
ist (#127). Seit #138 ist der Anker nicht mehr dokumentweit einmalig: ein
<div>, das eine eigene DURCHLAUFENDE Zaehlung bei n="1" beginnt, setzt ihn
zurueck, damit jedes Lied bzw. Kapitel seine sichtbare "1" bekommt.

Warum ein eigenes Skript: die Zahlen in docs/FEATURES.md und im Kommentar
in assets/js/rendering/tei-text-reader.js waren zweimal per Textfenster-
Heuristik geschaetzt und beide Male falsch (Review-Befund 28.07.: FR3 +141
ist arithmetisch unmoeglich, weil der Text nur 139 <l n="1"> hat). Dieses
Skript baut stattdessen die Render-Reihenfolge nach und zaehlt den
Unterschied zwischen "mit Reset" und "ohne Reset" direkt.

Nachgebaute Logik, Paritaet zu assets/js/rendering/tei-text-reader.js:

  divRestartsNumbering(div)   -> :366
      a) die erste numerische <l> im Teilbaum traegt n="1"
      b) n="1" kommt im Teilbaum GENAU EINMAL vor
      (querySelectorAll('l[n]') greift auf ALLE Nachfahren, auch ueber
      geschachtelte <div> hinweg; iter() bildet das ab)

  Randnummer sichtbar    -> :487
      isNumeric UND (noch kein Anker gesetzt ODER int(n) % 5 == 0)

Der Walk ist eine Pre-Order-Traversierung ueber <body>, weil der Renderer
rekursiv ueber die Kindelemente laeuft. <note> rendert seine Kinder mit
(:512-523), Notes werden also bewusst nicht uebersprungen.

Usage:
    python scripts/audit/count-verse-numbering-resets.py           # Gesamtreport
    python scripts/audit/count-verse-numbering-resets.py --top 15  # laengere Bestenliste
    python scripts/audit/count-verse-numbering-resets.py --text PZ # ein Text im Detail
"""
import argparse
import re
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

# Gemeinsame Korpusauswahl (#287).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from corpus_files import corpus_files  # noqa: E402

TEI_NS = 'http://www.tei-c.org/ns/1.0'

NUMERIC = re.compile(r'^\d+$')


def div_conditions(div_el):
    """(Bedingung a, Bedingung b) fuer ein <div>.

    a) die erste numerische <l> traegt n="1"
    b) n="1" kommt im Teilbaum genau einmal vor

    Getrennt zurueckgegeben, weil die Doku ausweisen muss, wie viele <div>
    allein an (b) scheitern: das ist die Menge mit strophenlokaler Zaehlung,
    also der eigentliche Schutz vor der #127-Regression.
    """
    first = None
    einsen = 0
    for line in div_el.iter(f'{{{TEI_NS}}}l'):
        n = line.get('n')
        if n is None or not NUMERIC.match(n):
            continue
        if first is None:
            first = n
        if n == '1':
            einsen += 1
    return first == '1', einsen == 1


def div_restarts_numbering(div_el):
    """Parity zu tei-text-reader.js:366 (divRestartsNumbering)."""
    a, b = div_conditions(div_el)
    return a and b


def simulate(body, with_reset, ignore_condition_b=False):
    """Randnummern zaehlen, die der Reader sichtbar rendert.

    Gibt (sichtbare Nummern, Reset-Ereignisse) zurueck. Ein Reset-Ereignis
    ist ein qualifizierendes <div>; bei geschachtelten qualifizierenden
    <div> zaehlt jedes einzeln, sichtbar wird davon aber nur eine Nummer.
    """
    anchor_shown = False
    visible = 0
    resets = 0
    for el in body.iter():
        tag = etree.QName(el).localname if isinstance(el.tag, str) else None
        if tag == 'div':
            a, b = div_conditions(el)
            if a and (b or ignore_condition_b):
                resets += 1
                if with_reset:
                    anchor_shown = False
        elif tag == 'l':
            n = el.get('n')
            if n is None or not NUMERIC.match(n):
                continue
            if not anchor_shown or int(n) % 5 == 0:
                visible += 1
                anchor_shown = True
    return visible, resets


def analyse(path):
    tree = etree.parse(str(path))
    body = tree.find(f'.//{{{TEI_NS}}}body')
    if body is None:
        return None

    types = Counter()
    divs_total = 0
    starts_at_one = 0        # Bedingung (a) erfuellt
    rejected_by_b = 0        # (a) erfuellt, (b) nicht: strophenlokale Zaehlung
    for div in body.iter(f'{{{TEI_NS}}}div'):
        divs_total += 1
        a, b = div_conditions(div)
        if not a:
            continue
        starts_at_one += 1
        if b:
            types[div.get('type') or '(ohne @type)'] += 1
        else:
            rejected_by_b += 1

    qualifying = sum(types.values())
    mit, _ = simulate(body, with_reset=True)
    ohne, _ = simulate(body, with_reset=False)
    nur_a, _ = simulate(body, with_reset=True, ignore_condition_b=True)

    return {
        'sigle': path.name.replace('.tei.xml', ''),
        'divs_total': divs_total,
        'starts_at_one': starts_at_one,
        'qualifying': qualifying,
        'rejected_by_b': rejected_by_b,
        'types': types,
        'numbers_with': mit,
        'numbers_without': ohne,
        'extra': mit - ohne,
        'extra_only_a': nur_a - ohne,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--top', type=int, default=10, help='Laenge der Bestenliste (Default 10)')
    ap.add_argument('--text', help='nur diese Sigle, mit Detailausgabe')
    args = ap.parse_args()

    files = corpus_files()
    if args.text:
        files = [f for f in files if f.name.startswith(args.text + '.')]
        if not files:
            raise SystemExit(f'Keine TEI-Datei fuer Sigle {args.text}')

    results = []
    for f in files:
        r = analyse(f)
        if r:
            results.append(r)

    if args.text:
        r = results[0]
        print(f"{r['sigle']}")
        print(f"  <div> gesamt              {r['divs_total']}")
        print(f"  davon (a) erfuellt        {r['starts_at_one']}")
        print(f"  davon qualifizierend      {r['qualifying']}")
        print(f"  an (b) gescheitert        {r['rejected_by_b']}")
        for t, c in sorted(r['types'].items(), key=lambda x: -x[1]):
            print(f"      {t:<16} {c}")
        print(f"  Randnummern ohne Reset    {r['numbers_without']}")
        print(f"  Randnummern mit Reset     {r['numbers_with']}")
        print(f"  zusaetzlich               {r['extra']:+d}")
        print(f"  zusaetzlich nur mit (a)   {r['extra_only_a']:+d}   "
              f"(Bedingung (b) verhindert {r['extra_only_a'] - r['extra']})")
        return

    qualifying_total = sum(r['qualifying'] for r in results)
    rejected_by_b_total = sum(r['rejected_by_b'] for r in results)
    starts_total = sum(r['starts_at_one'] for r in results)
    divs_total = sum(r['divs_total'] for r in results)
    texts_with_qualifying = sum(1 for r in results if r['qualifying'] > 0)
    texts_rejected_by_b = sum(1 for r in results if r['rejected_by_b'] > 0)
    extra_total = sum(r['extra'] for r in results)
    texts_with_extra = sum(1 for r in results if r['extra'] > 0)

    types = Counter()
    for r in results:
        types.update(r['types'])

    print(f'Korpus: {len(results)} Texte mit <body>, {divs_total} <div> gesamt')
    print()
    print(f'Bedingung (a) erfuellt           {starts_total}')
    print(f'  davon qualifizierend (a und b) {qualifying_total} in {texts_with_qualifying} Texten')
    for t, c in sorted(types.items(), key=lambda x: -x[1]):
        print(f'      {t:<18} {c}')
    print(f'  an (b) gescheitert             {rejected_by_b_total} in {texts_rejected_by_b} Texten')
    print('      (strophenlokale Zaehlung, wuerde ohne (b) nackte Randeinsen erzeugen)')
    print()
    print(f'Zusaetzliche Randnummern         {extra_total} in {texts_with_extra} Texten')
    only_a_total = sum(r['extra_only_a'] for r in results)
    print(f'  ohne Bedingung (b) waeren es   {only_a_total}, '
          f'(b) verhindert also {only_a_total - extra_total} unmotivierte Randeinsen')
    print()
    print(f'Groesste Faelle (Top {args.top}):')
    for r in sorted(results, key=lambda x: -x['extra'])[:args.top]:
        if r['extra'] == 0:
            break
        print(f"    {r['sigle']:<8} {r['extra']:+6d}   ({r['qualifying']} qualifizierende <div>, "
              f"{r['numbers_without']} -> {r['numbers_with']} Randnummern)")


if __name__ == '__main__':
    main()
