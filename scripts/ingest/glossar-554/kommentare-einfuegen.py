"""Fuegt die Kommentare aus ingest/glossar-554/kommentare/*.json in authority-files/lexicon.xml ein.

Je zugeordnetem Eintrag (zuordnung.tsv, Ausgang "zugeordnet") entsteht an der
entschiedenen <sense> eine Notiz

    <note type="comment" xml:lang="de" resp="contributors.xml#contrib_003">TEXT Quelle: ...</note>

unmittelbar nach <def> (Schema: def, note, ptr). Nicht eingefuegt werden Eintraege,
die in einordnung.json Teile der Kategorie (c) verloren haben (sie gehen auf die
Pruefseite), und zusammengefuehrte Eintraege ohne eigenen Text.

Die Quellenzeile haengt dieses Skript an, nie von Hand. Text-Einfuegung ohne
Neuserialisierung: der Rest der Datei bleibt Byte fuer Byte erhalten.
Jeder unerwartete Befund ist ein harter Fehler.

Aufruf (aus der Repositoriumswurzel):
    python -X utf8 -E -P scripts/ingest/glossar-554/kommentare-einfuegen.py [--schreiben]
Ohne --schreiben wird nur gezaehlt und geprueft.
"""
import csv
import glob
import json
import re
import sys
from xml.sax.saxutils import escape

LEXIKON = 'authority-files/lexicon.xml'
QUELLE = 'Quelle: Glossar Kochbuchforschung dig_ESTivum von Katharina Zeppezauer-Wachauer (2016-2026)'
RESP = 'contributors.xml#contrib_003'
# Sachliche Rueckfrage auf der Pruefseite (Gruppe D), geht erst nach KZWs Antwort in die Daten:
# 867 grandmangerie nennt Ulrich von dem Tuerlin als Verfasser der Crone (works.xml: Heinrich, person_867).
# Dazu 1905 huon und 2253 rëphuon: ihr Text fasst die Poetisierungsteile von henne (1900) bzw.
# rëphenne (2264) zusammen (Gruppe E); das war mehr als gleicher Text.
RUECKFRAGE = {'867', '1905', '2253'}


def lade_kommentare():
    alle = {}
    for pfad in sorted(glob.glob('ingest/glossar-554/kommentare/*.json')):
        alle.update(json.load(open(pfad, encoding='utf-8')))
    return alle


def main():
    schreiben = '--schreiben' in sys.argv
    kom = lade_kommentare()
    einordnung = json.load(open('ingest/glossar-554/einordnung.json', encoding='utf-8'))
    gekuerzt = {k for k, v in einordnung.items() if not k.startswith('_') and v.get('c')}
    zuordnung = [r for r in csv.DictReader(
        open('ingest/glossar-554/zuordnung.tsv', encoding='utf-8'), delimiter='\t')
        if r['ausgang'] == 'zugeordnet']

    with open(LEXIKON, encoding='utf-8', newline='') as f:
        inhalt = f.read()
    nl = '\r\n' if '\r\n' in inhalt else '\n'
    zeilen = inhalt.split(nl)

    eingefuegt = []
    uebersprungen = {'gekuerzt': [], 'zusammengefuehrt': [], 'rueckfrage': []}
    einfuegungen = []  # (zeilenindex nach dem eingefuegt wird, zeile)
    for r in zuordnung:
        gid = r['glossar_id']
        k = kom[gid]
        if gid in gekuerzt:
            uebersprungen['gekuerzt'].append(gid)
            continue
        if k.get('aufgegangen_in'):
            uebersprungen['zusammengefuehrt'].append(gid)
            continue
        if gid in RUECKFRAGE:
            uebersprungen['rueckfrage'].append(gid)
            continue
        sense_id = r['sense_id']
        muster = '<sense xml:id="%s"' % sense_id
        treffer = [i for i, z in enumerate(zeilen) if muster in z]
        if len(treffer) != 1:
            sys.exit('FEHLER: %s kommt %d-mal vor (Eintrag %s)' % (muster, len(treffer), gid))
        i = treffer[0]
        einzug = re.match(r'\s*', zeilen[i]).group(0)
        # Ende der <sense>: erste Zeile mit </sense>
        ende = next(j for j in range(i, len(zeilen)) if '</sense>' in zeilen[j])
        block = zeilen[i:ende + 1]
        if any('type="comment"' in z for z in block):
            sys.exit('FEHLER: %s traegt schon eine Kommentar-Notiz (Eintrag %s)' % (sense_id, gid))
        defs = [j for j in range(i, ende + 1) if '</def>' in zeilen[j]]
        if len(defs) > 1:
            sys.exit('FEHLER: %s hat mehrere <def> (Eintrag %s)' % (sense_id, gid))
        if defs:
            j = defs[0]
            if '<def' not in zeilen[j]:
                sys.exit('FEHLER: <def> in %s ueber mehrere Zeilen (Eintrag %s)' % (sense_id, gid))
            nach = j
            noteneinzug = re.match(r'\s*', zeilen[j]).group(0)
        else:
            nach = i
            noteneinzug = einzug + '  '
        text = k['text'].strip()
        if not text:
            sys.exit('FEHLER: leerer Text fuer Eintrag %s' % gid)
        zeile = '%s<note type="comment" xml:lang="de" resp="%s">%s %s</note>' % (
            noteneinzug, RESP, escape(text), escape(QUELLE))
        einfuegungen.append((nach, zeile, gid, sense_id))
        eingefuegt.append(gid)

    print('zugeordnet: %d' % len(zuordnung))
    print('einzufuegen: %d' % len(eingefuegt))
    print('uebersprungen gekuerzt (Pruefseite): %d %s' % (len(uebersprungen['gekuerzt']), uebersprungen['gekuerzt']))
    print('uebersprungen zusammengefuehrt: %d %s' % (len(uebersprungen['zusammengefuehrt']), uebersprungen['zusammengefuehrt']))
    print('uebersprungen Rueckfrage (Pruefseite D): %d %s' % (len(uebersprungen['rueckfrage']), uebersprungen['rueckfrage']))
    teile = [len(eingefuegt)] + [len(v) for v in uebersprungen.values()]
    print('Summe: %s = %d' % (' + '.join(str(t) for t in teile), sum(teile)))
    if not schreiben:
        return
    for nach, zeile, gid, sense_id in sorted(einfuegungen, key=lambda t: -t[0]):
        zeilen.insert(nach + 1, zeile)
    with open(LEXIKON, 'w', encoding='utf-8', newline='') as f:
        f.write(nl.join(zeilen))
    print('geschrieben: %s (%d Notizen, Zeilenende %s)' % (LEXIKON, len(einfuegungen), repr(nl)))


main()
