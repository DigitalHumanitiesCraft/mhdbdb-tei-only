#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#370 Punkt 2: entscheidungen.csv aus Evidenz und Urteilen.

Eingaben (in ingest/wzb/370-corresp/):
- evidenz.json           von collect-370-evidence.py, eine Zeile je Paar
- urteile-manuell.csv    die von Hand gelesenen und begruendeten Urteile

Ausgaben:
- entscheidungen.csv     genau eine Zeile je Paar aus offene-faelle.csv,
                         Spalten schreibung;lemma;tokens;entscheidung;begruendung;quellen
- abc-befunde.csv        die Paare unter lemma_2 abc mit meinem Zielvorschlag
- entscheidungen-zaehlung.txt  die Zaehlung je Entscheidung mit Nenner
- stichprobe.txt         die fuer die Gegenprobe gezogenen Paare (Seed steht darin)

Mit --nachtrag dasselbe fuer die Paare, die seit dem 31.08. dazugekommen sind
(offene-faelle-nachtrag.csv, evidenz-nachtrag.json, urteile-nachtrag.csv ->
entscheidungen-nachtrag.csv).

Festlegungen der Koordination vom 02.10.2026, die hier gelten:
- ANDERE_ZUORDNUNG wendet dieser Lauf nicht an: ein Urteil dieser Art wird zu
  PRUEFSEITE, das Ziel steht als KI-Vorschlag in der Begruendung.
- lemma_2 abc wird nicht bearbeitet (KZW, #228, 11.09.): jedes Paar darunter
  bekommt NICHT_ANLEGEN, der Befund steht in abc-befunde.csv.

Jedes Paar, das nicht in den Urteilen steht, wird so behandelt: gibt es unter dem
Lemma schon einen Typ mit derselben Schreibung (variants.xml), bekommt es
VERKNUEPFEN ("Typ existiert, nur @corresp setzen", ein Punkt-1-Fall). Sonst bekommt
es ANLEGEN mit einer aus der Evidenz zusammengesetzten Begruendung, die den
Kontext nennt. Das ist beim Nachtrag KEINE Lesung jedes Falls: dort steht nur,
was die Evidenz hergibt, und die Kontexte wurden einmal durchgesehen.

Defensiv: ein Urteil ohne Paar, ein doppeltes Urteil, ein unbekannter
Entscheidungswert oder ein Ziellemma, das es im Lexikon nicht gibt, sind harte
Fehler.

Aufruf aus dem Repo-Wurzelverzeichnis:
    python scripts/review/build-370-entscheidungen.py [--nachtrag]
"""

import argparse
import csv
import difflib
import json
import random
import sys
import unicodedata
from collections import Counter
from pathlib import Path

from lxml import etree

TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
ROOT = Path(__file__).resolve().parent.parent.parent
DIR = ROOT / 'ingest' / 'wzb' / '370-corresp'

# Stellenangaben aus der Wörterbuchnetz-API (bookref = Band, Spalte, Zeile),
# am 02.10.2026 abgefragt: GET /open-api/dictionaries/{sigle}/lemmata/{form}
QUELLEN = {
    'LEXER:meiligen': ('Lexer Bd. 1, Sp. 2077, meiligen swv. (beflecken, beschmutzen) und meilen swv. (dasselbe): '
                       'https://woerterbuchnetz.de/?sigle=Lexer&lemid=M00970 und '
                       'https://woerterbuchnetz.de/?sigle=Lexer&lemid=M00971'),
    'LEXER:gehaere': 'Lexer Bd. 1, Sp. 784, ge-hære stn. (Sammelbildung zu hâr): https://woerterbuchnetz.de/?sigle=Lexer&lemid=G01036',
    'LEXER:enphinden': 'Lexer Bd. 1, Sp. 564, enphinden stv.: https://woerterbuchnetz.de/?sigle=Lexer&lemid=E01066',
}
WERTE = ('ANLEGEN', 'NICHT_ANLEGEN', 'PRUEFSEITE', 'VERKNUEPFEN')
STICHPROBE = 30
SEED = 20261002
ABC = 'lemma_2'
ABC_GRUND = 'lemma_2 abc: eigenes Thema (KZW, #228, 11.09.), in diesem Lauf nicht bearbeitet.'


def lade_csv(pfad):
    with open(pfad, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def lemma_ids():
    ids = set()
    for _, el in etree.iterparse(str(ROOT / 'authority-files' / 'lexicon.xml'),
                                 events=('end',), tag=TEI + 'entry'):
        ids.add(el.get(XMLID))
        el.clear()
    return ids


def lade_vorhandene_typen():
    """(Schreibung NFC klein, Lemma) -> xml:id des Typs in variants.xml."""
    typen = {}
    for _, el in etree.iterparse(str(ROOT / 'authority-files' / 'variants.xml'),
                                 events=('end',), tag=TEI + 'entry'):
        corresp = el.get('corresp') or ''
        if len(corresp.split()) != 1 or corresp.count('#') != 1:
            raise SystemExit('mehrwertiger oder fehlender corresp an einem variants-Eintrag, '
                             'Schluessel waere mehrdeutig: %r' % corresp)
        lem = corresp.split('#')[1]
        for f in el.iterfind(TEI + 'form'):
            if f.text:
                typen.setdefault((unicodedata.normalize('NFC', f.text).lower(), lem), f.get(XMLID))
        el.clear()
    return typen


def graphie_unterschied(a, b):
    """Kurze Beschreibung, was sich zwischen zwei Schreibungen aendert."""
    teile = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b).get_opcodes():
        if tag == 'equal':
            continue
        teile.append('{}/{}'.format(a[i1:i2] or '-', b[j1:j2] or '-'))
    return ', '.join(teile[:4])


def lemma_label(info, lemma):
    if not info:
        return lemma
    pos = ','.join(str(p) for p in info['pos'])
    return '{} {} ({})'.format(lemma, info['orth'], pos)


def kontext(beleg):
    return "{} [{}] {}".format(beleg['vor'][-35:], beleg['tok'], beleg['nach'][:35]).strip()


def auto_begruendung(e):
    bl = e['belege']
    kopf = '[klar] Entschieden an den Belegen: Lemma {} passt'.format(lemma_label(e['lemma_info'], e['lemma']))
    if bl:
        kopf += " in '{}' ({})".format(kontext(bl[0]), bl[0]['id'])
        if len(bl) > 1:
            kopf += " und in '{}' ({})".format(kontext(bl[-1]), bl[-1]['id'])
    teile = [kopf + '.']
    if e['varianten_aehnlich']:
        v = e['varianten_aehnlich'][0]
        teile.append("Nächste vorhandene Variante desselben Lemmas: '{}' (Unterschied {}).".format(
            v, graphie_unterschied(e['form'], v) or 'keiner'))
    if e['heute_lage'] == 'anderes':
        andere = {l: n for l, n in e['norm_korpus'].items() if l != e['lemma']}
        top = max(andere.items(), key=lambda t: t[1])
        teile.append(
            'Die normalisierte Form löst heute auf {} auf ({} Belege im Korpus); '
            'beide bleiben Kandidaten, die Reihenfolge regelt Vorschrift B aus #378.'.format(
                lemma_label(e['heute_lemma_info'], e['heute_aufgeloest']), top[1]))
    elif e['heute_lage'] == 'richtig':
        teile.append('Die normalisierte Form löst heute schon auf dieses Lemma auf; der Typ hält die Schreibung fest.')
    return ' '.join(teile)


def belege_quelle(e, extra):
    ids = ', '.join(b['id'] for b in e['belege'][:3])
    teile = ['WZB-Belege (insgesamt {}): {}'.format(len(e['belege']), ids)]
    for k in (extra or '').split(' | '):
        k = k.strip()
        if k:
            teile.append(QUELLEN.get(k, k))
    teile.append('authority-files/variants.xml und lexicon.xml (Stand des Laufs)')
    return ' | '.join(teile)


def pruefe_urteile(urteile, ev, lex):
    uv = {}
    for u in urteile:
        k = (u['form'], u['lemma'])
        if k not in ev:
            sys.exit('Urteil ohne Paar: {}'.format(k))
        if k in uv:
            sys.exit('Doppeltes Urteil: {}'.format(k))
        ent = u['entscheidung']
        if ent not in WERTE and not ent.startswith('ANDERE_ZUORDNUNG:lemma_'):
            sys.exit('Unbekannter Entscheidungswert {} bei {}'.format(ent, k))
        if ent.startswith('ANDERE_ZUORDNUNG:'):
            ziel = ent.split(':', 1)[1]
            if ziel not in lex:
                sys.exit('Ziellemma {} bei {} gibt es im Lexikon nicht'.format(ziel, k))
            if ziel == u['lemma']:
                sys.exit('ANDERE_ZUORDNUNG auf das eigene Lemma bei {}'.format(k))
        if not u['begruendung'].strip():
            sys.exit('Urteil ohne Begründung: {}'.format(k))
        if ent == 'PRUEFSEITE' and not (u['vorschlag'].strip() and u['unsicher_weil'].strip()):
            sys.exit('PRUEFSEITE ohne Vorschlag oder Unsicherheitsgrund: {}'.format(k))
        uv[k] = u
    return uv


def main():
    ap = argparse.ArgumentParser(description='#370: entscheidungen.csv bauen.')
    ap.add_argument('--nachtrag', action='store_true',
                    help='die Paare seit dem 31.08. statt der 484 der Arbeitsliste')
    args = ap.parse_args()
    suffix = '-nachtrag' if args.nachtrag else ''

    paare = lade_csv(DIR / ('offene-faelle-nachtrag.csv' if args.nachtrag else 'offene-faelle.csv'))
    evidenz = json.load(open(DIR / ('evidenz-nachtrag.json' if args.nachtrag else 'evidenz.json'), encoding='utf-8'))
    urteile = lade_csv(DIR / ('urteile-nachtrag.csv' if args.nachtrag else 'urteile-manuell.csv'))
    lex = lemma_ids()

    if len(evidenz) != len(paare):
        sys.exit('Evidenz ({}) und Arbeitsliste ({}) haben verschiedene Länge'.format(len(evidenz), len(paare)))
    ev = {}
    for p, e in zip(paare, evidenz):
        if (p['form_schluessel'], p['lemma']) != (e['form'], e['lemma']):
            sys.exit('Reihenfolge weicht ab bei {}'.format(p['form_schluessel']))
        ev[(e['form'], e['lemma'])] = e
    uv = pruefe_urteile(urteile, ev, lex)

    zeilen = []
    abc = []
    auto_keys = []
    pruef_keys = []
    nur_verknuepfen = []
    vorhanden = lade_vorhandene_typen()
    zaehl = Counter()
    zaehl_tok = Counter()
    handarbeit = 0
    for p, e in zip(paare, evidenz):
        k = (e['form'], e['lemma'])
        u = uv.get(k)
        quellen = ''
        if u:
            ent, beg, quellen = u['entscheidung'], u['begruendung'].strip(), u['quellen_extra']
            handarbeit += 1
            if e['lemma'] == ABC:
                ziel = ent.split(':', 1)[1] if ent.startswith('ANDERE_ZUORDNUNG:') else ''
                bl = e['belege']
                abc.append([e['form'], e['lemma'], e['tokens'], ziel, beg,
                            "'{}' ({})".format(kontext(bl[0]), bl[0]['id']) if bl else '',
                            QUELLEN.get(quellen, quellen) or 'WZB-Belege, Lexikonsuche in lexicon.xml'])
                ent = 'NICHT_ANLEGEN'
                beg = "{} Beleg: '{}' ({}). Befund und Zielvorschlag: abc-befunde.csv.".format(
                    ABC_GRUND, kontext(bl[0]), bl[0]['id'])
            elif ent.startswith('ANDERE_ZUORDNUNG:'):
                ziel = ent.split(':', 1)[1]
                beg = '[KI-Vorschlag: ANDERE_ZUORDNUNG:{}] {} Eine Änderung von @lemmaRef wendet dieser Lauf nicht an, ' \
                      'die Entscheidung liegt bei der Prüfseite.'.format(ziel, beg)
                ent = 'PRUEFSEITE'
            if ent == 'PRUEFSEITE':
                pruef_keys.append(k)
        elif k in vorhanden:
            # Der Typ gibt es schon: kein neuer Typ, die Tokens sind nur zu verknüpfen (Punkt 1)
            bl = e['belege']
            ent = 'VERKNUEPFEN'
            beg = ("Der Typ existiert schon: {} unter {} (variants.xml). Kein neuer Typ; die Tokens ohne @corresp "
                   "sind mit diesem Typ zu verknüpfen (Punkt 1). Kontext: '{}' ({}).").format(
                       vorhanden[k], lemma_label(e['lemma_info'], e['lemma']),
                       kontext(bl[0]) if bl else '', bl[0]['id'] if bl else '')
            nur_verknuepfen.append(k)
        else:
            ent, beg = 'ANLEGEN', auto_begruendung(e)
            auto_keys.append(k)
        zaehl[ent] += 1
        zaehl_tok[ent] += e['tokens']
        zeilen.append([e['form'], e['lemma'], e['tokens'], ent, beg, belege_quelle(e, quellen)])

    with open(DIR / ('entscheidungen%s.csv' % suffix), 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f, delimiter=';', lineterminator='\n')
        w.writerow(['schreibung', 'lemma', 'tokens', 'entscheidung', 'begruendung', 'quellen'])
        w.writerows(zeilen)
    if abc:
        with open(DIR / 'abc-befunde.csv', 'w', encoding='utf-8-sig', newline='') as f:
            w = csv.writer(f, delimiter=';', lineterminator='\n')
            w.writerow(['schreibung', 'lemma', 'tokens', 'vorgeschlagenes_ziel', 'befund', 'beleg', 'quelle'])
            w.writerows(abc)

    n = len(zeilen)
    t = sum(z[2] for z in zeilen)
    txt = ['Entscheidungen #370 Punkt 2{}, {} Paare, {} Tokens'.format(' (Nachtrag)' if args.nachtrag else '', n, t)]
    for art in ('ANLEGEN', 'VERKNUEPFEN', 'NICHT_ANLEGEN', 'PRUEFSEITE'):
        txt.append('{}: {} von {} Paaren ({:.1f} %), {} von {} Tokens'.format(
            art, zaehl[art], n, 100 * zaehl[art] / n if n else 0, zaehl_tok[art], t))
    txt.append('davon von Hand begründet: {} von {} Paaren, mit Kontext aus der Evidenz zusammengesetzt: {}'.format(
        handarbeit, n, n - handarbeit))
    txt.append('VERKNUEPFEN, weil der Typ unter dem Lemma schon existiert: {} von {} Paaren, {} Tokens'.format(
        len(nur_verknuepfen), n, sum(ev[k]['tokens'] for k in nur_verknuepfen)))
    belegt = sum(len(e['belege']) for e in evidenz)
    txt.append('Tokens ohne @corresp bei diesen Paaren am heutigen Korpusstand: {} (Spalte tokens: {}; '
               'Soll für Spur A ist die heutige Zahl)'.format(belegt, t))
    if abc:
        txt.append('lemma_2 abc: {} Paare (NICHT_ANLEGEN), davon {} mit Zielvorschlag in abc-befunde.csv'.format(
            len(abc), sum(1 for a in abc if a[3])))
    text = '\n'.join(txt)
    (DIR / ('entscheidungen-zaehlung%s.txt' % suffix)).write_text(text + '\n', encoding='utf-8')
    print(text)

    rng = random.Random(SEED)
    ziehung = rng.sample(sorted(auto_keys), min(STICHPROBE, len(auto_keys)))
    st = ['Stichprobe für die Gegenprobe am Beleg, Seed {} (random.Random({}).sample(sorted(Paare), {}))'.format(
        SEED, SEED, STICHPROBE),
        'Gezogen aus den {} Paaren mit zusammengesetzter Begründung, dazu alle {} Paare auf der Prüfseite.'.format(
            len(auto_keys), len(pruef_keys)), '', 'Zufällig gezogen:']
    st += ['  {} {}'.format(a, b) for a, b in sorted(ziehung)]
    st += ['', 'Prüfseite:'] + ['  {} {}'.format(a, b) for a, b in sorted(pruef_keys)]
    (DIR / ('stichprobe%s.txt' % suffix)).write_text('\n'.join(st) + '\n', encoding='utf-8')


if __name__ == '__main__':
    main()
