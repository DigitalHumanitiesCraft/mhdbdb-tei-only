#!/usr/bin/env python3
"""Setzt die drei von @wachauer entschiedenen Annotationspakete um.

  #366  8 Tokens aus dem fyndling-Beitrag (Entscheidungen vom 11.09. und 17.09.)
  #375  4 Tokens der Form waeren, die KZW am 14.09. als ADJ gelesen hat
  #371  76 Tokens der Form stat/stât aus ihrem JSON-Review vom 15.09.

Zusammen 88 Tokens in 45 Korpusdateien, ein gemeinsamer Rebuild der
abgeleiteten Schicht, ein Versions-Bump.

WAS DAS SKRIPT NICHT TUT
------------------------
Kein `@ana`. In keinem der drei Vorgaenge hat KZW einen Sense benannt, und die
Sense-Zuordnung ist nach TEI-MODEL-AUTH-FILES.md kuratorisch ("New sense
meanings are curatorial (the team assigns the concept), not automatically
reconstructible from the corpus"). Ein hier gesetztes @ana waere kuratorische
Arbeit des Skripts. Korpusweit tragen 1.554.314 von 7.547.816 <w> mit
@lemmaRef kein @ana, der Zustand ist also Praxis und kein Loch. Das gilt auch
fuer FR1_4007060_6, dessen `sense`-Feld im reichen `faelle`-Array aus unserem
Vorschlag stammt und nicht aus KZWs Entscheidung (ihr `actions`-Array fuehrt
ueberhaupt kein sense-Feld).

Nicht angefasst werden ausserdem die 17 Faelle mit `option: OFFEN` und die 2 mit
`option: NEU_STAND` aus #371. Letztere braeuchten ein neues Lemma, und
Lemmaanlage kommt in diesem Lauf nirgends vor.

TYPEN
-----
Ein `type_N` ist EINE Schreibform EINES Lemmas. `extract-variants.py` loest ein
mehrdeutiges Typ-Lemma-Paar per Mehrheit auf, ohne Exit-Code, und genau das
gilt es zu vermeiden. Deshalb die Regel aus #367: neue Nummer praegen, nie eine
bestehende umhaengen. Zehn Nummern werden gepraegt, 372377 bis 372386; die
Zuordnung steht in TYPEN unten und in ingest/pos-disambig/*/README.md.

Der haerteste Fall ist `hawsen`: die Form wird bereits gefuehrt, aber unter
lemma_49714 (huesenblater, type_372368), gepraegt im #363-Lauf fuer die getrennt
geschriebenen Erstglieder. Ein Umhaengen risse jene Tokens mit.

SCHREIBWEISE
------------
Textuell auf den Dateien, nicht ueber einen Parse-Baum: eine
lxml-Neuserialisierung fasst alle Bytes an und macht die Diffs unlesbar
(dieselbe Begruendung wie in scripts/sync/sync_tei_headers.py und
fix-363-hausenblase.py). Gefunden wird mit lxml, geschrieben mit str.replace.

Nur das oeffnende <w>-Tag aendert sich; Tokentext, Reihenfolge und xml:id
bleiben byte-identisch (Invariante POS-TAGSET.md §6.3.4).

Der Ist-Zustand jedes Tokens wird vorher verifiziert und das Skript bricht ab,
wenn er abweicht. Es ist deshalb nicht idempotent: ein zweiter Lauf setzt den
Korpusstand VOR dem Batch voraus.

Usage:
    python scripts/ingest/pos-disambig/apply-366-375-371.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-366-375-371.py --apply
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
TEI_NS = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'

APPLY = '--apply' in sys.argv

# --------------------------------------------------------------------------
# Typvergabe. Hoechste vergebene Nummer am 21.09.2026: type_372376 (frisch
# gemessen an variants.xml, nicht aus einem Ticket uebernommen). Die zehn
# Nummern werden hier EINMAL vergeben, damit eine Fortsetzung nicht eine elfte
# praegt. Schluessel ist (Form im Korpus, Ziellemma).
# --------------------------------------------------------------------------
TYPEN = {
    # #366, alphabetisch nach Form
    ('bersige',         'lemma_26988'): 'type_372377',
    ('gehornn',         'lemma_2039'):  'type_372378',
    ('gewuertz',        'lemma_7736'):  'type_372379',
    ('hawsen',          'lemma_42619'): 'type_372380',
    ('würczenn',        'lemma_7736'):  'type_372381',
    ('würtzenn',        'lemma_7736'):  'type_372382',
    ('zimendtrinttenn', 'lemma_26776'): 'type_372383',
    # #371, neu
    ('stat',            'lemma_5712'):  'type_372384',
    ('stat',            'lemma_5713'):  'type_372385',
    ('stât',            'lemma_5732'):  'type_372386',
    # #371, bestehend
    ('stat',            'lemma_5710'):  'type_20050',
    ('stat',            'lemma_5732'):  'type_20161',
    # #375, bestehend: alle vier offenen Faelle tragen die Form wâren
    ('wâren',           'lemma_7338'):  'type_287014',
}
NEU_AB, NEU_BIS = 372377, 372386

# --------------------------------------------------------------------------
# #366: acht Tokens, alle heute ohne jede Annotation.
# Ziel je Token aus KZWs Kommentaren vom 11.09. und 17.09.2026.
# Format: (xml:id, Form, Ziellemma, Ziel-pos, Herkunft der Entscheidung)
# --------------------------------------------------------------------------
PAKET_366 = [
    ('DES2_591312010_1', 'bersige',         'lemma_26988', 'NOM', 'KZW 17.09., Punkt 1'),
    ('KBL4_981191050_3', 'gewuertz',        'lemma_7736',  'NOM', 'KZW 17.09., Punkt 2'),
    ('KDO_121160700_11', 'gehornn',         'lemma_2039',  'NOM', 'KZW 17.09., Punkt 3'),
    ('KDO_123250200_3',  'würtzenn',        'lemma_7736',  'NOM', 'KZW 17.09., Punkt 4'),
    ('KDO_124310400_12', 'würczenn',        'lemma_7736',  'NOM', 'KZW 17.09., Punkt 5'),
    ('KDO_123290200_10', 'zimendtrinttenn', 'lemma_26776', 'NOM', 'KZW 11.09., Zimtrinde'),
    ('KBL3_11282040_1',  'hawsen',          'lemma_42619', 'NOM', 'KZW 11.09., hausen der Fisch'),
    ('MBS2_52060_11',    'hawsen',          'lemma_42619', 'NOM', 'KZW 11.09., hausen der Fisch'),
]

# --------------------------------------------------------------------------
# #375: die vier Faelle, die KZW am 14.09. als ADJ gelesen hat. Die vier
# VRB-Faelle derselben Tabelle bestaetigen den Ist-Zustand und werden nicht
# angefasst; die acht "eindeutigen" sind seit PR #438 erledigt (nachgemessen).
# Format: (xml:id, Form, Quelltyp am Token, Ziellemma, Ziel-pos)
# --------------------------------------------------------------------------
PAKET_375 = [
    ('TIT_50020_2',  'wâren', 'type_273621', 'lemma_7338', 'ADJ'),
    ('PZ_23625_1',   'wâren', 'type_273621', 'lemma_7338', 'ADJ'),
    ('NLC_196220_1', 'wâren', 'type_273621', 'lemma_7338', 'ADJ'),
    ('KU_1534_3',    'wâren', 'type_273621', 'lemma_7338', 'ADJ'),
]

# #371 wird aus KZWs abgelegtem JSON gelesen, nicht abgeschrieben.
JSON_371 = ROOT / 'ingest' / 'pos-disambig' / '371-stat' / 'kzw-review-2026-09-15.json'

REVISION = {
    '366': ('<change when="2026-09-21" who="#editor">#366 fyndling-Beitrag: {n} '
            'unlemmatisierte Tokens annotiert (lemmaRef/pos/corresp; editorische '
            'Entscheidungen KZW vom 11.09. und 17.09.2026; je Schreibung ein neu '
            'gepraegter Variantentyp nach der Regel aus #367; kein @ana, weil die '
            'Sense-Zuordnung kuratorisch ist; Provenienz-Log: '
            'ingest/pos-disambig/366-fyndling/).</change>'),
    '375': ('<change when="2026-09-21" who="#editor">#375 waeren als Adjektiv: {n} '
            'Tokens der Form wâren von lemma_7505 wesen VRB auf lemma_7338 wâr ADJ '
            'umannotiert (lemmaRef/pos/corresp auf den bestehenden type_287014; '
            'Lektuere KZW vom 14.09.2026; Provenienz-Log: '
            'ingest/pos-disambig/375-waeren-ausweitung/).</change>'),
    '371': ('<change when="2026-09-21" who="#editor">#371 stat, drittes Lemma: {n} '
            'bislang unlemmatisierte Tokens der Form stat/stât annotiert '
            '(lemmaRef/pos/corresp nach dem actions-Array in KZWs Review vom '
            '15.09.2026; drei neu gepraegte Variantentypen; kein @ana, weil die '
            'Sense-Zuordnung kuratorisch ist; die 17 Faelle mit option OFFEN und die '
            '2 mit NEU_STAND bleiben unangetastet; Provenienz-Log: '
            'ingest/pos-disambig/371-stat/).</change>'),
}

ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)\s*\n(\s*)</revisionDesc>',
    re.S)


def frag(wert):
    """Nimmt den Fragmentbezeichner eines Verweisattributs, oder None."""
    if not wert:
        return None
    return wert.split()[0].split('#', 1)[-1]


def lade_371():
    """#371: die 76 Arbeitsfaelle aus KZWs JSON, mit zwei harten Bedingungen."""
    with open(JSON_371, encoding='utf-8') as fh:
        obj = json.load(fh)
    faelle, actions = obj['faelle'], obj['actions']
    if len(faelle) != 95:
        sys.exit(f'ABBRUCH: faelle hat {len(faelle)} Eintraege, erwartet 95')
    if len(actions) != 76:
        sys.exit(f'ABBRUCH: actions hat {len(actions)} Eintraege, erwartet 76')
    # Gegenprobe: die Arbeitsliste laesst sich auf einem zweiten, unabhaengigen
    # Weg bilden, und beide Wege muessen dieselbe MENGE ergeben, nicht nur
    # dieselbe Zahl. Sonst arbeitet das Skript auf einer Liste, die niemand
    # geprueft hat.
    ueber_option = {f['xml_id'] for f in faelle if str(f['option']).startswith('lemma_')}
    ueber_actions = {a['xml_id'] for a in actions}
    if ueber_option != ueber_actions:
        sys.exit('ABBRUCH: die beiden Wege zur Arbeitsliste ergeben verschiedene '
                 f'Mengen, Differenz: {sorted(ueber_option ^ ueber_actions)}')
    return [(a['xml_id'], a['form'], a['lemma'], a['pos']) for a in actions]


def scanne(ids):
    """Ist-Zustand aller genannten Tokens, aus den betroffenen Dateien."""
    je_sigle = defaultdict(set)
    for wid in ids:
        je_sigle[wid.rsplit('_', 2)[0]].add(wid)
    ist = {}
    for sigle, wids in je_sigle.items():
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        if not pfad.exists():
            sys.exit(f'ABBRUCH: {pfad} fehlt')
        for w in etree.parse(str(pfad)).iter(f'{TEI_NS}w'):
            wid = w.get(XMLID)
            if wid in wids:
                ist[wid] = {
                    'datei': f'{sigle}.tei.xml',
                    'form': ''.join(w.itertext()).strip(),
                    'lemmaRef': frag(w.get('lemmaRef')),
                    'pos': w.get('pos'),
                    'ana': frag(w.get('ana')),
                    'corresp': frag(w.get('corresp')),
                }
    return ist


def pruefe(auftraege, ist):
    """Erwarteter Ist-Zustand je Token. Abbruch bei jeder Abweichung."""
    fehler = []
    for auf in auftraege:
        wid = auf['xml_id']
        d = ist.get(wid)
        if d is None:
            fehler.append(f'{wid}: nicht im Korpus gefunden')
            continue
        if d['form'] != auf['form']:
            fehler.append(f'{wid}: Form {d["form"]!r}, erwartet {auf["form"]!r}')
        if d['lemmaRef'] != auf['ist_lemmaRef']:
            fehler.append(f'{wid}: lemmaRef {d["lemmaRef"]}, erwartet {auf["ist_lemmaRef"]}')
        if d['pos'] != auf['ist_pos']:
            fehler.append(f'{wid}: pos {d["pos"]}, erwartet {auf["ist_pos"]}')
        if d['corresp'] != auf['ist_corresp']:
            fehler.append(f'{wid}: corresp {d["corresp"]}, erwartet {auf["ist_corresp"]}')
        if d['ana'] is not None:
            fehler.append(f'{wid}: traegt bereits ana={d["ana"]}, das Skript hat dafuer keine Regel')
    return fehler


def baue_auftraege():
    """Die 88 Auftraege, je einer pro Token, mit Soll und erwartetem Ist."""
    auftraege = []

    for wid, form, lemma, pos, herkunft in PAKET_366:
        auftraege.append({
            'paket': '366', 'xml_id': wid, 'form': form, 'herkunft': herkunft,
            'ist_lemmaRef': None, 'ist_pos': None, 'ist_corresp': None,
            'soll_lemmaRef': lemma, 'soll_pos': pos,
            'soll_corresp': TYPEN[(form, lemma)],
        })

    for wid, form, quelltyp, lemma, pos in PAKET_375:
        auftraege.append({
            'paket': '375', 'xml_id': wid, 'form': form,
            'herkunft': 'KZW 14.09., Tabelle der acht gelesenen Faelle',
            'ist_lemmaRef': 'lemma_7505', 'ist_pos': 'VRB', 'ist_corresp': quelltyp,
            'soll_lemmaRef': lemma, 'soll_pos': pos,
            'soll_corresp': TYPEN[(form, lemma)],
        })

    # #371. Drei Tokens tragen heute bereits pos="NOM" ohne @lemmaRef; KZW hat
    # dort VRB entschieden (Felder pos/option/status in ihrem Review), der Wert
    # wird also ueberschrieben. Das ist die einzige Stelle im ganzen Lauf, an
    # der ein vorhandener Attributwert weicht, und sie steht deshalb hier
    # ausdruecklich und nicht als Nebenwirkung.
    POS_VORHANDEN = {'ADP_6505000_1': 'NOM', 'ADP_6511900_11': 'NOM', 'ADP_6605700_8': 'NOM'}
    for wid, form, lemma, pos in lade_371():
        schluessel = (form, lemma)
        if schluessel not in TYPEN:
            sys.exit(f'ABBRUCH: keine Typregel fuer {schluessel} ({wid})')
        auftraege.append({
            'paket': '371', 'xml_id': wid, 'form': form,
            'herkunft': 'KZW 15.09., actions-Array',
            'ist_lemmaRef': None, 'ist_pos': POS_VORHANDEN.get(wid), 'ist_corresp': None,
            'soll_lemmaRef': lemma, 'soll_pos': pos,
            'soll_corresp': TYPEN[schluessel],
        })
    return auftraege


def main():
    auftraege = baue_auftraege()
    print(f'Auftraege: {len(auftraege)} Tokens '
          f'(#366 {sum(1 for a in auftraege if a["paket"] == "366")}, '
          f'#375 {sum(1 for a in auftraege if a["paket"] == "375")}, '
          f'#371 {sum(1 for a in auftraege if a["paket"] == "371")})')

    ids = [a['xml_id'] for a in auftraege]
    if len(set(ids)) != len(ids):
        doppelt = sorted({i for i in ids if ids.count(i) > 1})
        sys.exit(f'ABBRUCH: xml:id doppelt beauftragt: {doppelt}')

    ist = scanne(ids)
    fehler = pruefe(auftraege, ist)
    if fehler:
        print('ABBRUCH, der Ist-Zustand weicht ab. Nichts wurde geschrieben:')
        for f in fehler:
            print(f'   {f}')
        return 1
    print(f'Ist-Zustand aller {len(auftraege)} Tokens wie erwartet.')

    # Die gepraegten Nummern, vor dem ersten gesetzten Token ausgegeben.
    print()
    print('Neu gepraegte Variantentypen:')
    gebraucht = {a['soll_corresp'] for a in auftraege}
    for (form, lemma), tid in sorted(TYPEN.items(), key=lambda x: x[1]):
        nr = int(tid.split('_')[1])
        if NEU_AB <= nr <= NEU_BIS:
            n = sum(1 for a in auftraege if a['soll_corresp'] == tid)
            print(f'   {tid}  {form:16} unter {lemma:14} {n:3} Tokens')
    print('Weiterverwendete bestehende Typen:')
    for (form, lemma), tid in sorted(TYPEN.items(), key=lambda x: x[1]):
        nr = int(tid.split('_')[1])
        if not (NEU_AB <= nr <= NEU_BIS) and tid in gebraucht:
            n = sum(1 for a in auftraege if a['soll_corresp'] == tid)
            print(f'   {tid}  {form:16} unter {lemma:14} {n:3} Tokens')

    # ---------------------------------------------------------------- schreiben
    je_datei = defaultdict(list)
    for a in auftraege:
        je_datei[ist[a['xml_id']]['datei']].append(a)

    print()
    print(f'Betroffene Korpusdateien: {len(je_datei)}')
    geschrieben = 0
    for dateiname, rows in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / dateiname
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()

        for a in rows:
            wid = a['xml_id']
            muster = re.compile(r'<w xml:id="' + re.escape(wid) + r'"[^>]*>([^<]*)</w>')
            treffer = muster.findall(text)
            if len(treffer) != 1:
                sys.exit(f'ABBRUCH: {wid} kommt {len(treffer)}x im Text vor, erwartet 1x')
            if treffer[0].strip() != a['form']:
                sys.exit(f'ABBRUCH: {wid} hat im Text die Form {treffer[0]!r}, '
                         f'erwartet {a["form"]!r}')
            neu_tag = (f'<w xml:id="{wid}" lemmaRef="lexicon.xml#{a["soll_lemmaRef"]}" '
                       f'pos="{a["soll_pos"]}" corresp="variants.xml#{a["soll_corresp"]}">')
            text, n = muster.subn(neu_tag + treffer[0] + '</w>', text)
            if n != 1:
                sys.exit(f'ABBRUCH: {wid} wurde {n}x ersetzt, erwartet 1x')
            geschrieben += 1

        # Ein revisionDesc-Eintrag je Paket, das diese Datei beruehrt.
        for paket in ('366', '375', '371'):
            n = sum(1 for a in rows if a['paket'] == paket)
            if not n:
                continue
            m = ANKER.search(text)
            if not m:
                sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {dateiname}')
            eintrag = REVISION[paket].format(n=n)
            text = text[:m.end(2)] + '\n' + m.group(1) + eintrag + text[m.end(2):]

        if APPLY:
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
        pakete = ','.join(sorted({a['paket'] for a in rows}))
        print(f'   {dateiname:20} {len(rows):3} Tokens  (#{pakete})'
              + ('' if APPLY else '  [Trockenlauf]'))

    print()
    print(f'Tokens geschrieben: {geschrieben}')
    print(f'Neue Typen: {NEU_BIS - NEU_AB + 1} (type_{NEU_AB} bis type_{NEU_BIS})')
    if not APPLY:
        print('\nTrockenlauf, nichts geaendert. Mit --apply schreiben.')
    else:
        print('\nGeschrieben. Jetzt die Kette aus dem Data-Change-Lifecycle:')
        print('   python scripts/sync/extract-variants.py            # Gegenprobe ohne --apply')
        print('   python scripts/sync/extract-variants.py --apply')
        print('   python scripts/build-corpus-index.py --allow-dirty')
        print('   python scripts/build-authority-index.py --allow-dirty')
        print('   python scripts/build-api.py --allow-dirty')
    return 0


if __name__ == '__main__':
    sys.exit(main())
