#!/usr/bin/env python3
"""#462 (Lexikon gegen Korpus, 25 Lemmata) und #602 (naschen), Lauf 18.10.2026.

Freigabe: Kickoff `docs/playbooks/kickoffs/2026-10-18-kickoff-daten.md` (D1, D2),
Grundlage KZWs Antwort vom 16.10.2026 in #462 (Codes a, b, c uebernommen;
guenlich: Gunst als NOM; deprofundis: NOM; ungenuoge: ADV) und der Auftrag in
#602. Vorschlagsliste: `ingest/pos-disambig/462-pos/vorschlaege.tsv`.

LEXIKON (a und guenlich): 16 Lemmata bekommen Wortarten dazu, 17 Wortarten
insgesamt (ater: PRP und PRO). Nichts wird entfernt. Die Reihenfolge in
`<gramGrp>` ist alphabetisch (10.158 von 10.160 Eintraegen mit mehr als einer
Wortart, gemessen am 18.10.2026), neue Werte werden dort einsortiert.

TOKEN (b, deprofundis, ungenuoge): 6 Tokens aendern `@pos`. Das `@reason`
fuer die Fusion ze+dolne (Vorschlag in vorschlaege.tsv) entfaellt: ein `@reason`
auf <w> macht die Datei fuer tei_all ungueltig, JT stuende dann neu ausserhalb
der Baseline in validate-corpus.py (gemessen am 18.10.2026). #602: 4 Tokens
von naschen bekommen `@ana` auf
lemma_57919_sense_93122 (Essen).

UMHAENGEN (c): ADP_201100_7 (aditus) kommt von lemma_67689 adire auf
lemma_67813 aditus, ADP_701000_13 (standime) von lemma_70735 steter auf
lemma_70734 stander. Typen nach der Regel aus #367: neue Nummer praegen, nie
eine bestehende umhaengen. Hoechste vergebene Nummer am 18.10.2026: type_372858
(gemessen an variants.xml). Gepraegt werden type_372859 (aditus unter
lemma_67813) und type_372860 (standime unter lemma_70734); variants.xml wird
anschliessend mit extract-variants.py --apply regeneriert.

NICHT UMGESETZT: indelicius (ADP_104900_10) und unpeweglich (LZT_2360_0), und
der Kommentartext zu deprofundis/indelicius; beides geht als Frage an KZW.
Ebenso der Beleg OVW_1025010230_4 von naschen (Essen oder Erotik offen).

SCHREIBWEISE
------------
Wie apply-460-461-rest.py: gefunden mit lxml, geschrieben textuell, Ist-Zustand
vorher verifiziert (nicht idempotent), Zeilenende erhalten, je Datei ein
<change> in der revisionDesc.

Usage:
    python scripts/ingest/pos-disambig/apply-462-602.py           # Trockenlauf
    python scripts/ingest/pos-disambig/apply-462-602.py --apply
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
HOECHSTE_TYPNUMMER = 372858

# Lemma -> (Lemmaform, Ist-Wortarten im Lexikon, hinzuzufuegende Wortarten)
LEXIKON = {
    'lemma_28722': ('ordenter', ['PRO', 'VRB'], ['ADJ']),
    'lemma_35938': ('enzerrîzen', ['ADV', 'NEG', 'VRB'], ['ADJ']),
    'lemma_36303': ('wandelsâne', ['ADJ', 'ADV'], ['NOM']),
    'lemma_36513': ('gewiʒʒenlôs', ['ADV', 'NEG'], ['ADJ']),
    'lemma_36569': ('enerleschen', ['NEG', 'VRB'], ['ADJ']),
    'lemma_39197': ('enfirmen', ['ADV', 'NEG', 'VRB'], ['ADJ']),
    'lemma_48265': ('devotus', ['ADJ', 'GRA'], ['ADV']),
    'lemma_48743': ('enwunden', ['ADV', 'NEG', 'VRB'], ['ADJ']),
    'lemma_52645': ('nâchder', ['ADV', 'ART'], ['PRP']),
    'lemma_54948': ('decies', ['ADJ', 'ADV'], ['NUM']),
    'lemma_54949': ('sepcies', ['ADJ', 'ADV'], ['NUM']),
    'lemma_62410': ('clemens', ['ADJ', 'GRA'], ['ADV']),
    'lemma_67708': ('ater', ['ADJ', 'NOM'], ['PRO', 'PRP']),
    'lemma_23289': ('Cristeleison', ['NAM', 'VRB'], ['INJ']),
    'lemma_24478': ('enbewegen', ['NEG', 'VRB'], ['ADJ']),
    'lemma_21642': ('günlich', ['ADJ', 'ADV'], ['NOM']),
}
ERWARTET_LEXIKON = (16, 17)

N93122 = 'lemma_57919_sense_93122'
S_ADITUS = 'lemma_67813_sense_105127'
NEUER_TYP = {'aditus': 'type_372859', 'standime': 'type_372860'}

# xml:id -> (Form, Ist-Attribute, Soll-Attribute); Attribute ohne xml:id,
# None = Attribut fehlt. Reihenfolge der Ausgabe: lemmaRef pos ana corresp reason.
FOLGE = ('lemmaRef', 'pos', 'ana', 'corresp', 'reason')


def ref(lemma):
    return f'lexicon.xml#{lemma}'


def typ(t):
    return f'variants.xml#{t}'


TOKENS = {
    # b: zedolne, ze+doln (ohne @reason, siehe Docstring)
    'JT_48512000_3': ('zedolne',
                      dict(lemmaRef=ref('lemma_17456'), pos='CNJ VRB', ana=ref('lemma_17456_sense_29790'),
                           corresp=typ('type_75261'), reason=None),
                      dict(pos='PRP VRB'), '462'),
    'JT_48672000_3': ('zedolne',
                      dict(lemmaRef=ref('lemma_17456'), pos='CNJ VRB', ana=ref('lemma_17456_sense_29790'),
                           corresp=typ('type_75261'), reason=None),
                      dict(pos='PRP VRB'), '462'),
    # b: alwirdic, immo
    'AC1_34630_0': ('allerwirdigister',
                    dict(lemmaRef=ref('lemma_36619'), pos='NOM', ana=ref('lemma_36619_sense_57192'),
                         corresp=typ('type_189527'), reason=None),
                    dict(pos='ADJ'), '462'),
    'AC1_35150_4': ('ymmo',
                    dict(lemmaRef=ref('lemma_78454'), pos='CNJ', ana=ref('lemma_78454_sense_117010'),
                         corresp=typ('type_367451'), reason=None),
                    dict(pos='ADV'), '462'),
    # KZW 16.10.: deprofundis NOM, ungenuoge ADV
    'ADP_8507000_12': ('deprofundis',
                       dict(lemmaRef=ref('lemma_55290'), pos='NAM', ana=ref('lemma_55290_sense_89987'),
                            corresp=typ('type_302410'), reason=None),
                       dict(pos='NOM'), '462'),
    'AXU_8247_3': ('ungenuoge',
                   dict(lemmaRef=ref('lemma_29486'), pos='ADJ ADV NEG', ana=ref('lemma_29486_sense_3333'),
                        corresp=typ('type_147751'), reason=None),
                   dict(pos='ADV'), '462'),
    # c: Umhaengen
    'ADP_201100_7': ('aditus',
                     dict(lemmaRef=ref('lemma_67689'), pos='NOM', ana=ref('lemma_67689_sense_105013'),
                          corresp=typ('type_341714'), reason=None),
                     dict(lemmaRef=ref('lemma_67813'), ana=ref(S_ADITUS), corresp=typ(NEUER_TYP['aditus'])),
                     '462'),
    'ADP_701000_13': ('standime',
                      dict(lemmaRef=ref('lemma_70735'), pos='ADJ', ana=None,
                           corresp=typ('type_350509'), reason=None),
                      dict(lemmaRef=ref('lemma_70734'), corresp=typ(NEUER_TYP['standime'])), '462'),
}
# #602 naschen
for _wid, _form, _typ in (('JEW_2743000000_3', 'naschen', 'type_310733'),
                          ('NEI_9806110_9', 'naschen', 'type_310733'),
                          ('NEIC_9806110_9', 'naschen', 'type_310733'),
                          ('NEIR_1607110_10', 'naschen', 'type_310733')):
    TOKENS[_wid] = (_form,
                    dict(lemmaRef=ref('lemma_57919'), pos='VRB', ana=None, corresp=typ(_typ), reason=None),
                    dict(ana=ref(N93122)), '602')

ERWARTET_TOKENS = {'462': 8, '602': 4}

ANKER = re.compile(
    r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)(\s*)</revisionDesc>',
    re.S)


def oeffnendes_tag(wid, attribute):
    teile = [f'xml:id="{wid}"'] + [f'{k}="{attribute[k]}"' for k in FOLGE if attribute.get(k) is not None]
    return '<w ' + ' '.join(teile) + '>'


def lexikon_aendern(text, fehler):
    nl = '\r\n' if '\r\n' in text else '\n'
    for lid, (orth, ist, neu) in LEXIKON.items():
        muster = re.compile(
            r'(<entry xml:id="' + lid + r'">.*?<orth>' + re.escape(orth) + r'</orth>.*?<gramGrp>)(.*?)(</gramGrp>)',
            re.S)
        m = muster.search(text)
        if not m:
            fehler.append(f'{lid} {orth}: Eintrag nicht gefunden')
            continue
        # der Treffer darf nicht ueber das Ende des Eintrags hinausreichen
        if '</entry>' in m.group(0):
            fehler.append(f'{lid} {orth}: gramGrp ausserhalb des Eintrags gefunden')
            continue
        werte = re.findall(r'<pos>([^<]*)</pos>', m.group(2))
        if werte != ist:
            fehler.append(f'{lid} {orth}: Lexikon {werte}, erwartet {ist}')
            continue
        einzug = re.search(r'([ \t]*)<pos>', m.group(2)).group(1)
        soll = sorted(set(werte) | set(neu))
        koerper = nl + ''.join(f'{einzug}<pos>{p}</pos>{nl}' for p in soll) + einzug[:-2]
        text = text[:m.start(2)] + koerper + text[m.end(2):]
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
    for sid in (N93122, S_ADITUS):
        if f'xml:id="{sid}"' not in lexikon:
            sys.exit(f'ABBRUCH: {sid} fehlt in lexicon.xml')
    for lid in ('lemma_67813', 'lemma_70734'):
        if f'<entry xml:id="{lid}">' not in lexikon:
            sys.exit(f'ABBRUCH: {lid} fehlt in lexicon.xml')
    zaehl = defaultdict(int)
    for _, _, _, paket in TOKENS.values():
        zaehl[paket] += 1
    if dict(zaehl) != ERWARTET_TOKENS:
        sys.exit(f'ABBRUCH: Tokenliste {dict(zaehl)}, erwartet {ERWARTET_TOKENS}')
    if (len(LEXIKON), sum(len(v[2]) for v in LEXIKON.values())) != ERWARTET_LEXIKON:
        sys.exit('ABBRUCH: Lexikonliste hat nicht die erwartete Groesse')

    fehler = []
    lexikon_neu = lexikon_aendern(lexikon, fehler)

    je_datei = defaultdict(list)
    for wid in TOKENS:
        je_datei[wid.split('_')[0]].append(wid)

    # Phase 1: Ist-Zustand pruefen
    for sigle, ids in sorted(je_datei.items()):
        gefunden = {w.get(XMLID): w
                    for w in etree.parse(str(ROOT / 'tei' / f'{sigle}.tei.xml')).iter(f'{TEI_NS}w')}
        for wid in ids:
            w = gefunden.get(wid)
            if w is None:
                fehler.append(f'{wid}: nicht gefunden')
                continue
            form_soll, ist, _soll, _ = TOKENS[wid]
            form = ''.join(w.itertext()).strip()
            ist_echt = {k: w.get(k) for k in FOLGE}
            if form != form_soll or ist_echt != ist:
                fehler.append(f'{wid}: Form {form!r}, ist {ist_echt}, erwartet {ist}')
            if set(w.attrib) - set(FOLGE) - {XMLID}:
                fehler.append(f'{wid}: weitere Attribute {sorted(w.attrib)}')
    if fehler:
        print('ABBRUCH, der Ist-Zustand weicht ab. Nichts wurde geschrieben:')
        for f in fehler:
            print('   ' + f)
        return 1
    print(f'Ist-Zustand wie erwartet: {len(TOKENS)} Tokens in {len(je_datei)} Dateien, '
          f'{len(LEXIKON)} Lexikoneintraege.')

    # Phase 2: textuell ersetzen
    neu = {}
    for sigle, ids in sorted(je_datei.items()):
        pfad = ROOT / 'tei' / f'{sigle}.tei.xml'
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        for wid in ids:
            form, ist, aend, _ = TOKENS[wid]
            soll = dict(ist)
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
        n462 = sum(1 for wid in ids if TOKENS[wid][3] == '462')
        n602 = len(ids) - n462
        saetze = []
        if n462:
            saetze.append(f'#462 Lexikon gegen Korpus: {n462} Token{"" if n462 == 1 else "s"} nach KZWs '
                          f'Antwort vom 2026-10-16 in @pos oder Lemma angepasst.')
        if n602:
            saetze.append(f'#602 naschen: {n602} Token{"" if n602 == 1 else "s"} mit @ana auf '
                          f'{N93122} (Essen) gesetzt.')
        eintrag = f'<change when="{DATUM}" who="#editor">{" ".join(saetze)}</change>'
        text = text[:m.end(2)] + nl + m.group(1) + eintrag + text[m.end(2):]
        neu[pfad] = text

    if APPLY:
        for pfad, text in neu.items():
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
        with open(lexpfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(lexikon_neu)
    print(f'{len(TOKENS)} Tokens in {len(neu)} Dateien, lexicon.xml: {len(LEXIKON)} Eintraege, '
          f'{sum(len(v[2]) for v in LEXIKON.values())} Wortarten dazu, neue Typen {NEUER_TYP}'
          + ('' if APPLY else '  [Trockenlauf]'))
    if not APPLY:
        print('Trockenlauf, nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
