#!/usr/bin/env python3
"""
#228, zweiter Schritt: die 26 Ziffern in <supplied> (MR1, WVV) entannotieren
und die dadurch belegfreien Ziffern-Lemmata loeschen.

Entscheidung von KZW in #228 (Kommentar vom 25.09.2026): "Die 26 Ziffern in
MR1 und WVV bitte entannotieren und ihren sichtbaren Wortlaut innerhalb von
<supplied> erhalten. Keine pauschale Uebertragung nach @n. Anschliessend die
dadurch belegfreien Ziffern-Lemmata entfernen, sofern keine weiteren
Referenzen darauf bestehen."

Entannotieren heisst wie in apply-228.py: lemmaRef, pos, ana und corresp
fallen weg, das <w> mit seiner Ziffer bleibt in seinem <supplied>. Die
Funktionen dafuer kommen aus apply-228.py, damit beide Schritte dieselbe
Mechanik haben.

lemma_53328 ("1") behaelt seine 63 Belege in NEIM (#453) und bleibt.
Mur (lemma_66692) ist nicht Teil dieses Schritts: KZW will vorher die
Verknuepfungen von Murouwe und Murstetten geprueft und die Kennzeichnung
reiner Bestandteil-Eintraege geklaert haben.

Danach: scripts/sync/extract-variants.py --apply, beide Indexe, API, Bump.

Aufruf:
    python scripts/ingest/entannotate-228/apply-228-ziffern.py            # Trockenlauf
    python scripts/ingest/entannotate-228/apply-228-ziffern.py --apply    # schreiben
"""

import argparse
import importlib.util
import sys
from collections import Counter
from pathlib import Path

from lxml import etree

HIER = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location('apply228', HIER / 'apply-228.py')
a228 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(a228)
a228.DATUM = '2026-10-01'

T, XID, TEI_DIR, AUTH_DIR = a228.T, a228.XID, a228.TEI_DIR, a228.AUTH_DIR

ZIFFERN_LEMMATA = {'lemma_53328': '1', 'lemma_69748': '36', 'lemma_69749': '42', 'lemma_69750': '49'}
SIGLEN = ('MR1', 'WVV')
# Gemessen am 01.10.2026 auf 4076e1bca. Weicht der Bestand ab, bricht das Skript ab.
ERWARTET = {'MR1': 15, 'WVV': 11, 'loeschen': ['lemma_69748', 'lemma_69749', 'lemma_69750']}
EINTRAG = ('#228: {n} Ziffern in supplied (Zählung der Edition) entannotiert: '
           'lemmaRef, pos, ana und corresp entfallen, die Ziffer bleibt stehen. '
           'Entscheidung KZW 25.09.2026: Ziffern sind keine Lemmata.')


def ziffern_lemma(w):
    lr = w.get('lemmaRef')
    if not lr:
        return None
    ids = [t.split('#')[1] for t in lr.split()]
    treffer = [i for i in ids if i in ZIFFERN_LEMMATA]
    if treffer and len(ids) != 1:
        sys.exit('FEHLER: %s: Ziffern-Lemma in mehrwertigem lemmaRef %r' % (w.get(XID), lr))
    return treffer[0] if treffer else None


def main():
    p = argparse.ArgumentParser(description='#228 Ziffern in MR1/WVV entannotieren')
    p.add_argument('--apply', action='store_true', help='schreiben statt nur pruefen')
    args = p.parse_args()

    tokens = {s: [] for s in SIGLEN}
    belege = Counter(); im_scope = Counter()
    for pfad in sorted(TEI_DIR.glob('*.tei.xml')):
        sigle = pfad.name[:-len('.tei.xml')]
        for w in etree.parse(str(pfad)).getroot().iter(T + 'w'):
            l = ziffern_lemma(w)
            if l is None:
                continue
            belege[l] += 1
            if sigle not in SIGLEN:
                continue
            if w.getparent().tag != T + 'supplied':
                sys.exit('FEHLER: %s steht nicht direkt in <supplied>' % w.get(XID))
            text = ''.join(w.itertext())
            if not text.isdigit():
                sys.exit('FEHLER: %s traegt keine Ziffer, sondern %r' % (w.get(XID), text))
            tokens[sigle].append(w.get(XID))
            im_scope[l] += 1

    for s in SIGLEN:
        print('%s: %d Ziffern' % (s, len(tokens[s])))
        if len(tokens[s]) != ERWARTET[s]:
            sys.exit('FEHLER: %s erwartet %d' % (s, ERWARTET[s]))
    for l, orth in sorted(ZIFFERN_LEMMATA.items()):
        print('  %s "%s": %d Belege, davon %d im Scope' % (l, orth, belege[l], im_scope[l]))

    waisen = sorted(l for l in im_scope if im_scope[l] == belege[l])
    verweise = a228.fremdverweise(set(waisen))
    for l in sorted(verweise):
        print('  gehalten %s: %s' % (l, '; '.join(verweise[l])))
    loeschen = [l for l in waisen if l not in verweise]
    print('belegfrei danach: %d, gehalten: %d, geloescht: %d' % (len(waisen), len(verweise), len(loeschen)))
    if loeschen != ERWARTET['loeschen']:
        sys.exit('FEHLER: erwartet geloescht %s' % ERWARTET['loeschen'])

    neu = {}
    for sigle in SIGLEN:
        pfad = TEI_DIR / (sigle + '.tei.xml')
        with open(pfad, encoding='utf-8', newline='') as fh:
            text = fh.read()
        for xml_id in tokens[sigle]:
            text = a228.entannotiere(text, xml_id, sigle)
        neu[pfad] = a228.mit_change(text, EINTRAG.format(n=len(tokens[sigle])), sigle)

    lex = AUTH_DIR / 'lexicon.xml'
    with open(lex, encoding='utf-8', newline='') as fh:
        text = fh.read()
    neu[lex] = a228.loesche_eintraege(text, loeschen)
    print('lexicon.xml: %d Eintraege geloescht' % len(loeschen))

    # Jede Datei muss nach der Aenderung wohlgeformt sein, bevor irgendetwas geschrieben wird.
    for pfad, text in neu.items():
        try:
            etree.fromstring(text.encode('utf-8'))
        except etree.XMLSyntaxError as e:
            sys.exit('FEHLER: %s waere nicht wohlgeformt: %s' % (pfad.name, e))
    if args.apply:
        for pfad, text in neu.items():
            with open(pfad, 'w', encoding='utf-8', newline='') as fh:
                fh.write(text)
    print('%s: %d Dateien' % ('geschrieben' if args.apply else 'Trockenlauf', len(neu)))
    if not args.apply:
        print('Nichts geaendert. Mit --apply schreiben.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
