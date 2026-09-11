#!/usr/bin/env python3
"""#363: die Hausenblase korpusweit auf hûsenblâter (lemma_49714) zusammenfuehren.

Kontext (Issue #363): gemeldet war ein einzelnes Token, `hawssen` in MBS5, das
am Adjektiv heiʒ haengt. Die korpusweite Suche nach den Schreibformen (Erstglied
hau-/haw-/hu-, Zweitglied pl-/bl-) findet 19 Belege in 7 Sigeln, und alle sieben
sind Kochbuecher. Von den 19 sind heute 5 richtig; die uebrigen verteilen sich
auf sieben verschiedene Lemmata, darunter das Verb hûsen "wohnen", den hasen, das
Blatt einer Pflanze und die Moenchstonsur.

Die editorische Entscheidung hat KZW am 10.09. getroffen (Kommentar in #363):
"Alle Komposita und Kookurrenzen in diesem Kontext, egal in welcher Schreibart,
muessen zur Fischblase." Und, in einem zweiten Kommentar: "Schmeiss die
hasenblâse weg (lemma_27031), diese existiert nicht."

Damit macht dieses Skript drei Dinge:

  1. 6 zusammengeschriebene Komposita -> lemma_49714. Fuenf haengen schon dort,
     das KDO-Kompositum wandert von lemma_27031 herueber.
  2. 13 getrennt geschriebene Paare, BEIDE Tokens -> lemma_49714, derselbe
     Sense, @pos je Token einzeln, @corresp je Token eigen. Das ist der
     Hausstil des Korpus fuer Mehrwort-Einheiten (lemma_3141 Joie de la Court,
     lemma_9250 Schastel Marveile, das ebenfalls die getrennte UND die
     zusammengeschriebene Schreibung traegt); dokumentiert in TEI-MODEL.md
     §4.1a seit #425.
  3. lemma_27031 hasenblâse aus lexicon.xml geloescht. Der Eintrag hat
     korpusweit genau einen Beleg, und das ist das Token aus Punkt 1.

@ana wird hier gesetzt, anders als bei den #189/#198-Batches. Dort ist die
Sense-Zuordnung kuratorisch und bleibt deshalb leer; hier IST sie die
kuratorische Entscheidung, und sie benennt genau diesen Sense
(lemma_49714_sense_78649: Organe von Fischen, Atmung von Fischen, Verarbeitung
von Fischen).

TYPEN. @corresp zeigt auf den variants-Typ der Form unter dem Ziel-Lemma; ein
type_N ist EINE Schreibform EINES Lemmas (extract-variants.py loest ein
mehrdeutiges Typ-Lemma-Paar per Mehrheit auf, und genau das gilt es zu
vermeiden). Deshalb entscheidet das Skript pro Form:

  - Der Bestands-Typ wird WEITERVERWENDET, wenn ihn korpusweit nur Tokens aus
    dieser Menge tragen. Dann wandert die Form als Ganzes, das Quell-Lemma
    verliert sie zu Recht (Beispiel: type_131170 haueßenn, einziger Beleg von
    lemma_2670 fuer diese Form).
  - Sonst wird ab NEXT_TYPE_ID eine neue ID gepraegt, sortiert nach Form.
    Beispiel: type_106683 pleter traegt 45 Tokens, 43 davon bleiben bei
    lemma_737 blat. Wer den Typ mitnaehme, risse 43 fremde Tokens mit.

Die Weiterverwendung wird zur Laufzeit entschieden, nicht aus einer Liste
gelesen: das Skript scannt alle 667 Korpusdateien und praegt neu, sobald ein Typ
auch nur ein fremdes Token traegt. Die unten stehende Aufteilung in 5 weiter-
verwendete und 10 neue Typen ist also ein Messergebnis dieses Laufs und keine
Vorgabe; ein fremder Traeger an einer der 5 verschoebe sie stillschweigend nach
oben, ohne Abbruch. Abgebrochen wird nur, wo das Skript keine Regel hat: wenn
eine Form zwei verschiedene exklusive Typen traegt.

Die Typen materialisieren sich beim anschliessenden variants.xml-Rebuild, der
Korpus fuehrt.

Nur das oeffnende <w>-Tag aendert sich; Token-Text, Reihenfolge und xml:id
bleiben byte-identisch (Invariante POS-TAGSET.md §6.3.4). Geschrieben wird
textuell, gefunden mit lxml: ein lxml-Roundtrip wuerde sieben Korpusdateien
neu formatieren.

Usage:
    python scripts/ingest/pos-disambig/fix-363-hausenblase.py           # Trockenlauf
    python scripts/ingest/pos-disambig/fix-363-hausenblase.py --apply

Nicht idempotent: ein zweiter Lauf setzt den Korpus-Stand VOR dem Batch voraus,
weil das Skript den Ist-Zustand jedes Ziel-Tokens vorher verifiziert.
"""

import re
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'scripts'))
from corpus_files import corpus_files  # noqa: E402

TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'

APPLY = '--apply' in sys.argv

ZIEL_LEMMA = 'lemma_49714'
ZIEL_SENSE = 'lemma_49714_sense_78649'
ZIEL_POS = 'NOM'
LOESCH_LEMMA = 'lemma_27031'
LOESCH_SENSE_TYP = 'type_131175'   # einziger Beleg von lemma_27031, wandert mit
# Hoechste vergebene type-Nummer in variants.xml == Korpus-Maximum (nach #115
# loesen alle Korpus-@corresp auf). Zuletzt vergeben hat #189 bis 372365.
NEXT_TYPE_ID = 372366

# Ist-Zustand, am 10.09.2026 gemessen. (xml:id, Form, lemmaRef, pos, ana, corresp);
# None heisst: Attribut fehlt. Das Skript schreibt nur, wenn es genau das findet.
IST = [
    # --- 13 getrennt geschriebene Paare, beide Tokens ---
    ('HUB3_11080_11',      'hawssen',  'lemma_2730', 'ADJ', None,                    'type_272171'),
    ('HUB3_11090_0',       'pleter',   'lemma_737',  'NOM', None,                    'type_106683'),
    ('HUB3_71010_10',      'hawsen',   None,         None,  None,                    None),
    ('HUB3_71010_11',      'plotter',  'lemma_737',  'NOM', None,                    'type_272472'),
    ('HUB3_71040_0',       'hawsen',   None,         None,  None,                    None),
    ('HUB3_71040_1',       'ploter',   'lemma_737',  'NOM', None,                    'type_272473'),
    ('HUB3_77020_10',      'hawsen',   None,         None,  None,                    None),
    ('HUB3_77020_11',      'plater',   'lemma_734',  'NOM', None,                    'type_153734'),
    ('HUB3_77050_12',      'hawsen',   None,         None,  None,                    None),
    ('HUB3_77060_0',       'pleter',   'lemma_737',  'NOM', None,                    'type_106683'),
    ('HUB3_78030_2',       'hausen',   'lemma_2934', 'VRB', 'lemma_2934_sense_4710', 'type_163436'),
    ('HUB3_78030_3',       'ploter',   'lemma_737',  'NOM', None,                    'type_272473'),
    ('HUB3_79020_7',       'hawsen',   None,         None,  None,                    None),
    ('HUB3_79020_8',       'ploter',   'lemma_737',  'NOM', None,                    'type_272473'),
    ('KBL3_46962020_2',    'hausen',   'lemma_2934', 'VRB', None,                    'type_163436'),
    ('KBL3_46962020_3',    'platern',  'lemma_738',  'NOM', None,                    'type_271760'),
    ('KBL4_1051192050_12', 'husen',    None,         None,  None,                    None),
    ('KBL4_1051192060_0',  'blater',   'lemma_734',  'NOM', None,                    'type_173163'),
    ('KDO_121170100_2',    'haueßenn', 'lemma_2670', 'NOM', 'lemma_2670_sense_4300', 'type_131170'),
    ('KDO_121170100_3',    'plossenn', None,         None,  None,                    None),
    ('MBS2_34040_5',       'hausen',   'lemma_2934', 'VRB', None,                    'type_163436'),
    ('MBS2_34040_6',       'plateren', 'lemma_734',  'NOM', None,                    'type_274810'),
    ('MBS5_2151412120_10', 'hawssen',  'lemma_2730', 'ADJ', None,                    'type_272171'),
    ('MBS5_2151412130_0',  'platern',  'lemma_738',  'NOM', None,                    'type_271760'),
    ('SUB1_61040_0',       'hausen',   'lemma_2934', 'VRB', None,                    'type_163436'),
    ('SUB1_61040_1',       'pletter',  'lemma_737',  'NOM', None,                    'type_157201'),
    # --- 6 zusammengeschriebene Komposita ---
    ('KDO_120090100_2',    'haußenploßenn', 'lemma_27031', 'NOM', 'lemma_27031_sense_42996', 'type_131175'),
    ('MBS5_2041392010_7',  'hawssenplater', 'lemma_49714', 'NOM', ZIEL_SENSE,                'type_275110'),
    ('SUB1_10050_4',       'haussenpletern', 'lemma_49714', 'NOM', ZIEL_SENSE,               'type_284780'),
    ('SUB1_23080_2',       'haussenpleter', 'lemma_49714', 'NOM', ZIEL_SENSE,                'type_285118'),
    ('SUB1_24020_7',       'haussenpleter', 'lemma_49714', 'NOM', ZIEL_SENSE,                'type_285118'),
    ('SUB1_61070_8',       'hausenpletter', 'lemma_49714', 'NOM', ZIEL_SENSE,                'type_285717'),
]

REVISION = ('<change when="2026-09-10" who="#editor">#363 Hausenblase: {n} Tokens '
            'der Konstruktion hûsenblâter (zusammen- und getrennt geschrieben) '
            'auf lemma_49714 hûsenblâter vereinheitlicht (lemmaRef/pos/ana/corresp; '
            'Mehrwort-Einheit nach TEI-MODEL.md §4.1a; editorische Entscheidung KZW '
            'in #363; Provenienz-Log: ingest/pos-disambig/363-hausenblase/).</change>')


def frag(value):
    if not value:
        return None
    return value.split()[0].split('#', 1)[-1]


def scan():
    """Korpus einmal lesen: Ziel-Tokens einsammeln, Typ-Nutzung zaehlen."""
    ist = {}
    typ_traeger = defaultdict(list)
    ziel_ids = {row[0] for row in IST}
    for fp in corpus_files():
        tree = etree.parse(str(fp))
        for w in tree.iter(f'{TEI}w'):
            wid = w.get(XMLID)
            corresp = w.get('corresp')
            if corresp:
                for tok in corresp.split():
                    if tok.startswith('variants.xml#'):
                        typ_traeger[tok.split('#', 1)[1]].append(wid)
            if wid in ziel_ids:
                ist[wid] = (fp.name, ''.join(w.itertext()).strip(),
                            frag(w.get('lemmaRef')), w.get('pos'),
                            frag(w.get('ana')), frag(corresp))
    return ist, typ_traeger


def typ_plan(ist, typ_traeger):
    """Pro Form entscheiden: Bestands-Typ weiterverwenden oder neu praegen."""
    ziel_ids = {row[0] for row in IST}
    form_typen = {}          # Form -> Bestands-Typ (sofern alle Traeger in der Menge)
    formen_neu = set()
    for wid, form, _l, _p, _a, corresp in ((r[0], r[1], r[2], r[3], r[4], r[5]) for r in IST):
        if corresp is None:
            formen_neu.add(form)
            continue
        fremd = [t for t in typ_traeger.get(corresp, []) if t not in ziel_ids]
        if fremd:
            formen_neu.add(form)
        else:
            vorher = form_typen.get(form)
            if vorher is not None and vorher != corresp:
                sys.exit(f'ABBRUCH: Form {form!r} traegt zwei exklusive Typen '
                         f'({vorher}, {corresp}); das Skript kennt dafuer keine Regel.')
            form_typen[form] = corresp
    # Eine Form, die irgendwo einen fremd belegten Typ traegt, bekommt ueberall
    # eine neue ID: sonst haette dieselbe Schreibung unter demselben Lemma zwei
    # Typen, und variants.xml wuerde beide fuehren.
    for form in list(form_typen):
        if form in formen_neu:
            del form_typen[form]
    neu = {}
    for i, form in enumerate(sorted(formen_neu)):
        neu[form] = f'type_{NEXT_TYPE_ID + i}'
    return form_typen, neu


def main():
    print(f'Scanne {len(corpus_files())} Korpusdateien...')
    ist, typ_traeger = scan()

    fehler = []
    for wid, form, lem, pos, ana, corresp in IST:
        if wid not in ist:
            fehler.append(f'{wid}: nicht im Korpus gefunden')
            continue
        _datei, ist_form, ist_lem, ist_pos, ist_ana, ist_corresp = ist[wid]
        soll = (form, lem, pos, ana, corresp)
        habe = (ist_form, ist_lem, ist_pos, ist_ana, ist_corresp)
        if soll != habe:
            fehler.append(f'{wid}: erwartet {soll}, gefunden {habe}')
    if fehler:
        print('ABBRUCH, Ist-Zustand weicht ab:')
        for f in fehler:
            print(f'   {f}')
        return 1

    weiter, neu = typ_plan(ist, typ_traeger)
    print()
    print('Typ-Zuordnung:')
    for form in sorted(set(list(weiter) + list(neu))):
        if form in weiter:
            n = len(typ_traeger.get(weiter[form], []))
            print(f'   {form:16} weiter  {weiter[form]:14} (korpusweit {n} Tokens, alle in dieser Menge)')
        else:
            print(f'   {form:16} NEU     {neu[form]}')

    # Zuordnung Token -> Zieltyp
    zieltyp = {}
    for wid, form, *_ in IST:
        zieltyp[wid] = weiter.get(form) or neu[form]

    # --- Korpus schreiben ---
    je_datei = defaultdict(list)
    for wid, form, lem, pos, ana, corresp in IST:
        je_datei[ist[wid][0]].append((wid, form, lem, pos, ana, corresp))

    geaendert = 0
    for dateiname, rows in sorted(je_datei.items()):
        fp = ROOT / 'tei' / dateiname
        with open(fp, encoding='utf-8', newline='') as fh:
            text = fh.read()
        for wid, form, lem, pos, ana, corresp in rows:
            attrs = [f'xml:id="{wid}"']
            if lem:
                attrs.append(f'lemmaRef="lexicon.xml#{lem}"')
            if pos:
                attrs.append(f'pos="{pos}"')
            if ana:
                attrs.append(f'ana="lexicon.xml#{ana}"')
            if corresp:
                attrs.append(f'corresp="variants.xml#{corresp}"')
            alt = f'<w {" ".join(attrs)}>{form}</w>'
            if text.count(alt) != 1:
                sys.exit(f'ABBRUCH: {wid} kommt {text.count(alt)}x als Text vor: {alt}')
            neu_tag = (f'<w xml:id="{wid}" lemmaRef="lexicon.xml#{ZIEL_LEMMA}" '
                       f'pos="{ZIEL_POS}" ana="lexicon.xml#{ZIEL_SENSE}" '
                       f'corresp="variants.xml#{zieltyp[wid]}">{form}</w>')
            text = text.replace(alt, neu_tag)
            geaendert += 1
        eintrag = REVISION.format(n=len(rows))
        m = re.search(r'([ \t]*)(<change when="[^"]*" who="#editor">(?:(?!</change>).)*</change>)\s*\n(\s*)</revisionDesc>',
                      text, re.S)
        if not m:
            sys.exit(f'ABBRUCH: kein revisionDesc-Anker in {dateiname}')
        text = text[:m.end(2)] + '\n' + m.group(1) + eintrag + text[m.end(2):]
        if APPLY:
            with open(fp, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
        print(f'   {dateiname}: {len(rows)} Tokens' + ('' if APPLY else ' (Trockenlauf)'))

    # --- lexicon.xml ---
    lex = ROOT / 'authority-files' / 'lexicon.xml'
    with open(lex, encoding='utf-8', newline='') as fh:
        ltext = fh.read()

    # 1. lemma_27031 loeschen
    m = re.search(r'[ \t]*<entry xml:id="lemma_27031">.*?</entry>\n', ltext, re.S)
    if not m:
        sys.exit('ABBRUCH: lemma_27031 nicht in lexicon.xml gefunden')
    ltext = ltext[:m.start()] + ltext[m.end():]

    # 2. type_131170 aus lemma_2670_sense_4300 nehmen: die Form haueßenn belegt
    #    den hasen nach dieser Korrektur nicht mehr.
    m = re.search(r'(<sense xml:id="lemma_2670_sense_4300" ana=")([^"]*)(")', ltext)
    if not m:
        sys.exit('ABBRUCH: lemma_2670_sense_4300 nicht gefunden')
    typen = [t for t in m.group(2).split() if t != '#type_131170']
    if len(typen) != len(m.group(2).split()) - 1:
        sys.exit('ABBRUCH: type_131170 stand nicht in lemma_2670_sense_4300')
    ltext = ltext[:m.start(2)] + ' '.join(typen) + ltext[m.end(2):]

    # 3. lemma_49714_sense_78649 um alle Typen erweitern, die den Sense jetzt
    #    belegen. Die Reihenfolge folgt der Bestandsordnung dieser Datei:
    #    alphabetisch nach der ID als Zeichenkette, nicht numerisch.
    alle_typen = sorted({f'#{t}' for t in zieltyp.values()})
    m = re.search(r'(<sense xml:id="lemma_49714_sense_78649" ana=")([^"]*)(")', ltext)
    if not m:
        sys.exit('ABBRUCH: lemma_49714_sense_78649 nicht gefunden')
    vorhanden = set(m.group(2).split())
    zusammen = sorted(vorhanden | set(alle_typen))
    ltext = ltext[:m.start(2)] + ' '.join(zusammen) + ltext[m.end(2):]

    if APPLY:
        with open(lex, 'w', encoding='utf-8', newline='') as fh:
            fh.write(ltext)

    print()
    print(f'lexicon.xml: lemma_27031 geloescht, type_131170 aus lemma_2670_sense_4300 entfernt,')
    print(f'             lemma_49714_sense_78649 auf {len(zusammen)} Typen erweitert'
          + ('' if APPLY else ' (Trockenlauf)'))
    print()
    print(f'Tokens geaendert: {geaendert}')
    print(f'Neue Typen: {len(neu)} ({NEXT_TYPE_ID}..{NEXT_TYPE_ID + len(neu) - 1})')
    if not APPLY:
        print('\nTrockenlauf. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
