"""Sucht je Eintrag die Anker der Vorstufe, die im uebernommenen Kommentar fehlen.

Anker sind (1) Zitate in Anfuehrungszeichen (ab 12 Zeichen, normalisiert),
(2) Zahlen ab drei Stellen und (3) Eigennamen mitten im Satz. Wer ein Zitat,
eine Zahl oder einen Namen streicht, streicht in aller Regel einen Beleg oder
eine Sachaussage; Umformulierungen verlieren dagegen keinen Anker. Die Ausgabe
ist Arbeitsmaterial fuer die Einordnung (a/b/c), keine Entscheidung.

Aufruf (aus der Repositoriumswurzel):
    python -X utf8 -E -P scripts/ingest/glossar-554/anker-fehlen.py <gmh189c.json> [glossar_id ...]
"""
import glob
import json
import re
import sys


def lade_kommentare():
    alle = {}
    for pfad in sorted(glob.glob('ingest/glossar-554/kommentare/*.json')):
        alle.update(json.load(open(pfad, encoding='utf-8')))
    return alle


def norm(s):
    s = s.lower()
    s = re.sub(r'[^\w\s]', ' ', s)
    return ' '.join(s.split())


def anker(text):
    zitate = [m.group(1) for m in re.finditer(r'[„"‚]([^„“"‘’]{12,}?)[“"‘’]', text)]
    zahlen = re.findall(r'\b\d{3,}\b', text)
    namen = re.findall(r'(?<=[a-zäöüß,;(] )([A-ZÄÖÜ][a-zäöüß]{3,})', text)
    return zitate, zahlen, namen


def main():
    vor = {o['id']: o for o in json.load(open(sys.argv[1], encoding='utf-8'))}
    kom = lade_kommentare()
    ids = sys.argv[2:] or sorted(kom, key=int)
    for gid in ids:
        k = kom[gid]
        if k.get('aufgegangen_in'):
            continue
        o = vor[gid]
        quelle = o['enz_t'] + ('\n\n' + o['poet_t'] if k.get('poet') == 'uebernommen' else '')
        neu = norm(k['text'])
        zit, zah, nam = anker(quelle)
        fz = []
        for z in zit:
            n = norm(z)
            if len(n) >= 10 and n not in neu and n[:25] not in neu:
                fz.append(z)
        fzah = sorted({z for z in zah if z not in k['text']})
        fnam = sorted({n for n in nam if n not in k['text']})
        print('===== %s %s | Zitate fehlen %d/%d, Zahlen fehlen %d/%d, Namen fehlen %d/%d' % (
            gid, o['title'], len(fz), len(zit), len(fzah), len(set(zah)), len(fnam), len(set(nam))))
        for z in fz:
            print('  Z: %s' % z[:300].replace('\n', ' '))
        if fzah:
            print('  N: %s' % ', '.join(fzah))
        if fnam:
            print('  E: %s' % ', '.join(fnam))


main()
