#!/usr/bin/env python3
"""Seltenes Gate (#414): gemessene Verszaehlungs- und div-Zahlen gegen ihre
Fundstellen halten, auch in .js-Kommentaren.

Warum ein eigenes Gate neben doc-count-audit.py: die beiden Zaehlskripte
(count-verse-numbering-resets.py, count-editorial-notes-and-div-heads.py)
bauen die Renderreihenfolge bzw. parsen alle Korpusdateien; der ganze Lauf
braucht rund vier Minuten (263 s, ein Lauf am 10.10.2026), doc-count-audit.py
rund fuenf Sekunden. In jeden Audit-Lauf passen sie nicht. Das Gate laeuft deshalb woechentlich und bei
Aenderungen unter tei/ (.github/workflows/measured-counts.yml).

Was es prueft: jede Fundstelle in CLAIMS steht als woertlicher Satz mit
Platzhaltern fuer die gemessenen Zahlen. Das Gate misst, setzt ein, normalisiert
den Text der Datei (Kommentarzeichen und Zeilenumbrueche weg) und verlangt den
Satz darin, mit Zahlengrenze (500 trifft nicht in 1.500). Fehlt er, steht die
Zahl falsch oder der Satz wurde umformuliert: passt der Satz mit beliebigen
Zahlen, meldet das Gate "Zahl weicht ab" mit der gefundenen Stelle, sonst
"Anker nicht gefunden".

Was es NICHT prueft: Zahlen ausserhalb der Liste CLAIMS. Eine neue Fundstelle
gehoert hier eingetragen, sonst ist sie ungegatet (#414). Die Lemma-Gesamtzahlen
in JS-Kommentaren gehoeren nicht hierher, sie sind durch Groessenordnungen
ersetzt (#451).

Usage:
    python scripts/audit/check-measured-counts.py            # messen und pruefen
    python scripts/audit/check-measured-counts.py --measured  # nur die Messwerte
"""
import argparse
import importlib.util
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AUDIT = Path(__file__).resolve().parent

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout.reconfigure(encoding='utf-8')


def load_module(filename):
    """Ein Zaehlskript aus scripts/audit/ importieren (Bindestriche im Namen)."""
    spec = importlib.util.spec_from_file_location(
        filename.replace('-', '_').removesuffix('.py'), AUDIT / filename)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(AUDIT.parent))
    spec.loader.exec_module(mod)
    return mod


def measure():
    """Alle Messwerte, flach, unter den Namen der Platzhalter."""
    os.chdir(REPO)
    verse_mod = load_module('count-verse-numbering-resets.py')
    heads_mod = load_module('count-editorial-notes-and-div-heads.py')
    v = verse_mod.measure()
    h = heads_mod.measure_div_heads(heads_mod.corpus_file_list())

    m = {
        'divs_total': v['divs_total'],
        'starts_total': v['starts_total'],
        'qualifying_total': v['qualifying_total'],
        'texts_with_qualifying': v['texts_with_qualifying'],
        'rejected_by_b_total': v['rejected_by_b_total'],
        'texts_rejected_by_b': v['texts_rejected_by_b'],
        'extra_total': v['extra_total'],
        'texts_with_extra': v['texts_with_extra'],
        # was Bedingung (b) an unmotivierten Randeinsen verhindert
        'unmotiviert': v['extra_only_a_total'] - v['extra_total'],
        'with_head': h['with_head'],
        'labelled_total': h['labelled_total'],
        'texts_with_head': h['texts_with_head'],
        'has_n': h['has_n'],
        'carries': h['carries'],
        'first_child_true': h['first_child_true'],
        'first_child_false': h['first_child_false'],
    }
    # Typaufschluesselung der qualifizierenden divs der Verszaehlung
    for key, label in (('v_chapter', 'chapter'), ('v_song', 'song'),
                       ('v_none', '(ohne @type)'), ('v_section', 'section'),
                       ('v_parallel', 'parallel'), ('v_number', 'number')):
        m[key] = v['types'].get(label, 0)
    # Groesste Faelle der zusaetzlichen Randnummern
    for sigle in ('PZ', 'WH', 'FR3', 'CHH', 'TKR', 'HUG'):
        m['x_' + sigle] = v['extra_by_text'].get(sigle, 0)
    # typisierte divs mit eigenem <head>, je Typ, und alle typisierten je Typ
    for t in ('song', 'chapter', 'recipe', 'number', 'section'):
        m['h_' + t] = sum(h['per_type'].get(t, {}).values())
    for t in ('song', 'chapter', 'recipe', 'section', 'number', 'parallel', 'colophon'):
        m['t_' + t] = h['total_labelled'].get(t, 0)
    # typisierte divs ausserhalb dieser sieben Typen (Voraussetzung von "no further types")
    m['t_other'] = h['labelled_total'] - sum(
        m['t_' + t] for t in ('song', 'chapter', 'recipe', 'section', 'number',
                              'parallel', 'colophon'))
    # Spitzentexte der Kopfzaehlung
    tops = dict(h['top_texts'])
    for sigle in ('NEI', 'NEIC', 'WZB', 'KBL4', 'SUB1'):
        m['top_' + sigle] = tops.get(sigle, 0)
    return m


def fmt(value, style):
    """Tausendertrennung: de = 1.959, en = 1,959, sonst unveraendert."""
    s = f'{value:,}'
    if style == 'de':
        return s.replace(',', '.')
    if style == 'en':
        return s
    return str(value)


FIELD = re.compile(r'\{(\w+)(?::(\w+))?\}')


def render(template, m):
    return FIELD.sub(lambda g: fmt(m[g.group(1)], g.group(2)), template)


def normalize(text, is_js):
    """Kommentarzeichen am Zeilenanfang weg, Whitespace auf ein Leerzeichen."""
    if is_js:
        text = re.sub(r'^[ \t]*(?://|/\*+|\*+/?|\*)[ \t]?', '', text, flags=re.M)
    return ' '.join(text.split())


TR = 'assets/js/rendering/tei-text-reader.js'
FE = 'docs/FEATURES.md'
TM = 'docs/TEI-MODEL.md'
CSS = 'assets/css/korpus.css'

# (Datei, Name, Satz mit Platzhaltern). Satzbau und Zeichensetzung muessen mit
# der Fundstelle uebereinstimmen; Zahlen kommen aus measure().
CLAIMS = [
    # --- assets/js/rendering/tei-text-reader.js, Kommentare ---
    (TR, 'divRestartsNumbering: Reichweite von (b)',
     'Korpusweit hält (b) {qualifying_total:de} divs und verwirft '
     '{rejected_by_b_total:de} strophenlokale in {texts_rejected_by_b} Texten, '
     'was {unmotiviert:de} unmotivierte Randeinsen verhindert'),
    (TR, 'divRestartsNumbering: divs ohne @type',
     '{v_none} der qualifizierenden divs haben gar kein @type'),
    (TR, 'isInNestedParallel: heutiger Stand',
     'heute liefert dasselbe Skript {qualifying_total:de} qualifizierende divs '
     'und {extra_total:de} zusätzliche Randnummern in {texts_with_extra} Texten'),
    (TR, 'isInNestedParallel: Herleitung',
     '1.492 + 467 = {qualifying_total:de}, 1.352 + 466 = {extra_total:de}, '
     '49 + 1 = {texts_with_extra}'),
    (TR, 'isInNestedParallel: Fall FR3 und section',
     'FR3 steht unverändert bei +{x_FR3}, die section-Zahl {v_section} gilt'),
    (TR, 'isInNestedParallel: Nenner der div-Zahl',
     'Der Nenner „{labelled_total:de} typisierte divs'),
    (TR, 'hasOwnHeading: Zähler, Nenner, Texte',
     'Korpusweit betrifft das {with_head:de} der {labelled_total:de} '
     'typisierten divs in {texts_with_head} Texten'),
    (TR, 'hasOwnHeading: Herleitung des Nenners',
     '(4.676 + 467 = {labelled_total:de})'),
    (TR, 'hasOwnHeading: Nummer im head',
     'in keinem dieser {with_head:de} Fälle enthält der <head> die Nummer aus @n'),
    (TR, 'hasOwnHeading: davon mit @n',
     'und {has_n} davon haben ein @n'),
    (TR, 'Zählungs-Anker: Reichweite und Typen',
     'Reichweite: {qualifying_total:de} divs in {texts_with_qualifying} Texten '
     'erfüllen das Kriterium ({v_chapter:de} chapter, {v_song} song, '
     '{v_none} ohne @type, {v_section} section, {v_parallel} parallel, '
     '{v_number} number); sichtbar werden dadurch {extra_total:de} zusätzliche '
     'Randnummern in {texts_with_extra} Texten.'),
    (TR, 'Zählungs-Anker: größte Fälle',
     'Größter Fall ist PZ mit +{x_PZ}, dann WH +{x_WH}, FR3 +{x_FR3}, '
     'CHH +{x_CHH}, TKR +{x_TKR}, HUG +{x_HUG}'),

    # --- docs/FEATURES.md ---
    (FE, 'Verse numbering: Grundgesamtheit',
     'Of {divs_total:en} `<div>`s in the corpus {starts_total:en} meet the first '
     'condition, of which **{qualifying_total:en} in {texts_with_qualifying} texts** '
     'qualify ({v_chapter:en} `chapter`, {v_song} `song`, {v_none} without `@type`, '
     '{v_section} `section`, {v_parallel} `parallel`, {v_number} `number`).'),
    (FE, 'Verse numbering: zusätzliche Randnummern',
     'This makes **{extra_total:en} additional margin numbers in '
     '{texts_with_extra} texts** visible.'),
    (FE, 'Verse numbering: größte Fälle',
     'The largest case is PZ (Parzival) with +{x_PZ}, followed by WH (+{x_WH}, '
     'which entered this statistic only with the Willehalm rebuild in #358), '
     'FR3 (+{x_FR3}), CHH (+{x_CHH}), TKR (+{x_TKR}) and HUG (+{x_HUG}, '
     'Julia\'s original case).'),
    (FE, 'Verse numbering: Wirkung von (b)',
     'It discards {rejected_by_b_total:en} `<div>`s in {texts_rejected_by_b} texts '
     'corpus-wide and thereby prevents {unmotiviert:en} unmotivated margin ones.'),
    (FE, 'Section label: Zähler, Nenner, Texte, Typen',
     'This affects {with_head:en} of the {labelled_total:en} typed `<div>`s in '
     '{texts_with_head} texts ({h_song} `song`, {h_chapter} `chapter`, '
     '{h_recipe} `recipe`, {h_number} `number`, {h_section} `section`)'),
    (FE, 'Section label: führende Texte',
     'led by NEI and NEIC ({top_NEI} each), WZB ({top_WZB}) and KBL4/SUB1 '
     '({top_KBL4} each)'),
    (FE, 'Section label: Divs mit @n',
     'and {has_n} of the divs have an `@n`'),

    # --- docs/TEI-MODEL.md, Typentabelle und Summe ---
    # --- assets/css/korpus.css, Kommentar am Nachbarselektor ---
    (CSS, 'Nachbarselektor: erstes Kind',
     'Das trifft auf {first_child_true:de} der {with_head:de} Fälle zu; bei den '
     'übrigen {first_child_false} steht ein anderes Element davor'),

    (TM, 'div/@type: song', '| **`song`** | {t_song:en} |'),
    (TM, 'div/@type: chapter', '| **`chapter`** | {t_chapter:en} |'),
    (TM, 'div/@type: recipe', '| **`recipe`** | {t_recipe:en} |'),
    (TM, 'div/@type: section', '| **`section`** | {t_section:en} |'),
    (TM, 'div/@type: number', '| **`number`** | {t_number:en} |'),
    (TM, 'div/@type: parallel', '| **`parallel`** | {t_parallel:en} |'),
    (TM, 'div/@type: colophon', '| **`colophon`** | {t_colophon:en} |'),
    (TM, 'div/@type: Summe',
     '(`div[@type]`, {labelled_total:en} in total, no further types)'),
]


NUM = r'[\d.,]+'


def exact_pattern(want):
    """Der erwartete Satz als Regex; eine Zahl am Rand darf nicht Teil einer
    laengeren sein (500 in 1.500, 15 in 159)."""
    pat = re.escape(want)
    if want[0].isdigit():
        pat = r'(?<![\d.,])' + pat
    if want[-1].isdigit():
        pat += r'(?!\d|[.,]\d)'
    return re.compile(pat)


def loose_pattern(template):
    """Derselbe Satz mit beliebiger Zahl an jedem Platzhalter (Diagnose)."""
    parts = FIELD.split(template)
    # split mit zwei Gruppen: [Text, Name, Stil, Text, Name, Stil, ..., Text]
    pat = ''.join(re.escape(parts[i]) if i % 3 == 0 else (NUM if i % 3 == 1 else '')
                  for i in range(len(parts)))
    return re.compile(pat)


def check(m):
    """Liste der Befunde (Datei, Name, Meldung); leer = gruen."""
    problems = []
    # Voraussetzungen von Saetzen, die eine Allaussage tragen
    if m['carries'] != 0:
        problems.append((TR, 'hasOwnHeading: Nummer im head',
                         f'der Kommentar sagt "in keinem dieser Faelle", gemessen '
                         f'sind {m["carries"]}'))
    if m['t_other'] != 0:
        problems.append((TM, 'div/@type: Summe',
                         f'die Tabelle sagt "no further types", gemessen sind '
                         f'{m["t_other"]} typisierte divs anderer Typen'))
    texts = {}
    for path, name, template in CLAIMS:
        if path not in texts:
            p = REPO / path
            if not p.exists():
                texts[path] = None
            else:
                texts[path] = normalize(p.read_text(encoding='utf-8'),
                                        path.endswith('.js'))
        text = texts[path]
        if text is None:
            problems.append((path, name, 'Datei fehlt'))
            continue
        want = render(template, m)
        if exact_pattern(want).search(text):
            continue
        hit = loose_pattern(template).search(text)
        if hit is None:
            problems.append((path, name,
                             f'Anker nicht gefunden (Satz umformuliert?): '
                             f'erwartet "{want}"'))
        else:
            problems.append((path, name,
                             f'Zahl weicht ab:\n        erwartet "{want}"\n'
                             f'        steht     "{hit.group(0)}"'))
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--measured', action='store_true',
                    help='nur die Messwerte als JSON ausgeben')
    ap.add_argument('--use-measured', metavar='JSON',
                    help='Messwerte aus einer frueheren --measured-Ausgabe lesen, '
                         'statt rund vier Minuten neu zu messen (Mutationsproben)')
    args = ap.parse_args()

    if args.use_measured:
        m = json.loads(Path(args.use_measured).read_text(encoding='utf-8'))
    else:
        m = measure()
    if args.measured:
        print(json.dumps(m, ensure_ascii=False, indent=2, sort_keys=True))
        return

    problems = check(m)
    files = sorted({p for p, _, _ in CLAIMS})
    print(f'{len(CLAIMS)} Fundstellen in {len(files)} Dateien gegen den Korpus gehalten '
          f'({", ".join(files)})')
    if not problems:
        print('Keine Drift.')
        return
    for path, name, msg in problems:
        print(f'  {path} / {name}: {msg}')
    print()
    print(f'{len(problems)} Fundstellen weichen ab. Die gemessene Zahl gilt; '
          f'Messvorschrift: python scripts/audit/check-measured-counts.py --measured')
    sys.exit(1)


if __name__ == '__main__':
    main()
