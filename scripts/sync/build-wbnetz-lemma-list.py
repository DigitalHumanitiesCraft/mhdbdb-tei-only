#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aktualisiert die MHDBDB-Verweise in der Lemmaliste des Woerterbuchnetzes (#225).

Die Eingabedatei stammt von Thomas Burch (Trier) und ist NICHT unsere
Lemmaliste, auch wenn sie so heisst. Sie ist die Lexer-Liste mit einer
optionalen Bruecke zu uns:

    <lexer>
      <entry>
        <lemma>minne</lemma>
        <lemid>M01874</lemid>
        <mhdbdbId>4130</mhdbdbId>      <- optional, das ist unser Anteil
        <url>...</url>
      </entry>
      ...

Trier hat um Formatgleichheit gebeten ("damit ich das Import-Script nicht neu
entwickeln muss"), deshalb wird die Datei zeilenweise bearbeitet und nicht
ueber einen lxml-Roundtrip: alles ausser den <mhdbdbId>-Zeilen bleibt Byte
fuer Byte stehen, inklusive DOCTYPE, Einrueckung und Zeilenenden.

WICHTIG, Lizenz: die Eingabedatei ist Copyright Trier. Sie gehoert nicht ins
Repo, und die Ausgabedatei ebenso wenig. Das Skript weigert sich deshalb,
innerhalb des Repos zu schreiben.

Drei Regeln, entschieden von chsteiner am 2026-08-07 (#225):

1. NUR <mhdbdbId> auffuellen. Unsere Lemmata ohne Lexer-Entsprechung haben in
   diesem Format keinen Platz (keine lemid, keine url) und bleiben draussen.
2. EXAKTES Matching. Ergaenzt wird nur, wo die Schreibform zeichengenau
   uebereinstimmt UND genau ein Lemma von uns sie traegt. Die MHD-
   Normalisierung braechte rund 360 Eintraege mehr, erzeugt aber 133 statt 10
   mehrdeutige Faelle. Begruendung: ein falscher Zeiger ist teurer als ein
   fehlender, weil er im Woerterbuchnetz als geprueftes Querverweis-Ziel
   erscheint.
3. TOTE ZEIGER (die ID gibt es bei uns nicht mehr) werden mit derselben
   Strenge umgebogen, wo die Schreibform sie eindeutig traegt, und sonst
   ersatzlos gestrichen. Eine tote ID ist heute eine Sackgasse: die Lemma-
   Seite meldet "Lemma mit ID N wurde nicht gefunden".

Messwerte des Laufs vom 2026-08-07 gegen lexicon.xml (43.879 Eintraege) und
die Trierer Liste (86.121 Eintraege) stehen im Report, den das Skript selbst
druckt. Sie werden hier bewusst NICHT als Konstanten wiederholt: sie altern
mit beiden Dateien.

Usage:
    python scripts/sync/build-wbnetz-lemma-list.py <trier.xml>
    python scripts/sync/build-wbnetz-lemma-list.py <trier.xml> --apply --out <ziel.xml>
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from lxml import etree

TEI_NS = 'http://www.tei-c.org/ns/1.0'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
REPO = Path(__file__).resolve().parents[2]
LEXICON = REPO / 'authority-files' / 'lexicon.xml'

# Die Zeilen der Eingabe sind schlicht genug fuer einen Zeilenparser, und
# genau das ist gewollt (siehe Docstring). Kein <mhdbdbId> traegt Attribute.
RE_LEMMA = re.compile(r'^\s*<lemma>(.*)</lemma>\s*$')
RE_LEMID = re.compile(r'^\s*<lemid>(.*)</lemid>\s*$')
RE_MHDBDB = re.compile(r'^\s*<mhdbdbId>(.*)</mhdbdbId>\s*$')


def lexikon_lesen(pfad):
    """Liefert (vorhandene_ids, exakte_form -> [ids]) aus lexicon.xml."""
    baum = etree.parse(str(pfad))
    ids = set()
    formen = defaultdict(list)
    for eintrag in baum.iter('{%s}entry' % TEI_NS):
        lid = (eintrag.get(XML_ID) or '').replace('lemma_', '')
        if not lid:
            continue
        ids.add(lid)
        orth = eintrag.find('{%s}form/{%s}orth' % (TEI_NS, TEI_NS))
        if orth is not None and orth.text:
            formen[orth.text].append(lid)
    # Nur eindeutige Formen taugen als Zuordnung (Regel 2).
    eindeutig = {form: liste[0] for form, liste in formen.items() if len(liste) == 1}
    return ids, eindeutig, formen


def verarbeiten(zeilen, vorhandene_ids, eindeutig):
    """Zeilen der Trierer Liste umschreiben.

    Arbeitet in einem Durchgang mit einem Ein-Eintrag-Puffer: <lemma> steht
    laut Format immer vor <lemid> und <mhdbdbId>, die Entscheidung ist also
    zum Zeitpunkt der <mhdbdbId>-Zeile bzw. am </entry> immer schon faellig.
    """
    ausgabe = []
    zaehler = defaultdict(int)
    lemma = None
    lemid_index = None   # Position der <lemid>-Zeile in `ausgabe`
    hat_mhdbdb = False

    for zeile in zeilen:
        treffer_lemma = RE_LEMMA.match(zeile)
        if treffer_lemma:
            lemma = treffer_lemma.group(1).strip()
            lemid_index = None
            hat_mhdbdb = False
            ausgabe.append(zeile)
            continue

        if RE_LEMID.match(zeile):
            ausgabe.append(zeile)
            lemid_index = len(ausgabe) - 1
            continue

        treffer_mhdbdb = RE_MHDBDB.match(zeile)
        if treffer_mhdbdb:
            hat_mhdbdb = True
            alt = treffer_mhdbdb.group(1).strip()
            if alt in vorhandene_ids:
                zaehler['unveraendert'] += 1
                ausgabe.append(zeile)
            else:
                neu = eindeutig.get(lemma)
                if neu:
                    zaehler['umgebogen'] += 1
                    ausgabe.append(zeile.replace('>%s<' % alt, '>%s<' % neu))
                else:
                    # Ersatzlos streichen: die Zeile wird nicht uebernommen.
                    zaehler['gestrichen'] += 1
            continue

        if zeile.strip() == '</entry>':
            if not hat_mhdbdb and lemma is not None:
                neu = eindeutig.get(lemma)
                if neu and lemid_index is not None:
                    # Einruecken wie die <lemid>-Zeile darueber, damit die
                    # Datei so aussieht wie die, die Trier kennt.
                    vorlage = ausgabe[lemid_index]
                    einzug = vorlage[:len(vorlage) - len(vorlage.lstrip())]
                    ende = '\r\n' if vorlage.endswith('\r\n') else '\n'
                    ausgabe.insert(lemid_index + 1,
                                   '%s<mhdbdbId>%s</mhdbdbId>%s' % (einzug, neu, ende))
                    zaehler['ergaenzt'] += 1
                else:
                    zaehler['ohne_zuordnung'] += 1
            ausgabe.append(zeile)
            lemma = None
            lemid_index = None
            hat_mhdbdb = False
            continue

        ausgabe.append(zeile)

    return ausgabe, zaehler


def pruefen(vorher_text, nachher_text):
    """Wohlgeformtheit und Eintragszahl der Ausgabe gegen die Eingabe.

    Die Eintragszahl MUSS gleich bleiben: das Skript aendert Verweise, es
    entfernt keine Lexer-Lemmata. Weicht sie ab, ist der Zeilenparser an
    einem Sonderfall gescheitert, den der Docstring nicht kennt.
    """
    parser = etree.XMLParser(resolve_entities=False, load_dtd=False, no_network=True)
    vorher = etree.fromstring(vorher_text.encode('utf-8'), parser)
    nachher = etree.fromstring(nachher_text.encode('utf-8'), parser)
    v_entries = len(vorher.findall('.//entry'))
    n_entries = len(nachher.findall('.//entry'))
    v_ids = len([e for e in vorher.iter('mhdbdbId') if (e.text or '').strip()])
    n_ids = len([e for e in nachher.iter('mhdbdbId') if (e.text or '').strip()])
    return v_entries, n_entries, v_ids, n_ids


def main():
    p = argparse.ArgumentParser(description=__doc__.split('\n')[1])
    p.add_argument('eingabe', help='Lemmaliste des Woerterbuchnetzes (XML von Trier)')
    p.add_argument('--apply', action='store_true',
                   help='Ausgabedatei wirklich schreiben (sonst nur Report)')
    p.add_argument('--out', help='Zieldatei; Pflicht bei --apply, muss AUSSERHALB des Repos liegen')
    p.add_argument('--lexicon', default=str(LEXICON), help='abweichender Pfad zu lexicon.xml')
    args = p.parse_args()

    eingabe = Path(args.eingabe)
    if not eingabe.is_file():
        print('Eingabedatei nicht gefunden: %s' % eingabe, file=sys.stderr)
        return 2

    vorhandene_ids, eindeutig, alle_formen = lexikon_lesen(Path(args.lexicon))
    mehrdeutig = sum(1 for liste in alle_formen.values() if len(liste) > 1)

    text = eingabe.read_text(encoding='utf-8')
    zeilen = text.splitlines(keepends=True)
    ausgabe, z = verarbeiten(zeilen, vorhandene_ids, eindeutig)
    ergebnis = ''.join(ausgabe)

    v_entries, n_entries, v_ids, n_ids = pruefen(text, ergebnis)

    print('Lexikon      : %d Eintraege, %d eindeutige Schreibformen, %d Formen mit mehreren Lemmata'
          % (len(vorhandene_ids), len(eindeutig), mehrdeutig))
    print('Trierer Liste: %d Eintraege, %d mit Verweis' % (v_entries, v_ids))
    print('')
    print('  unveraendert (Verweis existiert bei uns): %d' % z['unveraendert'])
    print('  ergaenzt (Schreibform exakt eindeutig)  : %d' % z['ergaenzt'])
    print('  umgebogen (tote ID, Form eindeutig)     : %d' % z['umgebogen'])
    print('  gestrichen (tote ID, keine Zuordnung)   : %d' % z['gestrichen'])
    print('  weiterhin ohne Verweis                  : %d' % z['ohne_zuordnung'])
    print('')
    print('Verweise: %d -> %d' % (v_ids, n_ids))
    # Beide Seiten zaehlen nur Zeiger, die bei UNS existieren. Sonst vergleicht
    # die Zeile zwei verschiedene Dinge: die Ausgabe kann per Konstruktion
    # keine toten IDs mehr enthalten, die Eingabe schon.
    erreicht_vor = {i for i in set(_verweise(text)) if i in vorhandene_ids}
    erreicht_nach = {i for i in set(_verweise(ergebnis)) if i in vorhandene_ids}
    print('Erreichbare Lemmata bei uns: %d -> %d (%.2f -> %.2f Prozent von %d)'
          % (len(erreicht_vor), len(erreicht_nach),
             len(erreicht_vor) / len(vorhandene_ids) * 100,
             len(erreicht_nach) / len(vorhandene_ids) * 100,
             len(vorhandene_ids)))
    tot_nach = set(_verweise(ergebnis)) - vorhandene_ids
    print('Tote Zeiger in der Ausgabe : %d (muss 0 sein)' % len(tot_nach))

    if v_entries != n_entries:
        print('\nFEHLER: Eintragszahl veraendert (%d -> %d). Nichts geschrieben.'
              % (v_entries, n_entries), file=sys.stderr)
        return 1

    if not args.apply:
        print('\nDry-Run, nichts geschrieben. Mit --apply --out <ziel.xml> anwenden.')
        return 0

    if not args.out:
        print('\n--apply braucht --out.', file=sys.stderr)
        return 2
    ziel = Path(args.out).resolve()
    if REPO in ziel.parents or ziel == REPO:
        print('\nZiel liegt im Repo (%s). Die Datei ist Copyright Trier und darf '
              'dort nicht landen.' % ziel, file=sys.stderr)
        return 2

    ziel.write_text(ergebnis, encoding='utf-8', newline='')
    print('\nGeschrieben: %s' % ziel)
    return 0


def _verweise(text):
    """Alle nicht-leeren mhdbdbId-Werte eines Dokuments, als Liste.

    Eigenes Muster statt RE_MHDBDB: das ist auf ganze Zeilen verankert und
    findet ueber einen Gesamttext nichts. Genau so ist die Abdeckungszeile
    beim ersten Lauf still auf 0 gelaufen, obwohl die Zaehler daneben stimmten.
    """
    return [w for w in re.findall(r'<mhdbdbId>([^<]*)</mhdbdbId>', text) if w.strip()]


if __name__ == '__main__':
    sys.exit(main())
