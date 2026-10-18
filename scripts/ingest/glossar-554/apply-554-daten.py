#!/usr/bin/env python3
"""#554 Datenteil, Lauf 18.10.2026: Korrekturen aus KZWs Entscheidungen vom 16.10.2026.

Grundlage: Kommentar von Katharina (EIL) vom 16.10.2026 in #554, Abschnitte 2 und 5,
und der Auftrag in `docs/playbooks/kickoffs/2026-10-18-kickoff-daten.md` (D4).

LEXIKON
- bri (lemma_32468): <pos>ADJ</pos> entfaellt ("brî: ADJ entfernen"). Im Korpus
  tragen die 9 Tokens ausschliesslich NOM.
- laerche (lemma_3654): der Verweis "(vgl. „lêrchenvuoʒ“)" in der Notiz entfaellt.
  lêrchenvuoʒ hat im Korpus keinen Beleg, auch nicht getrennt geschrieben; kein
  Lemma wird angelegt.

TOKEN
- nagel (lemma_4302): 9 Tokens im Gewuerzkontext tragen das Lemma, aber kein @ana.
  Sie bekommen @ana auf lemma_4302_sense_6725 (Gewuerzpflanzen, Notiz Gewuerznelke).
- truebe (lemma_15282): 17 Tokens gehoeren nicht zur Weintraube. 13 Adjektive gehen
  auf lemma_6251 trüebe (@pos ADJ), 4 Verben auf lemma_6252 trüeben (@pos VRB). Das
  alte @ana (Traubensinn) faellt, ein neues wird nicht gesetzt: die Bedeutung bleibt offen.
  Typen nach der Regel aus #367: neue Nummer praegen, nie eine bestehende umhaengen.
  Hoechste vergebene Nummer am 18.10.2026: type_372860 (gemessen an variants.xml).
  variants.xml wird anschliessend mit extract-variants.py --apply regeneriert.

Wie apply-462-602.py: gefunden mit lxml, geschrieben textuell, Ist-Zustand vorher
verifiziert (nicht idempotent), Zeilenende erhalten, je Datei ein <change>.

Usage:
    python scripts/ingest/glossar-554/apply-554-daten.py           # Trockenlauf
    python scripts/ingest/glossar-554/apply-554-daten.py --apply
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
DATUM = '2026-10-18'
HOECHSTE_TYPNUMMER = 372860
FOLGE = ('lemmaRef', 'pos', 'ana', 'corresp', 'reason')

S_NAGEL = 'lemma_4302_sense_6725'
S_TRUEBE_ALT = 'lemma_15282_sense_25272'

# neue Typen: (Zeichenform im Text, Lemma) -> Typnummer
NEUER_TYP = {
    ('trüben', 'lemma_6251'): 'type_372861',
    ('trube', 'lemma_6251'): 'type_372862',
    ('trûben', 'lemma_6252'): 'type_372863',
    ('trûbe', 'lemma_6252'): 'type_372864',
    ('trüben', 'lemma_6252'): 'type_372865',
}

NAGEL = ['AXU_14617_5', 'DES2_21241050_6', 'DES2_281281120_4', 'FLO_2081_3', 'GSP_205000_0',
         'GSP_2710008_4', 'KBL3_18282030_6', 'PRT_2300_4', 'TRO_28297_4']
ADJ = {  # xml:id -> Form
    'FR1_2013050_4': 'trüben', 'FR1_13013060_1': 'trüben', 'FR2_731030_4': 'trüben',
    'GWTK_419122444200_2': 'trüben',
    'NEI_9701010_1': 'trube', 'NEIC_9701010_1': 'trube', 'NEI_11102110_5': 'trube',
    'NEIC_11102110_5': 'trube', 'NEIR_4201080_6': 'trube',
    'TRY_4343_3': 'trube', 'TRY_7374_4': 'trube', 'TRY_10404_3': 'trube', 'TRY_17088_3': 'trube',
}
VRB = {
    'AXS_4879000_5': 'trûben', 'AXS_4880000_2': 'trûbe', 'FR1_5067170_3': 'trüben',
    'PL3_336512_11': 'trüben',
}
ERWARTET = {'nagel': 9, 'adj': 13, 'vrb': 4}

ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)


def ref(lemma):
    return f'lexicon.xml#{lemma}'


def typ(t):
    return f'variants.xml#{t}'


def soll_tokens():
    """xml:id -> (Form, Paket, Ist-Pruefung (lemma, pos), Aenderung)"""
    t = {}
    for wid in NAGEL:
        t[wid] = (None, 'nagel', ('lemma_4302', 'NOM', None), dict(ana=ref(S_NAGEL)))
    for wid, form in ADJ.items():
        t[wid] = (form, 'adj', ('lemma_15282', 'NOM', ref(S_TRUEBE_ALT)),
                  dict(lemmaRef=ref('lemma_6251'), pos='ADJ', ana=None,
                       corresp=typ(NEUER_TYP[(form, 'lemma_6251')])))
    for wid, form in VRB.items():
        t[wid] = (form, 'vrb', ('lemma_15282', 'NOM', ref(S_TRUEBE_ALT)),
                  dict(lemmaRef=ref('lemma_6252'), pos='VRB', ana=None,
                       corresp=typ(NEUER_TYP[(form, 'lemma_6252')])))
    return t


def oeffnendes_tag(wid, attribute):
    teile = [f'xml:id="{wid}"'] + [f'{k}="{attribute[k]}"' for k in FOLGE if attribute.get(k) is not None]
    return '<w ' + ' '.join(teile) + '>'


def lexikon_aendern(text, fehler):
    # bri: ADJ raus
    m = re.search(r'(<entry xml:id="lemma_32468">\s*<form type="lemma">\s*<orth>brî</orth>\s*</form>\s*<gramGrp>)'
                  r'(.*?)(</gramGrp>)', text, re.S)
    if not m or '</entry>' in m.group(0):
        fehler.append('lemma_32468 brî: gramGrp nicht gefunden')
    else:
        werte = re.findall(r'<pos>([^<]*)</pos>', m.group(2))
        if werte != ['ADJ', 'NOM']:
            fehler.append(f'lemma_32468 brî: Lexikon {werte}, erwartet [ADJ, NOM]')
        else:
            nl = '\r\n' if '\r\n' in m.group(2) else '\n'
            einzug = re.search(r'([ \t]*)<pos>', m.group(2)).group(1)
            koerper = nl + f'{einzug}<pos>NOM</pos>{nl}' + einzug[:-2]
            text = text[:m.start(2)] + koerper + text[m.end(2):]
    # laerche: Verweis auf lêrchenvuoʒ
    alt = ' (vgl. „lêrchenvuoʒ“)'
    if text.count(alt) != 1:
        fehler.append(f'lêrche-Notiz: Verweis {text.count(alt)}x gefunden, erwartet 1')
    else:
        text = text.replace(alt, '')
    return text


def main():
    varianten = (ROOT / 'authority-files' / 'variants.xml').read_text(encoding='utf-8')
    hoechster = max(int(m) for m in re.findall(r'xml:id="type_(\d+)"', varianten))
    if hoechster != HOECHSTE_TYPNUMMER:
        sys.exit(f'ABBRUCH: hoechste Typnummer {hoechster}, erwartet {HOECHSTE_TYPNUMMER}')
    for t in NEUER_TYP.values():
        if f'xml:id="{t}"' in varianten:
            sys.exit(f'ABBRUCH: {t} steht schon in variants.xml')
    lexpfad = ROOT / 'authority-files' / 'lexicon.xml'
    with open(lexpfad, encoding='utf-8', newline='') as fh:
        lexikon = fh.read()
    for sid in (S_NAGEL,):
        if f'xml:id="{sid}"' not in lexikon:
            sys.exit(f'ABBRUCH: {sid} fehlt in lexicon.xml')
    for lid in ('lemma_6251', 'lemma_6252'):
        if f'<entry xml:id="{lid}">' not in lexikon:
            sys.exit(f'ABBRUCH: {lid} fehlt in lexicon.xml')

    TOKENS = soll_tokens()
    zaehl = defaultdict(int)
    for _, paket, _, _ in TOKENS.values():
        zaehl[paket] += 1
    if dict(zaehl) != ERWARTET:
        sys.exit(f'ABBRUCH: Tokenliste {dict(zaehl)}, erwartet {ERWARTET}')

    fehler = []
    lexikon_neu = lexikon_aendern(lexikon, fehler)

    je_datei = defaultdict(list)
    for wid in TOKENS:
        je_datei[wid.split('_')[0]].append(wid)

    # Phase 1: Ist-Zustand pruefen
    ist_corresp = {}
    for sigle, ids in sorted(je_datei.items()):
        gefunden = {w.get(XMLID): w
                    for w in etree.parse(str(ROOT / 'tei' / f'{sigle}.tei.xml')).iter(f'{TEI_NS}w')}
        for wid in ids:
            w = gefunden.get(wid)
            if w is None:
                fehler.append(f'{wid}: nicht gefunden')
                continue
            form_soll, paket, (lem, pos, ana), _ = TOKENS[wid]
            form = ''.join(w.itertext()).strip()
            if form_soll is not None and form != form_soll:
                fehler.append(f'{wid}: Form {form!r}, erwartet {form_soll!r}')
            if (w.get('lemmaRef'), w.get('pos'), w.get('ana')) != (ref(lem), pos, ana):
                fehler.append(f'{wid}: lemmaRef/pos/ana {w.get("lemmaRef")} {w.get("pos")} {w.get("ana")}')
            if w.get('reason') is not None or not w.get('corresp'):
                fehler.append(f'{wid}: reason oder corresp unerwartet')
            if set(w.attrib) - set(FOLGE) - {XMLID}:
                fehler.append(f'{wid}: weitere Attribute {sorted(w.attrib)}')
            ist_corresp[wid] = w.get('corresp')
    if fehler:
        print('ABBRUCH, der Ist-Zustand weicht ab. Nichts wurde geschrieben:')
        for f in fehler:
            print('   ' + f)
        return 1
    print(f'Ist-Zustand wie erwartet: {len(TOKENS)} Tokens in {len(je_datei)} Dateien.')

    # Phase 2: textuell ersetzen
    neu = {}
    for sigle, ids in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        for wid in ids:
            _, _, (lem, pos, ana), aend = TOKENS[wid]
            soll = dict(lemmaRef=ref(lem), pos=pos, ana=ana, corresp=ist_corresp[wid], reason=None)
            soll.update(aend)
            muster = re.compile(r'<w xml:id="' + re.escape(wid) + r'"[^>]*>([^<]*)</w>')
            if len(muster.findall(text)) != 1:
                sys.exit(f'ABBRUCH: {wid} nicht genau einmal textuell')
            text, n = muster.subn(lambda m, t=oeffnendes_tag(wid, soll): t + m.group(1) + '</w>', text)
            if n != 1:
                sys.exit(f'ABBRUCH: {wid} {n}x ersetzt')
        m = ANKER.search(text)
        if not m:
            sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {sigle}')
        nl = '\r\n' if '\r\n' in m.group(3) else '\n'
        n_nagel = sum(1 for wid in ids if TOKENS[wid][1] == 'nagel')
        n_adj = sum(1 for wid in ids if TOKENS[wid][1] == 'adj')
        n_vrb = sum(1 for wid in ids if TOKENS[wid][1] == 'vrb')
        saetze = []
        if n_nagel:
            saetze.append(f'#554 nagel: {n_nagel} Token{"" if n_nagel == 1 else "s"} im Gewuerzkontext mit '
                          f'@ana auf {S_NAGEL} gesetzt.')
        if n_adj + n_vrb:
            saetze.append(f'#554 trûbe: {n_adj + n_vrb} Token{"" if n_adj + n_vrb == 1 else "s"} '
                          f'(Adjektiv trüebe {n_adj}, Verb trüeben {n_vrb}) von lemma_15282 umgehaengt, '
                          f'@ana entfaellt.')
        eintrag = f'<change when="{DATUM}" who="#editor">{" ".join(saetze)}</change>'
        text = text[:m.end(2)] + nl + m.group(1) + eintrag + text[m.end(2):]
        neu[pfad] = text

    if APPLY:
        for pfad, text in neu.items():
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
        with open(lexpfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(lexikon_neu)
    print(f'{len(TOKENS)} Tokens in {len(neu)} Dateien, lexicon.xml: brî und lêrche, neue Typen '
          f'{sorted(NEUER_TYP.values())}' + ('' if APPLY else '  [Trockenlauf]'))
    if not APPLY:
        print('Trockenlauf, nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
