"""Prueft die Kommentartexte in ingest/glossar-554/kommentare/*.json gegen zuordnung.tsv.

Meldet: fehlende und ueberzaehlige Eintraege, Mehrfachbelegung einer Bedeutung,
Zeichenlaenge (neu / Vorstufe) je Eintrag, unerlaubte Zeichen (Geviertstrich U+2014,
gerade Anfuehrungszeichen, Zeilenumbrueche im Text).

Aufruf (aus der Repositoriumswurzel):
    python -X utf8 -E -P scripts/ingest/glossar-554/kommentare-pruefen.py <gmh189c.json>
"""
import csv
import glob
import json
import sys

EM = chr(0x2014)


def lade_kommentare(ordner='ingest/glossar-554/kommentare'):
    alle = {}
    for pfad in sorted(glob.glob(ordner + '/*.json')):
        with open(pfad, encoding='utf-8') as f:
            d = json.load(f)
        for k, v in d.items():
            if k in alle:
                sys.exit('Doppelter Schluessel %s in %s' % (k, pfad))
            alle[k] = v
    return alle


def main():
    vorstufe = {o['id']: o for o in json.load(open(sys.argv[1], encoding='utf-8'))}
    zuordnung = [r for r in csv.DictReader(
        open('ingest/glossar-554/zuordnung.tsv', encoding='utf-8'), delimiter='\t')
        if r['ausgang'] == 'zugeordnet']
    soll = {r['glossar_id'] for r in zuordnung}
    kom = lade_kommentare()
    fehlt = sorted(soll - set(kom), key=int)
    zuviel = sorted(set(kom) - soll, key=int)
    print('zugeordnet laut zuordnung.tsv: %d' % len(soll))
    print('Kommentare vorhanden: %d' % len(kom))
    print('fehlen: %s' % fehlt)
    print('ueberzaehlig: %s' % zuviel)
    fehler = 0
    summe_neu = summe_alt = 0
    for gid in sorted(kom, key=int):
        k = kom[gid]
        t = k['text']
        o = vorstufe[gid]
        alt = len(o['enz_t']) + (len(o['poet_t']) if k.get('poet') == 'uebernommen' else 0)
        if k.get('aufgegangen_in'):
            if t:
                print('FEHLER %s aufgegangen, aber Text vorhanden' % gid)
                fehler += 1
            continue
        if not t:
            print('FEHLER %s leerer Text' % gid)
            fehler += 1
        if EM in t:
            print('FEHLER %s Geviertstrich' % gid)
            fehler += 1
        if '"' in t:
            print('FEHLER %s gerades Anfuehrungszeichen' % gid)
            fehler += 1
        if '\n' in t:
            print('FEHLER %s Zeilenumbruch' % gid)
            fehler += 1
        summe_neu += len(t)
        summe_alt += alt
    print('Zeichen neu %d, Vorstufe (Enz + uebernommene Poet) %d' % (summe_neu, summe_alt))
    sys.exit(1 if (fehler or fehlt or zuviel) else 0)


main()
