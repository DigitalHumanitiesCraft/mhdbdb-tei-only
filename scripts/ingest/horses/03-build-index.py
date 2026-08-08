#!/usr/bin/env python3
"""#193 Baustein 3: `data/horses-index.json.gz` aus Luise Boreks Auszeichnung.

Quelle: 'Exemplarische Auszeichnung arthurischer Pferde', Luise Borek,
TU Darmstadt, hdl:tudatalib/3695, CC0 1.0, publiziert 2023-01-18. Die Datei
selbst traegt im Header noch 'Veroeffentlichung unter CC-BY-SA wird
angestrebt' und das Datum Januar 2017: das ist der Entwurfsstand, es gilt die
Lizenz des Repositoriums.

## Wie ein Beleg gespeichert wird

Boreks Zitation und unser aufgeloestes Ziel sind ZWEI Angaben, und fuer acht
der 336 Verse fallen sie auseinander. Der Index fuehrt beide:

    citation   'Pz. 339,24'   Boreks Angabe, woertlich, unveraendert
    target     'PZ_33926'     wohin der Sprung in die Leseansicht geht
    match      'shifted'      wie sicher und auf welchem Weg
    score      0.83           gemessene Uebereinstimmung des Wortlauts

Der Grund steht in `mapping.py`: unser Parzival folgt Leitzmann (ATB 12,
7. Aufl. 1961), Borek nennt gar keine Ausgabe. Eine stille Umrechnung auf
unsere Zaehlung waere damit nicht nachpruefbar, denn nachpruefbar ist nur der
Wortlaut. Und Boreks Angabe wegzuwerfen hiesse, die Herkunft der Daten und
die zitierfaehige Referenz zu verlieren (ADR-018). Entschieden am 08.08.2026.

`target` ist der VERSKERN, nicht die erste Wort-ID: bei laufenden
Korpuskorrekturen kann sich das erste `<w>` eines Verses aendern, die Position
des Verses nicht.

## Was der Praezedenzfall sagt

#59 (Naming-Index) hat wegen abweichender Verszaehlung bewusst KEINE
Reader-Deep-Links gebaut, siehe `scripts/ingest/naming/01-fetch-and-build-index.py`.
Hier sind sie vertretbar, aber nur, weil jede einzelne Stelle am Wortlaut
geprueft ist. Ein `target` ohne diese Pruefung waere derselbe Fehler in neuem
Gewand: er traefe still das Falsche.

## Determinismus

Kein Build-Zeitstempel, gzip ohne mtime, `source.sha256` haelt den Quellstand
fest: gleiche Quelle plus gleiches Korpus ergibt einen byte-identischen Index.

Usage:
    python scripts/ingest/horses/03-build-index.py
    python scripts/ingest/horses/03-build-index.py --dry-run   # nur berichten
"""
import argparse
import gzip
import hashlib
import io
import json
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

from lxml import etree  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mapping  # noqa: E402

REPO = mapping.REPO
TEI, XML = mapping.TEI, mapping.XML
ZIEL = REPO / 'data' / 'horses-index.json.gz'

VERSION = '1.0.0'
QUELLE = ('https://tudatalib.ulb.tu-darmstadt.de/server/api/core/bitstreams/'
          'a64fd7c9-9c58-4446-97bd-885577f2b85c/content')
HERKUNFT = {
    'title': 'Exemplarische Auszeichnung arthurischer Pferde',
    'author': 'Luise Borek',
    'handle': 'hdl:tudatalib/3695',
    'url': 'https://tudatalib.ulb.tu-darmstadt.de/handle/tudatalib/3695',
    'licence': 'CC0 1.0',
    'published': '2023-01-18',
}


def text_von(e):
    return re.sub(r'\s+', ' ', ''.join(e.itertext())).strip()


def ref_liste(e, attr='ref'):
    """Boreks Referenzen sind nicht einheitlich notiert: mal mit fuehrendem
    '#', mal ohne (horseName ref='Ingliart'), und ein Attribut kann mehrere
    Ziele tragen ('#Er. #Iw. #Pz.'). Beides hier einsammeln statt an jeder
    Aufrufstelle."""
    return [t.lstrip('#') for t in (e.get(attr) or '').split() if t.strip('#')]


def erste_ref(e, attr='ref'):
    refs = ref_liste(e, attr)
    return refs[0] if refs else None


def _event(e):
    return {'type': e.get('type'),
            **({'subtype': e.get('subtype')} if e.get('subtype') else {})}


def ereignisse(l):
    """Alle Ereignistypen zu diesem Vers, von aussen nach innen.

    Boreks `event` schachtelt sich (6 Faelle), und der innere Typ ist der
    genauere. Ein `event` kann aber auch INNERHALB des Verses stehen statt um
    ihn herum (Pz. 549,7 traegt sein care so). Wer nur die Vorfahren absucht,
    verliert diesen Vers still aus jedem Ereignisfilter.
    """
    ueber, e = [], l.getparent()
    while e is not None and isinstance(e.tag, str):
        if e.tag == TEI + 'event' and e.get('type'):
            ueber.append(_event(e))
        e = e.getparent()
    drin = [_event(x) for x in l.iter(TEI + 'event') if x is not l and x.get('type')]
    return list(reversed(ueber)) + drin


def inline(l):
    """Was Borek IM Vers ausgezeichnet hat."""
    aus = defaultdict(list)
    for e in l.iter():
        if not isinstance(e.tag, str) or e is l:
            continue
        name = etree.QName(e).localname
        txt = text_von(e)
        if name == 'usg':
            # Die Bezeichnung, unter der das Pferd im Vers auftritt: 'ors',
            # 'Ez'. @type ist Boreks Wortart (NN, P, adj, AP).
            aus['designations'].append({'pos': e.get('type'), 'text': txt})
        elif name in ('trait', 'object'):
            aus[name + 's'].append({'type': e.get('type'), 'text': txt})
        elif name == 'person':
            eintrag = {'text': txt}
            if e.get('role'):
                eintrag['role'] = e.get('role')
            # Boreks @ref mischt hier Personen und Werke ('#Willehalm' neben
            # '#Pz.'). Ein Werkverweis ist keine Person und darf nicht als
            # Figur in den Index.
            figuren = [r for r in ref_liste(e) if r not in mapping.SIGLE]
            if figuren:
                eintrag['ref'] = figuren
            aus['persons'].append(eintrag)
        elif name in ('persName', 'placeName'):
            aus[{'persName': 'persons', 'placeName': 'places'}[name]].append({'text': txt})
        elif name == 'state':
            aus['states'].append({'text': txt})
        elif name == 'horseName':
            aus['horseNames'].append({'text': txt, 'ref': erste_ref(e)})
        elif name == 'horseGrp':
            # Die Bezeichnung einer Pferdegruppe statt eines einzelnen Tiers,
            # genau einmal im Datensatz: Pz. 474,3 vergleicht 'ein ors' mit
            # 'den orsn'. Nicht unter designations, das waere eine Aussage
            # ueber DIESES Pferd.
            aus['horseGroups'].append({'text': txt})
        elif name == 'objectName':
            # Eigenname eines Gegenstands (Wh. 77,14: das Schwert Schoyuse).
            # Steht der Name in einem <object>, ist er dort schon im Text
            # enthalten und wird hier nicht ein zweites Mal gefuehrt.
            if not any(a.tag == TEI + 'object' for a in e.iterancestors()
                       if isinstance(a.tag, str) and a is not l):
                aus['objectNames'].append({'text': txt})
    return dict(aus)


def pferde_und_belege(baum):
    wurzel = baum.getroot()
    liste = [h for h in wurzel.iter(TEI + 'horse')
             if h.getparent() is not None and h.getparent().tag == TEI + 'listPerson']

    # Zwei Sorten <horse> auf Listenebene: 10 Deklarationen (xml:id + ref auf
    # das Werk, sonst leer) und 13 Vorkommen (die Belege). Verknuepft sind sie
    # ueber horseName/@ref -> Deklaration/@xml:id. Drei Vorkommen tragen gar
    # keinen Namen, das sind die namenlosen Pferde.
    pferde = {}
    for h in liste:
        hid = h.get(XML + 'id')
        if hid:
            pferde[hid] = {'id': hid, 'name': hid, 'variants': [],
                           'works': [], 'attestations': 0, 'named': True}

    belege, anonym = [], Counter()
    for h in liste:
        if h.get(XML + 'id'):
            continue
        hn = h.find(TEI + 'horseName')
        hid = erste_ref(hn) if hn is not None else None
        varianten = [o.text for o in h.iter(TEI + 'orth') if o.text]

        for src in h.findall(TEI + 'source'):
            werk = erste_ref(src)
            sigle = mapping.SIGLE.get(werk)
            if sigle is None:
                continue
            eigner = hid
            if eigner is None:
                anonym[sigle] += 1
                eigner = '%s_ungenannt_%d' % (sigle, anonym[sigle])
                pferde.setdefault(eigner, {
                    'id': eigner, 'name': None, 'variants': [], 'works': [],
                    'attestations': 0, 'named': False})
            eintrag = pferde.setdefault(eigner, {
                'id': eigner, 'name': eigner, 'variants': [], 'works': [],
                'attestations': 0, 'named': True})
            for v in varianten:
                if v not in eintrag['variants']:
                    eintrag['variants'].append(v)
            if sigle not in eintrag['works']:
                eintrag['works'].append(sigle)

            for l in src.iter(TEI + 'l'):
                belege.append({'horse': eigner, 'work': sigle, 'n': l.get('n'),
                               'citation': '%s %s' % (werk, l.get('n')),
                               'text': text_von(l), 'events': ereignisse(l),
                               **inline(l)})
    return pferde, belege


def main():
    ap = argparse.ArgumentParser(description='#193: Horses-Index bauen.')
    ap.add_argument('--dry-run', action='store_true')
    ap.add_argument('--quelle', type=Path, default=HERE / 'arthurianHorses.xml')
    args = ap.parse_args()

    if not args.quelle.exists():
        print('hole %s' % QUELLE)
        args.quelle.write_bytes(urllib.request.urlopen(QUELLE, timeout=60).read())
    roh = args.quelle.read_bytes()

    pferde, belege = pferde_und_belege(etree.parse(io.BytesIO(roh)))

    # Aufloesen: je Werk einmal das Korpus laden, das sind grosse Dateien.
    nach_werk = defaultdict(list)
    for b in belege:
        nach_werk[b['work']].append(b)
    art = Counter()
    for sigle, gruppe in nach_werk.items():
        _, verskette = mapping.lade_verse(sigle)
        # Alle Fassungen desselben Verses gemeinsam bewerten, sonst haengt das
        # Ergebnis daran, welches Pferd den Vers zuerst zitiert.
        fassungen = defaultdict(list)
        for b in gruppe:
            fassungen[b['n']].append(b['text'])
        aufgeloest = {n: mapping.aufloesen(n, sigle, t, verskette)
                      for n, t in fassungen.items()}
        for b in gruppe:
            r = aufgeloest[b['n']]
            b['target'] = r['target']
            b['match'] = r['match']
            b['score'] = r['score']
            art[r['match']] += 1

    for b in belege:
        pferde[b['horse']]['attestations'] += 1

    belege.sort(key=lambda b: (b['work'], mapping.stellenkern(b['n'], b['work']), b['horse']))
    index = {
        'version': VERSION,
        'source': {**HERKUNFT, 'sha256': hashlib.sha256(roh).hexdigest()},
        'horses': sorted(pferde.values(), key=lambda h: (not h['named'], h['id'])),
        'attestations': belege,
    }

    print('Pferde:      %d (%d benannt, %d ungenannt)'
          % (len(pferde), sum(1 for h in pferde.values() if h['named']),
             sum(1 for h in pferde.values() if not h['named'])))
    print('Belegstellen: %d auf %d Versen'
          % (len(belege), len({(b['work'], b['n']) for b in belege})))
    # Je BELEG gezaehlt. Der Bericht 02-map-citations.py zaehlt je VERS und
    # kommt deshalb auf kleinere Zahlen, ohne zu widersprechen.
    print('Aufloesung:   %s (je Beleg)' % dict(art))
    if art['unresolved']:
        print('  WARNUNG: %d Belege ohne Ziel, im Frontend ohne Sprung anzeigen.'
              % art['unresolved'])

    if args.dry_run:
        print('\n--dry-run: nichts geschrieben.')
        return 0

    daten = json.dumps(index, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
    ZIEL.parent.mkdir(exist_ok=True)
    # mtime=0: sonst waere jeder Build byte-verschieden (#125-Prinzip).
    with gzip.GzipFile(ZIEL, mode='wb', mtime=0) as fh:
        fh.write(daten)
    print('\nGeschrieben: %s' % ZIEL.relative_to(REPO))
    print('  unkomprimiert %.0f KB, komprimiert %.0f KB'
          % (len(daten) / 1024, ZIEL.stat().st_size / 1024))
    return 0


if __name__ == '__main__':
    sys.exit(main())
