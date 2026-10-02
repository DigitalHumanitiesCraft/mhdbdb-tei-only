#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
#370 Punkt 2: Belegsammler fuer die 484 offenen Paare (Schreibung, Lemma).

Liest ingest/wzb/370-corresp/offene-faelle.csv, scannt tei/ einmal und schreibt
je Paar die Evidenz, auf der die Entscheidung steht, nach
ingest/wzb/370-corresp/evidenz.json:

- alle WZB-Tokens des Paars (xml:id) mit Kontext (10 Tokens davor, 10 danach)
- Lemma aus lexicon.xml: Lemmaform, Wortart, Zahl der Senses
- Varianten desselben Lemmas aus variants.xml (die aehnlichsten Formen)
- dieselbe Schreibung ausserhalb der WZB: unter welchen Lemmata, wie oft
- dieselbe NORMALISIERTE Form im ganzen Korpus: unter welchen Lemmata, wie oft
  (das ist die Grundlage fuer Vorschrift B aus #378)
- die heutige first-wins-Aufloesung der normalisierten Form (variants.xml)

Mit --nachtrag liest es offene-faelle-nachtrag.csv (find-370-nachtrag.py) und
schreibt evidenz-nachtrag.json.

Nur Lesen. Aufruf aus dem Repo-Wurzelverzeichnis:
    python scripts/review/collect-370-evidence.py [--nachtrag]
"""

import csv
import difflib
import json
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / 'scripts'))
from corpus_files import corpus_files  # noqa: E402
from mhg_normalizer import normalize_mhg  # noqa: E402

TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
DIR = ROOT / 'ingest' / 'wzb' / '370-corresp'
KONTEXT = 10


def lemma_id(ref):
    """Lemma-Id aus genau einem Verweis '#lemma_N'; mehrere Verweise sind ein harter Fehler."""
    if not ref:
        return None
    if len(ref.split()) != 1 or ref.count('#') != 1:
        raise SystemExit('mehrwertiger oder unbekannter Verweis, Schluessel waere mehrdeutig: %r' % ref)
    return ref.split('#')[1]


def lade_paare(name='offene-faelle.csv'):
    with open(DIR / name, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter=';'))


def scan_korpus(paare):
    """Ein Durchgang. Gibt zurueck: Tokenliste der WZB mit Kontext, Zaehler."""
    ziel = {(p['form_schluessel'], p['lemma']) for p in paare}
    formen = {p['form_schluessel'] for p in paare}
    exakt_ausserhalb = defaultdict(Counter)    # form -> Counter(lemma) ausserhalb WZB
    norm_gesamt = defaultdict(Counter)         # normalisierte Form -> Counter(lemma), gesamt
    norm_form_ziel = {normalize_mhg(f) for f in formen}
    wzb_belege = defaultdict(list)             # (form, lemma) -> [(id, ctx_vor, tok, ctx_nach, corresp)]
    wzb_gleiche_form_anderes_lemma = defaultdict(Counter)

    dateien = corpus_files()
    for n, pfad in enumerate(dateien, 1):
        ist_wzb = pfad.name == 'WZB.tei.xml'
        toks = []   # (text, id, lemma, corresp) in Dokumentordnung
        for _, el in etree.iterparse(str(pfad), events=('end',), tag=(TEI + 'w', TEI + 'pc')):
            text = ''.join(el.itertext()).strip()
            lem = lemma_id(el.get('lemmaRef')) if el.tag == TEI + 'w' else None
            if ist_wzb:
                toks.append((text, el.get(XMLID), lem, el.get('corresp'), el.get('pos')))
            elif lem and text:
                tl = unicodedata.normalize('NFC', text).lower()
                nf = normalize_mhg(text)
                if tl in formen:
                    exakt_ausserhalb[tl][lem] += 1
                if nf in norm_form_ziel:
                    norm_gesamt[nf][lem] += 1
            if not ist_wzb:
                el.clear()
        if ist_wzb:
            for i, (text, xid, lem, corr, pos) in enumerate(toks):
                if not lem or not text:
                    continue
                tl = unicodedata.normalize('NFC', text).lower()
                nf = normalize_mhg(text)
                if nf in norm_form_ziel:
                    norm_gesamt[nf][lem] += 1
                if (tl, lem) in ziel and not corr:
                    vor = ' '.join(t[0] for t in toks[max(0, i - KONTEXT):i])
                    nach = ' '.join(t[0] for t in toks[i + 1:i + 1 + KONTEXT])
                    wzb_belege[(tl, lem)].append({'id': xid, 'vor': vor, 'tok': text, 'nach': nach, 'pos': pos})
                elif tl in formen and (tl, lem) not in ziel:
                    wzb_gleiche_form_anderes_lemma[tl][lem] += 1
        if n % 100 == 0:
            print(f'  {n}/{len(dateien)} Dateien', file=sys.stderr)
    return wzb_belege, exakt_ausserhalb, norm_gesamt, wzb_gleiche_form_anderes_lemma


def lade_lexikon(lemmata):
    info = {}
    for _, el in etree.iterparse(str(ROOT / 'authority-files' / 'lexicon.xml'),
                                 events=('end',), tag=TEI + 'entry'):
        xid = el.get(XMLID)
        if xid in lemmata:
            orth = el.find(f'{TEI}form/{TEI}orth')
            pos = [p.text for p in el.iterfind(f'{TEI}gramGrp/{TEI}pos')]
            senses = el.findall(TEI + 'sense')
            info[xid] = {
                'orth': orth.text if orth is not None else None,
                'pos': pos,
                'senses': len(senses),
                'defs': [''.join(d.itertext()).strip() for d in el.iter(TEI + 'def')][:2],
            }
        el.clear()
    return info


def lade_varianten():
    """lemma -> [Formen]; first-wins-Abbildung normalisierte Form -> Lemma."""
    je_lemma = defaultdict(list)
    first_wins = {}
    for _, el in etree.iterparse(str(ROOT / 'authority-files' / 'variants.xml'),
                                 events=('end',), tag=TEI + 'entry'):
        lem = lemma_id(el.get('corresp'))
        for f in el.iterfind(TEI + 'form'):
            if f.text:
                je_lemma[lem].append(f.text)
                first_wins.setdefault(normalize_mhg(f.text), lem)
        el.clear()
    return je_lemma, first_wins


def aehnlichste(form, kandidaten, n=8):
    uniq = sorted(set(kandidaten))
    return difflib.get_close_matches(form, uniq, n=n, cutoff=0.0)


def main():
    nachtrag = '--nachtrag' in sys.argv[1:]
    paare = lade_paare('offene-faelle-nachtrag.csv' if nachtrag else 'offene-faelle.csv')
    print(f'{len(paare)} Paare, {sum(int(p["tokens"]) for p in paare)} Tokens', file=sys.stderr)
    belege, ausserhalb, norm_gesamt, wzb_anders = scan_korpus(paare)
    lemmata = {p['lemma'] for p in paare}
    # Konkurrenten kommen aus der first-wins-Abbildung und aus dem Korpuszaehler
    lex = lade_lexikon(lemmata | {l for c in norm_gesamt.values() for l in c})
    je_lemma, first_wins = lade_varianten()

    ergebnis = []
    for p in paare:
        form, lem = p['form_schluessel'], p['lemma']
        nf = normalize_mhg(form)
        heute = first_wins.get(nf)
        konk = norm_gesamt.get(nf, Counter())
        ergebnis.append({
            'form': form,
            'lemma': lem,
            'tokens': int(p['tokens']),
            'norm': nf,
            'lemma_info': lex.get(lem),
            'varianten_aehnlich': aehnlichste(form, je_lemma.get(lem, [])),
            'varianten_zahl': len(set(je_lemma.get(lem, []))),
            'heute_aufgeloest': heute,
            'heute_lage': ('nicht' if heute is None else
                           'richtig' if heute == lem else 'anderes'),
            'heute_lemma_info': lex.get(heute) if heute else None,
            'exakt_ausserhalb_wzb': ausserhalb.get(form, {}),
            'norm_korpus': dict(konk),
            'norm_korpus_lemma_info': {l: lex.get(l) for l in konk if l != lem},
            'wzb_gleiche_form_anderes_lemma': dict(wzb_anders.get(form, {})),
            'belege': belege.get((form, lem), []),
        })

    summe = sum(e['tokens'] for e in ergebnis)
    belegt = sum(len(e['belege']) for e in ergebnis)
    lage = Counter(e['heute_lage'] for e in ergebnis)
    lage_tok = Counter()
    for e in ergebnis:
        lage_tok[e['heute_lage']] += e['tokens']
    print(f'Paare {len(ergebnis)}, Tokens csv {summe}, Tokens mit Beleg gefunden {belegt}', file=sys.stderr)
    print('Lage heute (Paare):', dict(lage), 'Tokens:', dict(lage_tok), file=sys.stderr)
    with open(DIR / ('evidenz-nachtrag.json' if nachtrag else 'evidenz.json'), 'w', encoding='utf-8') as f:
        json.dump(ergebnis, f, ensure_ascii=False, indent=1)


if __name__ == '__main__':
    main()
