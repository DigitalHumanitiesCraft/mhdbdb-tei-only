#!/usr/bin/env python3
"""Setzt die drei von @wachauer entschiedenen Annotationspakete der Welle A1 um.

  #387  21 Resttokens der vrouwe/vro-Serie (Entscheidungen KZW 17.09.2026, K4)
  #418  12 offene hawe-Tokens (Zuordnung KZW 11.09.2026, K6; neue Bedeutung K9)
  #464  2 Tokens von lemma_28290 zalder (KZW 22.09.2026, K1)

Zusammen 35 Tokens in 19 Korpusdateien plus ein neuer Sense in lexicon.xml,
ein gemeinsamer Rebuild der abgeleiteten Schicht, ein Versions-Bump. Dazu
kommt ein 36. Token, AC3_23010_1: es ist seit #416 annotiert und bekommt
hier nur ein neues @corresp, siehe TYPEN.

TYPEN
-----
Ein `type_N` ist EINE Schreibform EINES Lemmas. Regel aus #367: neue Nummer
praegen, nie eine bestehende umhaengen. Hoechste vergebene Nummer am
23.09.2026: type_372386 (gemessen an variants.xml). Fuenf Nummern werden
gepraegt, 372387 bis 372391:

  vrow̆e  unter lemma_7260  von KZW in #387 K4 ausdruecklich freigegeben
  vroewe unter lemma_7256  folgt aus KZWs Lemmaentscheidung fuer FLG_1102110_14;
                           die Schreibung gibt es bisher nur unter lemma_7260
  fröwen unter lemma_7250  folgt aus KZWs Entscheidung fuer MR1_10272154200_0;
                           bisher nur unter lemma_7256 und lemma_7260
  hawe   unter lemma_2923  die sieben Verbbelege aus #418
  hawe   unter lemma_9644  die sechs Substantivbelege aus #418, AC3_23010_1
                           eingeschlossen

type_117159 (hawe unter lemma_2598 haben) verliert damit alle 13 Tokens und
faellt beim naechsten extract-variants.py --apply aus variants.xml heraus.
Die Alternative, ihn fuer lemma_9644 weiterzufuehren, waere genau das
Umhaengen, das die Regel verbietet: die Nummer wechselte von haben zu houwe.

SENSE
-----
lemma_9644 houwe bekommt einen zweiten Sense, lemma_9644_sense_119194, mit
den drei Konzepten aus lemma_2923_sense_4697 (KZW #418 K9, gegen die Quelle
gehalten in K10). Hoechste Sense-Nummer am 23.09.2026: 119193. Kein @ana am
neuen Sense: die Typlisten dort sind Migrationsbestand, 18.840 Senses fuehren
keine.

@ana AN TOKENS
--------------
Nur bei #418, wo KZW den Sense benannt hat. #387 und #464 setzen kein @ana,
dieselbe Begruendung wie in apply-366-375-371.py (Sense-Zuordnung ist
kuratorisch).

@reason
-------
Im Korpus bisher ausschliesslich Verschmelzungsnotation (wilt+du, färbe+ez).
#464 folgt dem (zalte+er). Die zwei ADJ NOM aus #387 tragen den erklaerenden
Kommentar, den KZW verlangt, und sind damit die ersten Prosawerte.
Die Reihenfolge ist KZWs ADJ NOM und bewusst NICHT die Bestandsreihenfolge
NOM ADJ: gemessen am 23.09.2026 traegt keiner der 119.501 NOM ADJ ein
@reason, die Reihenfolge ist dort durchgehend das unaufgeloeste Kompositum der
Migration, das die K4-Kampagne aufloesen soll. Bei den Verschmelzungen trennt
die Reihenfolge Absicht von Altlast genauso (VRB PRO 154 von 154 mit @reason,
PRO VRB 0 von 9.068). Laufplan 23.09.2026, Grenzverhandlung zur Zeile
„Tag-Reihenfolge #387“.

SCHREIBWEISE
------------
Textuell auf den Dateien, nicht ueber einen Parse-Baum (Begruendung wie in
apply-366-375-371.py). Gefunden wird mit lxml, geschrieben mit re.subn. Nur
das oeffnende <w>-Tag aendert sich; Tokentext, Reihenfolge und xml:id bleiben
byte-identisch. Zeilenenden der Datei bleiben erhalten (WZB ist CRLF).

Der Ist-Zustand jedes Tokens wird vorher verifiziert und das Skript bricht ab,
wenn er abweicht. Es ist deshalb nicht idempotent.

Usage:
    python scripts/ingest/pos-disambig/apply-387-418-464.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-387-418-464.py --apply
"""

import io
import re
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
TEI_NS = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
APPLY = '--apply' in sys.argv

NEU_AB, NEU_BIS = 372387, 372391
TYPEN = {
    ('vrow̆e',  'lemma_7260'): 'type_372387',
    ('vroewe', 'lemma_7256'): 'type_372388',
    ('fröwen', 'lemma_7250'): 'type_372389',
    ('hawe',   'lemma_2923'): 'type_372390',
    ('hawe',   'lemma_9644'): 'type_372391',
    # bestehend
    ('fro',    'lemma_7250'): 'type_41787',
    ('frô',    'lemma_7250'): 'type_25866',
    ('fröwen', 'lemma_7256'): 'type_289796',
    ('fröwen', 'lemma_7260'): 'type_289794',
}

NEUER_SENSE = 'lemma_9644_sense_119194'
SENSE_ALT = 'lemma_9644_sense_15624'
SENSE_KONZEPTE = ['concept_21072000', 'concept_23231000', 'concept_23304100']

REASON_387 = 'adjektivische und nominale Lesart nicht entscheidbar (KZW 17.09.2026, #387)'

# (xml:id, Form, Ist: lemmaRef, pos, ana, corresp, reason) -> (Soll: lemmaRef, pos, ana, corresp, reason)
# None heisst: Attribut fehlt.
LEER = (None, None, None, None, None)


def a387(wid, form, lemma, pos, reason=None, ist=LEER):
    return {'paket': '387', 'xml_id': wid, 'form': form, 'ist': ist,
            'soll': (lemma, pos, None, TYPEN[(form, lemma)], reason)}


AUFTRAEGE = [
    # #387, KZW K4 vom 17.09.2026, Tabelle „Die 13 vorgelegten Belege"
    a387('FR1_5092110_2',       'fro', 'lemma_7250', 'ADJ NOM', REASON_387),
    a387('FR3_105218020300_2',  'fro', 'lemma_7250', 'ADJ NOM', REASON_387),
    a387('FR2_419020_7',        'fro', 'lemma_7250', 'NOM'),
    a387('FR1_13058020_4',      'fro', 'lemma_7250', 'NOM'),
    a387('RVBR_6083_0',         'frô', 'lemma_7250', 'ADV'),
    a387('FR3_111209101540_6',  'fro', 'lemma_7250', 'ADV'),
    a387('FR3_211209020180_6',  'fro', 'lemma_7250', 'ADV'),
    a387('GWTK_272211589800_5', 'fro', 'lemma_7250', 'ADJ'),
    a387('NEIM_2503080_8',      'fro', 'lemma_7250', 'ADV'),
    a387('RVBR_5752_5',         'frô', 'lemma_7250', 'ADV'),
    a387('RVBR_15969_1',        'frô', 'lemma_7250', 'ADV'),
    a387('RVBR_26626_4',        'frô', 'lemma_7250', 'ADV'),
    a387('SVP_1990_1',          'fro', 'lemma_7250', 'ADV'),
    # #387, KZW K4, Tabelle „Die acht weiteren Restfälle"
    a387('FLG_1102110_14',      'vroewe', 'lemma_7256', 'VRB', ist=(None, 'VRB', None, None, None)),
    a387('GWTK_172211007700_0', 'fröwen', 'lemma_7256', 'VRB'),
    a387('GWTK_286111667400_2', 'fröwen', 'lemma_7256', 'VRB'),
    a387('MR1_10272154200_0',   'fröwen', 'lemma_7250', 'ADJ'),
    a387('MR1_10311172300_6',   'fröwen', 'lemma_7260', 'NOM'),
    a387('MR1_20342005600_2',   'fröwen', 'lemma_7256', 'VRB'),
    a387('MR1_30561036800_2',   'fröwen', 'lemma_7256', 'VRB'),
    a387('WZB_64ra_25_4',       'vrow̆e', 'lemma_7260', 'NOM'),
]

# #418, KZW K6 vom 11.09.2026 (Zuordnung), K8 (AC2_9100_9 ist das Verb), K9/K10 (neuer Sense)
HABEN_VRB = ('lemma_2598', 'VRB', None, 'type_117159', None)
HABEN_VRBVEX = ('lemma_2598', 'VRB VEX', None, 'type_117159', None)
VERB = ('lemma_2923', 'VRB', None, 'type_372390', None)
SUBST_ALT = ('lemma_9644', 'NOM', SENSE_ALT, 'type_372391', None)
SUBST_NEU = ('lemma_9644', 'NOM', NEUER_SENSE, 'type_372391', None)
for wid, ist, soll in [
    ('AC2_9100_9',           HABEN_VRB,    VERB),
    ('CEFB_172000471600_10', HABEN_VRBVEX, VERB),
    ('CEFB_341000801500_7',  HABEN_VRBVEX, VERB),
    ('DES2_291281010_8',     HABEN_VRBVEX, VERB),
    ('GAR_40930_3',          HABEN_VRBVEX, VERB),
    ('KFB_11812_4',          HABEN_VRBVEX, VERB),
    ('KFB_12820_9',          HABEN_VRBVEX, VERB),
    ('AC2_25010_2',          HABEN_VRB,    SUBST_ALT),
    ('AC3_17290_9',          HABEN_VRB,    SUBST_ALT),
    ('CEFB_71000210500_11',  HABEN_VRBVEX, SUBST_ALT),
    ('GAR_1530_5',           HABEN_VRBVEX, SUBST_NEU),
    ('MR2_12484100113100_4', HABEN_VRBVEX, SUBST_NEU),
    # seit #416 annotiert, nur der Typ wechselt (siehe TYPEN im Docstring)
    ('AC3_23010_1', ('lemma_9644', 'NOM', SENSE_ALT, 'type_117159', None), SUBST_ALT),
]:
    AUFTRAEGE.append({'paket': '418', 'xml_id': wid, 'form': 'hawe', 'ist': ist, 'soll': soll})

# #464, KZW K1 vom 22.09.2026
AUFTRAEGE += [
    {'paket': '464', 'xml_id': 'ENE_10090_1', 'form': 'zalder',
     'ist': ('lemma_28290', 'PRO VRB', None, 'type_140326', None),
     'soll': ('lemma_28290', 'VRB PRO', None, 'type_140326', 'zalte+er')},
    {'paket': '464', 'xml_id': 'ROT_28700_1', 'form': 'celder',
     'ist': ('lemma_28290', 'PRO VRB', None, 'type_144228', None),
     'soll': ('lemma_28290', 'VRB PRO', None, 'type_144228', 'zalte+er')},
]

REVISION = {
    '387': ('#387 vrouwe/vrô, Resttokens: {n} {t} annotiert nach den Einzelentscheidungen '
            'von KZW vom 17.09.2026 (lemmaRef/pos/corresp; kein @ana, weil die Sense-Zuordnung '
            'kuratorisch ist). Im ganzen Lauf: zwei Doppeltags ADJ NOM mit erklärendem '
            '@reason, wo KZW die Lesart für unentscheidbar erklärt hat, und drei neu geprägte '
            'Variantentypen nach der Regel aus #367.'),
    '418': ('#418 hawe: {n} {t} nach der Zuordnung von KZW vom 11.09.2026 auf lemma_2923 '
            'houwen bzw. lemma_9644 houwe gesetzt (lemmaRef/pos/corresp, @ana beim Substantiv). '
            'Im ganzen Lauf: zwei Belege auf den neuen Sense lemma_9644_sense_119194 „Schlag“; '
            'hawe erhält unter beiden Lemmata einen neu geprägten Variantentyp, type_117159 '
            'von lemma_2598 haben entfällt damit.'),
    '464': ('#464 zalder: {n} {t} von @pos PRO VRB auf VRB PRO, Verschmelzung aus einer '
            'Präteritalform von zeln und er als @reason dokumentiert, keine Token-Trennung '
            '(KZW 22.09.2026).'),
}
DATUM = '2026-09-23'

ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)


def frag(wert):
    if not wert:
        return None
    return wert.split()[0].split('#', 1)[-1]


def sigle(wid):
    return wid.split('_', 1)[0]


def scanne(ids):
    je = defaultdict(set)
    for wid in ids:
        je[sigle(wid)].add(wid)
    ist = {}
    for s, wids in je.items():
        pfad = ROOT / 'tei' / f'{s}.tei.xml'
        for w in etree.parse(str(pfad)).iter(f'{TEI_NS}w'):
            wid = w.get(XMLID)
            if wid in wids:
                ist[wid] = {
                    'form': ''.join(w.itertext()).strip(),
                    'wert': (frag(w.get('lemmaRef')), w.get('pos'), frag(w.get('ana')),
                             frag(w.get('corresp')), w.get('reason')),
                }
    return ist


def neues_tag(wid, soll):
    lemma, pos, ana, corresp, reason = soll
    teile = [f'<w xml:id="{wid}"', f'lemmaRef="lexicon.xml#{lemma}"', f'pos="{pos}"']
    if ana:
        teile.append(f'ana="lexicon.xml#{ana}"')
    teile.append(f'corresp="variants.xml#{corresp}"')
    if reason:
        teile.append(f'reason="{reason}"')
    return ' '.join(teile) + '>'


def lexikon(text):
    """Fuegt den neuen Sense hinter lemma_9644_sense_15624 ein."""
    if f'xml:id="{NEUER_SENSE}"' in text:
        sys.exit(f'ABBRUCH: {NEUER_SENSE} steht schon in lexicon.xml')
    if re.search(r'_sense_119194"', text):
        sys.exit('ABBRUCH: die Sense-Nummer 119194 ist schon vergeben')
    hoechste = max(int(m) for m in re.findall(r'_sense_(\d+)"', text))
    if hoechste != 119193:
        sys.exit(f'ABBRUCH: hoechste Sense-Nummer {hoechste}, erwartet 119193')
    muster = re.compile(
        r'(\n(\s*)<sense xml:id="' + SENSE_ALT + r'"[^>]*>\n(?:\s*<ptr [^>]*/>\n)+\s*</sense>)')
    treffer = muster.findall(text)
    if len(treffer) != 1:
        sys.exit(f'ABBRUCH: {SENSE_ALT} {len(treffer)}x gefunden, erwartet 1x')
    einzug = treffer[0][1]
    block = (f'\n{einzug}<sense xml:id="{NEUER_SENSE}">\n'
             + ''.join(f'{einzug}  <ptr target="concepts.xml#{k}"/>\n' for k in SENSE_KONZEPTE)
             + f'{einzug}</sense>')
    text, n = muster.subn(lambda m: m.group(1) + block, text)
    if n != 1:
        sys.exit(f'ABBRUCH: Sense {n}x eingefuegt, erwartet 1x')
    return text


def main():
    ids = [a['xml_id'] for a in AUFTRAEGE]
    if len(set(ids)) != len(ids):
        sys.exit('ABBRUCH: xml:id doppelt beauftragt')
    zahl = defaultdict(int)
    for a in AUFTRAEGE:
        zahl[a['paket']] += 1
    print(f'Auftraege: {len(AUFTRAEGE)} Tokens (#387 {zahl["387"]}, #418 {zahl["418"]}, '
          f'#464 {zahl["464"]})')
    if (zahl['387'], zahl['418'], zahl['464']) != (21, 13, 2):
        sys.exit('ABBRUCH: erwartet 21 + 13 + 2 Auftraege')

    # Die neuen Nummern duerfen im Bestand noch nicht vorkommen.
    varianten = (ROOT / 'authority-files' / 'variants.xml').read_text(encoding='utf-8')
    hoechster = max(int(m) for m in re.findall(r'xml:id="type_(\d+)"', varianten))
    if hoechster != NEU_AB - 1:
        sys.exit(f'ABBRUCH: hoechste Typnummer {hoechster}, erwartet {NEU_AB - 1}')

    ist = scanne(ids)
    fehler = []
    for a in AUFTRAEGE:
        d = ist.get(a['xml_id'])
        if d is None:
            fehler.append(f'{a["xml_id"]}: nicht gefunden')
            continue
        if d['form'] != a['form']:
            fehler.append(f'{a["xml_id"]}: Form {d["form"]!r}, erwartet {a["form"]!r}')
        if d['wert'] != a['ist']:
            fehler.append(f'{a["xml_id"]}: ist {d["wert"]}, erwartet {a["ist"]}')
    if fehler:
        print('ABBRUCH, der Ist-Zustand weicht ab. Nichts wurde geschrieben:')
        for f in fehler:
            print('   ' + f)
        return 1
    print(f'Ist-Zustand aller {len(AUFTRAEGE)} Tokens wie erwartet.')

    print('\nTypen (Soll):')
    for (form, lemma), tid in sorted(TYPEN.items(), key=lambda x: int(x[1].split('_')[1])):
        n = sum(1 for a in AUFTRAEGE if a['soll'][3] == tid)
        neu = 'neu' if NEU_AB <= int(tid.split('_')[1]) <= NEU_BIS else '   '
        print(f'   {neu} {tid:12} {form:7} unter {lemma:11} {n:3} Tokens')

    je_datei = defaultdict(list)
    for a in AUFTRAEGE:
        je_datei[sigle(a['xml_id'])].append(a)

    print(f'\nBetroffene Korpusdateien: {len(je_datei)}')
    geschrieben = 0
    for s, rows in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{s}.tei.xml'
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        for a in rows:
            wid = a['xml_id']
            muster = re.compile(r'<w xml:id="' + re.escape(wid) + r'"[^>]*>([^<]*)</w>')
            treffer = muster.findall(text)
            if len(treffer) != 1 or treffer[0].strip() != a['form']:
                sys.exit(f'ABBRUCH: {wid} textuell {len(treffer)}x, Form {treffer!r}')
            tag = neues_tag(wid, a['soll'])
            text, n = muster.subn(lambda m, t=tag: t + m.group(1) + '</w>', text)
            if n != 1:
                sys.exit(f'ABBRUCH: {wid} {n}x ersetzt')
            geschrieben += 1
        for paket in ('387', '418', '464'):
            n = sum(1 for a in rows if a['paket'] == paket)
            if not n:
                continue
            m = ANKER.search(text)
            if not m:
                sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {s}')
            nl = '\r\n' if '\r\n' in m.group(3) else '\n'
            eintrag = (f'<change when="{DATUM}" who="#editor">'
                       + REVISION[paket].format(n=n, t='Token' if n == 1 else 'Tokens')
                       + '</change>')
            text = text[:m.end(2)] + nl + m.group(1) + eintrag + text[m.end(2):]
        if APPLY:
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
        pakete = ','.join(sorted({a['paket'] for a in rows}))
        print(f'   {s + ".tei.xml":20} {len(rows):3} Tokens  (#{pakete})'
              + ('' if APPLY else '  [Trockenlauf]'))

    lexpfad = ROOT / 'authority-files' / 'lexicon.xml'
    with open(lexpfad, encoding='utf-8', newline='') as fh:
        lex = lexikon(fh.read())
    if APPLY:
        with open(lexpfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(lex)
    print(f'\nlexicon.xml: {NEUER_SENSE} mit {len(SENSE_KONZEPTE)} Konzepten'
          + ('' if APPLY else '  [Trockenlauf]'))

    print(f'\nTokens geschrieben: {geschrieben}')
    if not APPLY:
        print('Trockenlauf, nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
