#!/usr/bin/env python3
"""
#228: modernen Apparat und neuhochdeutsche Inhaltsangaben entannotieren,
die dadurch belegfreien Lemmata loeschen, lob in KVO nachtragen.

Entscheidungen von KZW in #228 (Kommentar vom 11.09.2026, 13:42; Rueckfrage
niune beantwortet von chsteiner am 11.09.2026, 13:52):

  1. Die acht Dichternamen im Verfasser-Slot (BRH HAW HDM HHP HHW NIU OBP OVB)
     sind Ueberschriften der Edition von Kraus, kein ueberlieferter Text:
     entannotieren, kein NAM-Lemma fuer NIU.
  2. CL und KVO bleiben; in KVO wird lob nachgetragen.
  3. Die 422 GWTK-Inhaltsangaben sind neuhochdeutsche Herausgeberprosa:
     entannotieren.
  4. Lemmata, die dadurch jeden Korpusbeleg verlieren, werden geloescht.
  Scope: alle annotierten <note n> ohne <l> ausser NEIR, CL und KVO, dazu GWTK.

Drei Einschraenkungen aus dem Nachtlauf vom 23.09.2026:

  - NEIM wird nicht angefasst: seine 39 <note n> tragen die Konkordanz Lied zu
    Hs. C, die #453 sichern will. Deshalb bleibt auch lemma_53328 ("1"), das
    dort 63 Belege behaelt.
  - Ein belegfreies Lemma, auf das ein anderer Eintrag einer Authority-Datei
    verweist, wird nicht geloescht, sondern gemeldet. Getroffen hat das
    lemma_66692 Mur (etym von lemma_33528 und lemma_66691). Nach der
    Regeneration von variants.xml zeigte sein Sense per @ana auf den
    entfallenen type_348958; dieses @ana ist von Hand entfernt (Review
    Runde 1), das Skript selbst tut das nicht. Dieselbe Mechanik traf 82
    weitere Tokens in mehrwertigen @ana-Listen; die entfernt
    prune-ana-228.py (Review Runde 2).
  - Die 26 Ziffern in <supplied> (MR1, WVV) bleiben annotiert. KZW hat sie am
    28.07.2026 als Nicht-Lemmata bezeichnet, die Umsetzung aber am 11.09.2026
    nur unter "sofern" genannt; die Form (entannotieren, <num>, @n) ist offen
    und geht als Frage in #228. Deshalb bleiben auch die Ziffern-Lemmata, die
    nur dort belegt sind.

Entannotieren heisst: lemmaRef, pos, ana und corresp fallen weg, das <w> und
seine Umgebung (<hi>, <supplied>) bleiben.

Danach: scripts/sync/extract-variants.py --apply, beide Indexe, API, Bump.

Aufruf:
    python scripts/ingest/entannotate-228/apply-228.py            # Trockenlauf
    python scripts/ingest/entannotate-228/apply-228.py --apply    # schreiben
"""

import argparse
import io
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

REPO = Path(__file__).resolve().parents[3]
TEI_DIR = REPO / 'tei'
AUTH_DIR = REPO / 'authority-files'
DATUM = '2026-09-23'
T = '{http://www.tei-c.org/ns/1.0}'
XID = '{http://www.w3.org/XML/1998/namespace}id'

NICHT_S1 = {'NEIR', 'CL', 'KVO', 'NEIM'}
LOB = ('KVO_300001_2', 'lob', ' lemmaRef="lexicon.xml#lemma_3849" pos="NOM" '
       'ana="lexicon.xml#lemma_3849_sense_6077" corresp="variants.xml#type_13441"')

# Gemessen am 23.09.2026 auf 3a5ff3158. Weicht der Bestand ab, bricht das Skript ab.
ERWARTET = {'S1': (69, 132), 'S2': (422, 2058), 'waisen': None, 'gehalten': None}

ANKER = re.compile(r'([ \t]*)(<change when="[^"]*"[^>]*>(?:(?!</change>).)*</change>)(\s*)</revisionDesc>', re.S)
EINTRAG = {
    'S1': '#228: {n} Tokens im editorischen Apparat der Noten mit @n (Sigel, Strophenzähler, Rubriken und Überschriften der Edition) entannotiert: lemmaRef, pos, ana und corresp entfallen. Entscheidung KZW 11.09.2026: moderner Apparat ist kein mittelhochdeutscher Text.',
    'S2': '#228: {n} Tokens in den neuhochdeutschen Inhaltsangaben der Noten mit @n entannotiert: lemmaRef, pos, ana und corresp entfallen. Entscheidung KZW 11.09.2026: Herausgeberprosa gehört nicht ins mittelhochdeutsche Korpus.',
    'LOB': '#228: lob in der Liedüberschrift „der gense lob“ nachannotiert (lemma_3849 lop, NOM), wie von KZW am 11.09.2026 erbeten.',
}


def lemma(w):
    return w.get('lemmaRef').split('#')[1].split()[0]


def scope():
    """Liefert tokens {sigle: [(klasse, xml_id)]}, notes Counter, belege Counter, scope_belege Counter."""
    tokens = defaultdict(list); notes = Counter(); belege = Counter(); im_scope = Counter()
    for pfad in sorted(TEI_DIR.glob('*.tei.xml')):
        sigle = pfad.name[:-len('.tei.xml')]
        root = etree.parse(str(pfad)).getroot()
        gesehen = set()
        for w in root.iter(T + 'w'):
            if w.get('lemmaRef'):
                belege[lemma(w)] += 1
        for note in root.iter(T + 'note'):
            if note.get('type') is not None or note.get('place') is not None or note.get('n') is None:
                continue
            ws = [w for w in note.iter(T + 'w') if w.get('lemmaRef')]
            if not ws:
                continue
            if next(note.iter(T + 'l'), None) is not None:
                if sigle != 'GWTK':
                    sys.exit('FEHLER: <note n> mit <l> ausserhalb von GWTK: %s' % sigle)
                klasse = 'S2'
            elif sigle in NICHT_S1:
                continue
            else:
                klasse = 'S1'
            notes[klasse] += 1
            for w in ws:
                tokens[sigle].append((klasse, w.get(XID)))
                im_scope[lemma(w)] += 1
    return tokens, notes, belege, im_scope


def fremdverweise(ziel):
    """lemma_id -> Liste der Stellen ausserhalb des eigenen <entry>, variants.xml ausgenommen."""
    muster = re.compile(r'(lemma_\d+)(?:_sense_\d+)?\b')
    treffer = defaultdict(list)
    for pfad in sorted(AUTH_DIR.glob('*.xml')):
        if pfad.name == 'variants.xml':
            continue
        root = etree.parse(str(pfad)).getroot()
        for el in root.iter():
            if not isinstance(el.tag, str):
                continue
            entry = el if el.tag == T + 'entry' else next(el.iterancestors(T + 'entry'), None)
            eigen = entry.get(XID) if entry is not None else None
            for k, v in el.attrib.items():
                if k == XID:
                    continue
                for m in muster.finditer(v):
                    if m.group(1) in ziel and m.group(1) != eigen:
                        treffer[m.group(1)].append('%s:%d %s' % (pfad.name, el.sourceline, v))
    return treffer


def mit_change(text, eintrag, name):
    if '<' in eintrag or '&' in eintrag:
        sys.exit('FEHLER: %s: <change>-Text enthaelt Markup: %r' % (name, eintrag))
    m = ANKER.search(text)
    if m is None:
        sys.exit('FEHLER: %s: kein <change>-Anker vor </revisionDesc>' % name)
    nl = '\r\n' if '\r\n' in m.group(3) else '\n'
    zeile = '<change when="%s" who="#editor">%s</change>' % (DATUM, eintrag)
    return text[:m.end(2)] + nl + m.group(1) + zeile + text[m.end(2):]


def entannotiere(text, xml_id, name):
    muster = re.compile(r'<w xml:id="%s"( [^>]*)>' % re.escape(xml_id))
    treffer = muster.findall(text)
    if len(treffer) != 1:
        sys.exit('FEHLER: %s: <w xml:id="%s"> steht %d-mal' % (name, xml_id, len(treffer)))
    attrs = sorted(re.findall(r'(\w+)="', treffer[0]))
    if attrs not in (['ana', 'corresp', 'lemmaRef', 'pos'], ['corresp', 'lemmaRef', 'pos']):
        sys.exit('FEHLER: %s: %s traegt unerwartete Attribute %s' % (name, xml_id, attrs))
    return muster.sub('<w xml:id="%s">' % xml_id, text)


def loesche_eintraege(text, ids):
    """Entfernt je <entry xml:id="..."> bis zum zugehoerigen </entry> samt Zeilenende."""
    for i in ids:
        m = re.search(r'[ \t]*<entry xml:id="%s">.*?</entry>[ \t]*\r?\n' % re.escape(i), text, re.S)
        if m is None:
            sys.exit('FEHLER: lexicon.xml: <entry xml:id="%s"> nicht gefunden' % i)
        if m.group(0).count('<entry ') != 1:
            sys.exit('FEHLER: lexicon.xml: %s ueberlappt einen anderen Eintrag' % i)
        text = text[:m.start()] + text[m.end():]
    return text


def main():
    p = argparse.ArgumentParser(description='#228 entannotieren und Geisterlemmata loeschen')
    p.add_argument('--apply', action='store_true', help='schreiben statt nur pruefen')
    args = p.parse_args()

    tokens, notes, belege, im_scope = scope()
    je_klasse = Counter(k for ts in tokens.values() for k, _ in ts)
    for k in ('S1', 'S2'):
        ist = (notes[k], je_klasse[k])
        print('%s: %d Notes, %d Tokens' % (k, *ist))
        if ist != ERWARTET[k]:
            sys.exit('FEHLER: %s erwartet %s' % (k, ERWARTET[k]))
    waisen = sorted(l for l in im_scope if im_scope[l] == belege[l])
    verweise = fremdverweise(set(waisen))
    gehalten = sorted(verweise)
    loeschen = [l for l in waisen if l not in verweise]
    print('Lemmata im Scope: %d, belegfrei danach: %d, davon mit Fremdverweis gehalten: %d, geloescht: %d'
          % (len(im_scope), len(waisen), len(gehalten), len(loeschen)))
    for l in gehalten:
        print('  gehalten %s: %s' % (l, '; '.join(verweise[l])))
    if ERWARTET['waisen'] is None:
        print('  belegfrei:', ' '.join(waisen))
    elif len(waisen) != ERWARTET['waisen'] or len(gehalten) != ERWARTET['gehalten']:
        sys.exit('FEHLER: erwartet %d belegfrei, %d gehalten' % (ERWARTET['waisen'], ERWARTET['gehalten']))

    neu = {}
    for sigle, ts in sorted(tokens.items()):
        pfad = TEI_DIR / (sigle + '.tei.xml')
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        for _, xml_id in ts:
            text = entannotiere(text, xml_id, sigle)
        for k, n in sorted(Counter(k for k, _ in ts).items()):
            text = mit_change(text, EINTRAG[k].format(n='{:,}'.format(n).replace(',', '.')), sigle)
        neu[pfad] = text
        print('  %-5s %s' % (sigle, dict(Counter(k for k, _ in ts))))

    pfad = TEI_DIR / 'KVO.tei.xml'
    with open(pfad, encoding='utf-8', newline='') as fh:
        text = fh.read()
    xml_id, form, attrs = LOB
    alt = '<w xml:id="%s">%s</w>' % (xml_id, form)
    if text.count(alt) != 1:
        sys.exit('FEHLER: KVO: %r steht %d-mal' % (alt, text.count(alt)))
    text = text.replace(alt, '<w xml:id="%s"%s>%s</w>' % (xml_id, attrs, form))
    neu[pfad] = mit_change(text, EINTRAG['LOB'], 'KVO')
    print('  KVO   lob nachgetragen')

    lex = AUTH_DIR / 'lexicon.xml'
    with open(lex, encoding='utf-8', newline='') as fh:
        text = fh.read()
    neu[lex] = loesche_eintraege(text, loeschen)
    print('lexicon.xml: %d Eintraege geloescht' % len(loeschen))

    # Jede Datei muss nach der Aenderung wohlgeformt sein, bevor irgendetwas geschrieben wird.
    for pfad, text in neu.items():
        try:
            etree.fromstring(text.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            sys.exit('FEHLER: %s waere nicht wohlgeformt: %s' % (pfad.name, e))
    for pfad, text in neu.items():
        if args.apply:
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
    print('%s: %d Dateien' % ('geschrieben' if args.apply else 'Trockenlauf', len(neu)))
    if not args.apply:
        print('Nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
