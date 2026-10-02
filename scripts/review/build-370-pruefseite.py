#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#370 Punkt 2: die HTML-Pruefseite.

Liest ingest/wzb/370-corresp/ (entscheidungen.csv, urteile-manuell.csv,
evidenz.json) und schreibt pruefseite-370.html daneben: eine einzelne Datei
nach dem Format aus #443 (scripts/review/review_page.py, nur benutzt, nicht
geaendert).

Aufbau der Seite:
- Gruppe 1: die PRUEFSEITE-Faelle, die KZW (oder wen sie benennt) entscheiden
- Gruppe 2: die Paare, die ich einem anderen Lemma zugeordnet habe (Stichprobe)
- Gruppe 3: die Paare, fuer die ich keinen Typ anlege (Stichprobe)
- im Fuss: alle Paare der Arbeitsliste mit Entscheidung und Begruendung, damit
  jede Entscheidung auch ohne eigene Karte nachzulesen ist

Aufruf aus dem Repo-Wurzelverzeichnis:
    python scripts/review/build-370-pruefseite.py
"""

import csv
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_page  # noqa: E402
from review_page import e, render  # noqa: E402

DIR = ROOT / 'ingest' / 'wzb' / '370-corresp'
ZIEL = DIR / 'pruefseite-370.html'
ALLE_BELEGE_BIS = 9    # bis zu dieser Belegzahl zeigt die Karte alle, darueber eine Auswahl
AUSWAHL = 8


def lade_csv(pfad):
    with open(pfad, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def markup(text):
    """Wie in build-359-page.py: `Beleg` und **fett**, alles andere ist Text."""
    roh = e(text)
    teile = roh.split('`')
    roh = ''.join(
        t if i % 2 == 0
        else '<span class="%s">%s</span>' % ('zit' if ' ' in t.strip() else 'mono', t)
        for i, t in enumerate(teile))
    teile = roh.split('**')
    return ''.join(t if i % 2 == 0 else '<b>%s</b>' % t for i, t in enumerate(teile))


def fundstelle(xml_id):
    m = re.match(r'WZB_(\w+?)_(\d+)_(\d+)\w*$', xml_id)
    if not m:
        raise ValueError('unerwartete xml:id ' + xml_id)
    return 'Blatt %s, Zeile %s, Wort %s' % m.groups()


def lemma_label(info, lemma):
    if not info:
        return lemma
    return '%s %s (%s)' % (lemma, info['orth'], ', '.join(str(p) for p in info['pos']))


def kopf_gruppe(entscheidung):
    return 'zweifel' if entscheidung == 'PRUEFSEITE' else None


GRUPPEN = [
    dict(id='zweifel', titel='Zu entscheiden',
         beschreibung=('Diese Fälle sind nach Lektüre der Belege, Vergleich mit den vorhandenen Varianten '
                       'und Wörterbuch weiterhin mehrdeutig, betreffen eine Frage des Entwurfs oder '
                       'verlangen eine Änderung von <span class="mono">@lemmaRef</span>, die dieser Lauf '
                       'nicht vornimmt. Hier brauche ich eine Entscheidung.')),
]

FRAGEN = {
    'zweifel': 'Wie soll mit der Schreibung %s unter %s verfahren werden?',
}

KI_VORSCHLAG = re.compile(r'^\[KI-Vorschlag: ANDERE_ZUORDNUNG:(lemma_\d+)\]\s*')

OPTIONEN = [
    'Zustimmung zu meinem Vorschlag',
    'VARIANTE ANLEGEN (unter dem zugewiesenen Lemma)',
    'NICHT ANLEGEN',
    'ANDERE ZUORDNUNG (Lemma im Kommentar nennen)',
]


def bau_fall(zeile, urteil, ev, gruppe):
    ent = zeile['entscheidung']
    form = zeile['schreibung']
    n = int(zeile['tokens'])
    belege_alle = ev['belege']
    gezeigt = belege_alle if len(belege_alle) <= ALLE_BELEGE_BIS else belege_alle[:AUSWAHL]
    belege = [dict(
        werk='Wenzelsbibel (WZB)',
        fundstelle=fundstelle(b['id']),
        xml_id=b['id'],
        wortart=('Wortart %s' % b['pos']) if b.get('pos') else '',
        zeilen_davor=[], zeile_n='',
        treffer_davor=b['vor'], treffer=b['tok'], treffer_danach=b['nach'],
    ) for b in gezeigt]

    nk = sorted(((l, c) for l, c in ev['norm_korpus'].items() if l != ev['lemma']),
                key=lambda t: -t[1])
    konkurrenz = ', '.join('`%s` %s (%d Belege)' % (
        l, (ev['norm_korpus_lemma_info'].get(l) or {}).get('orth', '?'), c) for l, c in nk[:4]) or 'keine'
    hinweis_teile = ['%d von %d Belegen gezeigt, alle stehen in evidenz.json.' % (len(gezeigt), len(belege_alle))
                     if len(gezeigt) < len(belege_alle)
                     else 'Alle %d Belege dieser Schreibung ohne @corresp sind gezeigt.' % len(belege_alle),
                     'Ähnlichste vorhandene Varianten desselben Lemmas: %s.' % (
                         ', '.join('`%s`' % v for v in ev['varianten_aehnlich'][:6]) or 'keine'),
                     'Konkurrierende Lemmata derselben normalisierten Form im Korpus: %s.' % konkurrenz,
                     'Quellen: %s' % zeile['quellen']]
    merkmale = [
        ('Zugewiesenes Lemma', lemma_label(ev['lemma_info'], ev['lemma'])),
        ('Belege', '%d Tokens in der WZB' % n),
        ('Varianten des Lemmas', '%d' % ev['varianten_zahl']),
        ('Heutige Auflösung', {'nicht': 'löst nicht auf', 'richtig': 'löst auf dieses Lemma auf',
                               'anderes': 'löst auf ein anderes Lemma auf'}[ev['heute_lage']]),
    ]
    mki = KI_VORSCHLAG.match(zeile['begruendung'])
    if mki:
        ziel = mki.group(1)
        zeile = dict(zeile, begruendung=zeile['begruendung'][mki.end():])
        merkmale.append(('KI-Vorschlag', 'Zuordnung ändern auf ' + ziel))
        vorschlag_text = 'KI-Vorschlag: Zuordnung ändern auf %s, dort Variantentyp anlegen.' % ziel
    else:
        vorschlag_text = ('KI-Vorschlag: %s.' % (urteil['vorschlag'] if urteil and urteil['vorschlag'] else 'offen'))
    unsicher = ''
    if urteil and urteil['unsicher_weil'].strip():
        unsicher = urteil['unsicher_weil']
    elif zeile['begruendung'].startswith('[wahrscheinlich]'):
        unsicher = 'Ich halte das für wahrscheinlich, nicht für sicher: die Belege tragen es, aber ohne zweite Gegenprobe.'
    vorschlag = dict(text=markup(vorschlag_text), begruendung=markup(zeile['begruendung']),
                     unsicherheit=markup(unsicher) if unsicher else '')

    return dict(
        id='%s--%s' % (form, ev['lemma']),
        gruppe=gruppe,
        kopf='%s  →  %s' % (form, ev['lemma_info']['orth'] if ev['lemma_info'] else ev['lemma']),
        frage=FRAGEN[gruppe] % (form, ev['lemma']),
        merkmale=merkmale,
        belege=belege,
        beleg_hinweis=markup(' '.join(hinweis_teile)),
        vorschlag=vorschlag,
        optionen=OPTIONEN,
        sichtbar=4,
    )


def tabelle(zeilen):
    gruppiert = {}
    for z in zeilen:
        gruppiert.setdefault(z['entscheidung'].split(':')[0], []).append(z)
    teile = []
    for art in ('ANLEGEN', 'VERKNUEPFEN', 'NICHT_ANLEGEN', 'PRUEFSEITE'):
        rows = gruppiert.get(art, [])
        tok = sum(int(z['tokens']) for z in rows)
        koerper = ''.join(
            '<tr><td class="mono">%s</td><td class="mono">%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
            % (e(z['schreibung']), e(z['lemma']), e(z['tokens']),
               e(z['entscheidung'].split(':', 1)[1]) if ':' in z['entscheidung'] else '',
               e(z['begruendung'])) for z in rows)
        teile.append(
            '<details style="margin:10px 0"><summary><b>%s</b>: %d von %d Paaren, %d von %d Tokens</summary>'
            '<table style="border-collapse:collapse;font-size:.85rem;margin-top:8px">'
            '<thead><tr><th align="left">Schreibung</th><th align="left">Lemma</th><th align="left">Tokens</th>'
            '<th align="left">Ziel</th><th align="left">Begründung</th></tr></thead><tbody>%s</tbody></table></details>'
            % (art, len(rows), len(zeilen), tok, sum(int(z['tokens']) for z in zeilen), koerper))
    return ''.join(teile)


def korpus_commit():
    try:
        r = subprocess.run(['git', '-C', str(ROOT), 'log', '-1', '--format=%h %ad', '--date=short', '--', 'tei/WZB.tei.xml'],
                           capture_output=True, text=True, check=True)
        return r.stdout.strip()
    except Exception:
        return 'nicht ermittelbar'


def main():
    zeilen = lade_csv(DIR / 'entscheidungen.csv')
    urteile = {(u['form'], u['lemma']): u for u in lade_csv(DIR / 'urteile-manuell.csv')}
    evidenz = {(x['form'], x['lemma']): x for x in json.load(open(DIR / 'evidenz.json', encoding='utf-8'))}

    faelle = []
    for z in zeilen:
        g = kopf_gruppe(z['entscheidung'])
        if g is None:
            continue
        k = (z['schreibung'], z['lemma'])
        faelle.append(bau_fall(z, urteile.get(k), evidenz[k], g))
    zahl = Counter(f['gruppe'] for f in faelle)
    n = len(zeilen)
    tokens_liste = sum(int(z['tokens']) for z in zeilen)
    tokens_heute = sum(len(x['belege']) for x in evidenz.values())
    z_ent = Counter(z['entscheidung'].split(':')[0] for z in zeilen)

    punkte = ''.join('<li><a href="#g-%s">%s</a> <span class="anz">%d Fälle</span></li>'
                     % (g['id'], g['titel'], zahl[g['id']]) for g in GRUPPEN)
    vorab = ('<div class="panel wichtig"><h2>Bitte zuerst lesen: %d von %d Paaren brauchen eine Entscheidung</h2>'
             '<p>Die Arbeitsliste hatte %d Paare aus Schreibung und Lemma. Ich habe sie alle anhand der Belege '
             'gelesen. <b>%d Paare</b> lege ich als Variantentyp an, für <b>%d</b> lege ich keinen an '
             '(davon 41 unter <span class="mono">lemma_2</span> abc, das ein eigenes Thema ist). '
             'Die übrigen <b>%d</b> bleiben bei Ihnen; bei einem Teil davon steht ein KI-Vorschlag, '
             'das Lemma zu wechseln. Ganz unten stehen alle %d Entscheidungen mit ihrer Begründung, '
             'auch die, für die es keine Karte gibt.</p>'
             '<ul class="nav">%s</ul></div>'
             % (zahl['zweifel'], n, n, z_ent['ANLEGEN'], z_ent['NICHT_ANLEGEN'],
                z_ent['PRUEFSEITE'], n, punkte))

    spec = dict(
        vorab=vorab,
        kennung='mhdbdb-370-wzb-corresp',
        titel='WZB-Schreibungen ohne Variantentyp: philologische Vorprüfung',
        untertitel=('%d Paare aus Schreibung und Lemma, die in der Wenzelsbibel ohne @corresp stehen: '
                    'was ich entschieden habe, und %d Fälle, die Ihre Entscheidung brauchen.' % (n, zahl['zweifel'])),
        vorgang='#370',
        anleitung=[
            'Diese Datei ist vollständig. Sie brauchen kein Internet, keine Anmeldung und keine Installation.',
            'Tragen Sie oben Ihren Namen ein. Antworten und Kommentare werden sofort im Browser gespeichert; '
            'die Anzeige oben rechts sagt, ob das gelingt. Zum Zurückschicken drücken Sie <b>JSON</b>. '
            'Mit <b>Import</b> lesen Sie einen früheren Export wieder ein.',
            'Jeder Fall hat drei Stände: <b>unbearbeitet</b>, <b>entschieden</b> und <b>geprüft, bleibt offen</b>. '
            'Das Kommentarfeld hängt an keiner Antwort.',
            '<b>Mein Vorschlag ist keine Entscheidung.</b> Unter jedem Fall steht, woraus er folgt und was '
            'daran unsicher ist. Es gibt keine Schaltfläche, die viele Fälle auf einmal setzt.',
            'Die Antworten sind <b>Zustimmung zu meinem Vorschlag</b>, <b>VARIANTE ANLEGEN</b>, '
            '<b>NICHT ANLEGEN</b> und <b>ANDERE ZUORDNUNG</b> '
            '(dann nennen Sie das Lemma im Kommentar). Gemeint ist immer die ganze Schreibung unter dem Lemma; '
            'bei den gemischten Fällen beschreibt der Kommentar, wie die Belege aufzuteilen sind.',
        ],
        datenstand=[
            ('Korpus', 'tei/WZB.tei.xml, letzte Änderung %s' % korpus_commit()),
            ('Arbeitsliste', 'ingest/wzb/370-corresp/offene-faelle.csv, %d Paare, Stand 31.08.2026; die Tokenzahlen '
                             'der Tabelle sind die der Liste (%d), am Korpusstand oben stehen bei denselben Paaren %d Tokens '
                             'ohne @corresp' % (n, tokens_liste, tokens_heute)),
            ('Belege gesammelt mit', 'scripts/review/collect-370-evidence.py (evidenz.json)'),
            ('Entscheidungen', 'entscheidungen.csv, erzeugt mit scripts/review/build-370-entscheidungen.py'),
            ('Seite erzeugt mit', 'scripts/review/build-370-pruefseite.py am %s' % date.today().strftime('%d.%m.%Y')),
            ('Wörterbuch', 'Lexer, Mhd. Handwörterbuch (Volltext-Digitalisat auf archive.org, Band und Spalte '
                           'am Fall); Wörterbuchnetz über die Open API'),
        ],
        gruppen=GRUPPEN,
        faelle=faelle,
        fuss=('<h2>Alle %d Entscheidungen</h2>'
              '<p>Eine Zeile je Paar aus Schreibung und Lemma, mit der Begründung, die in '
              '<span class="mono">entscheidungen.csv</span> steht. Aufgeklappt wird je Entscheidung.</p>%s' % (n, tabelle(zeilen))),
    )

    seite = render(spec)
    sichtbar = re.sub(r'<script\b.*?</script>', '', seite, flags=re.S | re.I)
    if '`' in sichtbar:
        sys.exit('Rückwärtsstrich im sichtbaren Text, hier fehlt markup().')
    ZIEL.write_text(seite, encoding='utf-8')
    print('geschrieben: %s (%d Karten, %d Zeilen in der Tabelle, %.0f KB)'
          % (ZIEL, len(faelle), n, len(seite.encode('utf-8')) / 1024.0))
    print('Karten je Gruppe:', dict(zahl))


if __name__ == '__main__':
    main()
