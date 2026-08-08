#!/usr/bin/env python3
"""#193 Baustein 2: Luise Boreks drei hippologische Wortlisten gegen unseren Wortschatz.

Boreks Fallstudie zu arthurischen Pferden (Hirzel 2023) hat drei Wortlisten
auf TUdatalib hinterlegt: Pferdebezeichnungen, Koerperteile, Gangarten. Dieses
Skript laedt sie und beantwortet zwei Fragen je Form:

  1. Loest sie ueberhaupt auf ein Lemma auf?    -> Luecke im Wortschatz
  2. Traegt das Lemma ein einschlaegiges Konzept? -> Luecke in der Klassifikation

Die Listen werden NICHT im Repo abgelegt. Sie stehen unter CC-BY 4.0 und
duerften es, aber das Skript holt sie in Sekunden reproduzierbar ueber ihre
Handles, und eine Kopie im Repo waere eine zweite Stelle, die altern kann.
Wer offline arbeitet, legt die drei .txt neben dieses Skript.

## Was das Ergebnis NICHT sagt

Eine nicht aufgeloeste Form ist kein fehlendes Lemma. `variants.xml` ist
korpus-abgeleitet (ADR-015): es kennt nur Schreibungen, die in unseren 667
Texten wirklich vorkommen. Boreks Listen stammen aus einem weiteren Textfeld,
darunter Woerterbuecher. Gemessen am 08.08.2026 tragen 34 der 67 nicht
aufgeloesten Pferdebezeichnungen ein bekanntes Grundwort in sich (`-ros`,
`-pfert`), 33 nicht. Das Grundwort ist dort also da und nur diese eine
Zusammensetzung nicht belegt. Die beiden Zahlen stehen hier statt eines
'in der Mehrzahl': der Abstand betraegt eine Form und kippt sonst unbemerkt. Das
Skript trennt die beiden Faelle deshalb, statt eine Zahl zu melden, die als
Arbeitsliste missverstanden wird.

Aufgeloest wird mit Stufe 1 und 2 der kanonischen Kette (exakte normalisierte
Form, dann Varianten-Woerterbuch). Stufe 3, der beidseitige Praefix-Fallback,
bleibt draussen: er ist fuer die Suche gebaut und wuerde den Report mit
Rauschen fuellen (ADR-016).

Usage:
    python scripts/ingest/horses/01-wordlist-crosscheck.py            # Bericht
    python scripts/ingest/horses/01-wordlist-crosscheck.py --json     # maschinenlesbar
    python scripts/ingest/horses/01-wordlist-crosscheck.py --offline  # ohne Download
"""
import argparse
import gzip
import io
import json
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(REPO / 'scripts'))
from mhg_normalizer import normalize_mhg as normalize  # noqa: E402

API = 'https://tudatalib.ulb.tu-darmstadt.de/server/api'

# Handle plus Bitstream-UUID je Liste. Die UUIDs sind stabil und ersparen
# drei Aufloesungsschritte pro Liste; das Handle steht daneben, damit die
# Herkunft ohne Umweg zitierbar bleibt.
LISTEN = {
    'wl-pferdetypen':  ('hdl:tudatalib/2955', '7f5267a3-05c0-4006-9207-2e02523cbf22'),
    'wl-koerperteile': ('hdl:tudatalib/2954', '0a33c43b-6e99-4740-bef9-1a82d49678e6'),
    'wl-gangarten':    ('hdl:tudatalib/2953', 'b1631706-a426-42c9-83f9-c407d91e691d'),
}

# Konzepte, unter denen ein Treffer der jeweiligen Liste stehen sollte.
# Bewusst weit gefasst: der Report zeigt Kandidaten, er entscheidet nicht.
RELEVANT = {
    'wl-pferdetypen': {
        'concept_23220000',   # Pferd/Reiten
        'concept_23221000',   # Pferd und Reiten/Namen
        'concept_14012000',   # Haustiere/Nutztiere
        'concept_14012100',   # Haustiere/Namen
    },
    'wl-koerperteile': {
        'concept_14011100',   # Koerper/Gliedmassen von Saeugetieren
        'concept_23220000',
    },
    'wl-gangarten': {
        'concept_31800000',   # Bewegung
        'concept_21070000',   # Bewegungen/Stellungen/Haltungen
        'concept_23220000',
        'concept_23307300',   # Reisen
    },
}


def hole(name, offline=False):
    """Rohtext einer Liste. ISO-8859-1, so liegt sie im Repositorium."""
    lokal = HERE / (name + '.txt')
    if offline or lokal.exists():
        if not lokal.exists():
            sys.exit('--offline, aber %s fehlt' % lokal)
        raw = lokal.read_bytes()
    else:
        _, uuid = LISTEN[name]
        with urllib.request.urlopen('%s/core/bitstreams/%s/content' % (API, uuid), timeout=30) as r:
            raw = r.read()
    return raw.decode('iso-8859-1')


def main():
    ap = argparse.ArgumentParser(description='#193 Baustein 2: Wortlisten-Abgleich.')
    ap.add_argument('--json', action='store_true', dest='as_json')
    ap.add_argument('--offline', action='store_true', help='Listen neben dem Skript erwarten.')
    args = ap.parse_args()

    with gzip.open(REPO / 'data' / 'authority-index.json.gz', 'rb') as fh:
        idx = json.loads(fh.read())

    by_norm = defaultdict(list)
    by_id = {}
    for lem in idx['lemmata']:
        by_norm[lem['normalized']].append(lem)
        by_id[lem['id']] = lem
    variants = idx['variants']
    concepts = {c['id']: c for c in idx['concepts']}

    def concepts_of(lem):
        out = set()
        for s in lem.get('senses') or []:
            out.update(s.get('conceptIds') or [])
        return out

    report = {}
    for name, relevant in RELEVANT.items():
        roh = hole(name, args.offline)
        zeilen = [l.strip() for l in roh.splitlines() if l.strip()]
        # Borek markiert Formen mit einem Stern (nur in bestimmten
        # Verwendungen einschlaegig). Der Stern ist Notation, nicht
        # Wortbestand: ungestrippt scheitert jede dieser Formen an der
        # Aufloesung und erschiene als Luecke im Wortschatz.
        markiert = sorted({f for f in zeilen if f.endswith('*')})
        uniq = sorted({f.rstrip('*') for f in zeilen})

        resolved, unresolved = {}, []
        for f in uniq:
            n = normalize(f)
            if n in by_norm:
                resolved[f] = ([l['id'] for l in by_norm[n]], 'exakt')
            elif n in variants:
                resolved[f] = ([variants[n]], 'variante')
            else:
                unresolved.append(f)

        # Formen, die ueber IRGENDEINEN ihrer Homographen schon richtig
        # erfasst sind: dort ist ein unklassifizierter Zwilling kein Befund.
        # "ros" trifft das Pferd UND ein lateinisches Wetterwort.
        abgedeckt = {f for f, (ids, _) in resolved.items()
                     if any(concepts_of(by_id[i]) & relevant for i in ids if i in by_id)}

        klassifiziert, offen, verdacht, zwilling = [], [], [], []
        for f, (ids, how) in sorted(resolved.items()):
            for lid in ids:
                lem = by_id.get(lid)
                if lem is None:
                    continue
                cs = concepts_of(lem)
                # .get() und nicht by_norm[...]: by_norm ist ein defaultdict
                # und lebt ueber alle drei Listen. Ein Lesezugriff mit
                # eckigen Klammern legt fuer jede ueber Stufe 2 aufgeloeste
                # Form einen leeren Eintrag an, und die naechste Liste nimmt
                # dieselbe Form dann faelschlich in Stufe 1 mit leerer
                # ID-Liste: sie zaehlt als aufgeloest, faellt aber aus jeder
                # Ergebnisklasse heraus. Drei Formen stehen in mehr als einer
                # Liste (ravit, zeldere, zelter), und zeldere ist genau so
                # verschwunden.
                row = [f, how, lid, lem['lemma'], sorted(cs), len(by_norm.get(normalize(f), []))]
                if cs & relevant:
                    klassifiziert.append(row)
                elif f in abgedeckt:
                    zwilling.append(row)
                elif how == 'variante':
                    # Ueber das Varianten-Woerterbuch gelaufen heisst: im
                    # Korpus traegt ein <w> mit dieser Schreibung dieses
                    # Lemma. Lautet das Lemma dann voellig anders (hors auf
                    # 'haar'), ist eine Fehlannotation wahrscheinlicher als eine
                    # Klassifikationsluecke. Getrennt berichten, sonst liest
                    # sich der Report als Arbeitsliste fuer die falsche Arbeit.
                    verdacht.append(row)
                else:
                    offen.append(row)

        # Steckt in einer nicht aufgeloesten Form ein bekanntes Grundwort?
        # Dann Kompositum oder Schreibvariante, kein fehlendes Lemma. Grobe
        # Heuristik ohne Morphologie: sie findet die -ros-Bildungen und
        # verwechselt sich gelegentlich (schenkel gegen kel).
        bekannt = sorted({normalize(f) for f in resolved}, key=len, reverse=True)
        komposita, echt_offen = [], []
        for f in unresolved:
            n = normalize(f)
            teil = next((b for b in bekannt if len(b) >= 3 and b in n and b != n), None)
            (komposita if teil else echt_offen).append([f, teil])

        report[name] = dict(
            quelle=LISTEN[name][0], formen=len(zeilen), eindeutig=len(uniq),
            aufgeloest=len(resolved), markiert=markiert,
            komposita=komposita, echt_offen=echt_offen,
            klassifiziert=klassifiziert, offen=offen,
            verdacht=verdacht, zwilling=zwilling,
        )

    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    for name, d in report.items():
        print('=' * 78)
        print('%s   (%s)' % (name, d['quelle']))
        print('=' * 78)
        print('  %d Formen, %d eindeutig, %d aufgeloest (%.0f %%)'
              % (d['formen'], d['eindeutig'], d['aufgeloest'],
                 100 * d['aufgeloest'] / d['eindeutig']))
        print('  einschlaegig klassifiziert:  %d' % len(d['klassifiziert']))
        print('  Klassifikation zu pruefen:   %d' % len(d['offen']))
        print('  Zuordnung verdaechtig:       %d' % len(d['verdacht']))
        print('  Homograph, schon abgedeckt:  %d' % len(d['zwilling']))
        print('  Kompositum oder Variante:    %d' % len(d['komposita']))
        print('  ohne erkennbares Grundwort:  %d' % len(d['echt_offen']))
        print()

        def block(rows, titel, limit=40):
            if not rows:
                return
            print('  --- %s ---' % titel)
            for f, how, lid, lemma, cs, amb in rows[:limit]:
                labels = ', '.join((concepts.get(c) or {}).get('termDE', c) for c in cs) or 'gar kein Konzept'
                flag = ' [%d Homographen]' % amb if amb > 1 else ''
                print('    %-16s -> %-12s %-16s [%s]%s' % (f, lid, lemma, labels[:52], flag))
            if len(rows) > limit:
                print('    ... und %d weitere' % (len(rows) - limit))
            print()

        if d['markiert']:
            print('  %d Formen tragen bei Borek einen Stern, vor der Aufloesung entfernt:'
                  % len(d['markiert']))
            print('    ' + ', '.join(d['markiert']))
            print()
        block(d['offen'], 'Lemma getroffen, einschlaegiges Konzept fehlt (Kandidaten fuer Nachklassifikation)')
        block(d['verdacht'], 'ueber eine Korpus-Variante gelaufen, Lemma passt inhaltlich nicht (Verdacht auf Fehlannotation)')
        block(d['zwilling'], 'Homograph, ueber ein anderes Lemma bereits erfasst, kein Befund', 12)
        if d['komposita']:
            print('  --- Kompositum oder Schreibvariante eines vorhandenen Lemmas: %d ---'
                  % len(d['komposita']))
            for i in range(0, len(d['komposita']), 5):
                print('    ' + '  '.join('%s (%s)' % (f, b) for f, b in d['komposita'][i:i + 5]))
            print()
        if d['echt_offen']:
            print('  --- weder aufgeloest noch ein Grundwort erkennbar: %d ---' % len(d['echt_offen']))
            for i in range(0, len(d['echt_offen']), 8):
                print('    ' + '  '.join(f for f, _ in d['echt_offen'][i:i + 8]))
            print()
    return 0


if __name__ == '__main__':
    sys.exit(main())
