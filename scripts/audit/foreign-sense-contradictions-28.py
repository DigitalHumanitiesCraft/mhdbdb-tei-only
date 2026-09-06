#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#28 Phase 2: die Stellen, an denen der Bestand der Sprachzuordnung widerspricht.

Gleis 1 (build-foreign-candidates-28.py) liefert 6.246 Lemmata, deren Senses
auf den Subtree unter concept_23123000 zeigen. Die Liste ist zu gross, um sie
von Hand durchzusehen, und nach Belegzahl sortiert steht das Rauschen oben:
niht traegt "Lateinisch" und allein rund ein Drittel der Tokenmenge.

Dieses Skript baut die zwei Mengen, mit denen Phase 2 anfangen kann, statt mit
einer Frequenzschwelle. Beide sind im Phasenplan als Nachtrag beschrieben und
hier zum ersten Mal als Liste erzeugt.

## Menge 1: die Tokens, deren @ana widerspricht

Neben @lemmaRef (auf das Lemma) tragen die Tokens ein @ana auf den **Sense**.
Wo dieser Sense selbst kein Sprachkonzept fuehrt, sagt der annotierte Bestand
ausdruecklich, dass an dieser Stelle nicht die sprachbezogene Lesart gemeint
ist. Das ist das schaerfste rein maschinelle Ausschlusskriterium, das Gleis 1
hat, und es ist klein: der Phasenplan misst 430 solche Tokens gegen 209.832,
die auf einen Sprach-Sense zeigen.

Klein ist hier ein Vorzug. 430 Belege sind lesbar, 209.832 sind es nicht.

## Menge 2: die belegstaerksten Lemmata

Der Phasenplan haelt fest, dass ein Frequenz-Cutoff falsch waere: in derselben
obersten Klasse stehen niht (Rauschen) und bischof, klâr, engel (echte
Lehnwoerter). Die Klasse ist trotzdem der richtige Einstieg, weil sie ueber
gut drei Viertel der Nicht-Namen-Tokens entscheidet und weil sie klein genug
ist, um sie einzeln anzusehen. Das Skript legt sie mit den Angaben vor, die
fuer ein Urteil noetig sind: Belegzahl, Streuung ueber Texte, die zugeordneten
Sprachen, die uebrigen Konzepte des Lemmas, und wie oft ein @ana der
Zuordnung widerspricht.

## Was das Skript NICHT tut

Es entscheidet nichts und schreibt nichts ins Korpus. Ob eine Zuordnung
bleibt, ist eine philologische Frage; §28 haelt ausdruecklich fest, dass
zwischen Lehnwort und Fremdwort keine Grenze gezogen wird und dass kein
Integrationsgrad-Urteil in die Daten kommt.

Nur lesend, deterministisch. Ein Lauf braucht rund eine Viertelstunde, im
Wesentlichen fuer den Korpusdurchlauf.

Usage:
    python scripts/audit/foreign-sense-contradictions-28.py \
        --out-dir ingest/foreign-lang
"""
import argparse
import csv
import importlib.util
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / 'scripts'))
from corpus_files import corpus_files  # noqa: E402

from lxml import etree  # noqa: E402

TEI = '{http://www.tei-c.org/ns/1.0}'
XML_ID = '{http://www.w3.org/XML/1998/namespace}id'
LEMMATA_INDEX = REPO / 'api' / 'lemmata' / 'index.json'
HANDPRUEFUNG_AB = 501       # Grenze der obersten Belegklasse aus Gleis 1
KONTEXT_FENSTER = 12        # Tokens je Seite fuer die Belegzeile

# Konvention in scripts/audit/ (#329): das Skript druckt Korpusformen, und die
# MHG-Sonderzeichen liegen ausserhalb von cp1252.
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8',
                                  errors='replace')


def gleis1():
    """language_concepts() und candidate_lemmata() aus dem Gleis-1-Skript.

    Importiert statt nachgebaut. Die Huelle ist die Stelle, an der Gleis 1
    schon einmal danebenlag (die Wurzel fehlte, 27 Lemmata gingen lautlos
    verloren), und eine zweite Fassung derselben Logik waere genau die Art
    Verdopplung, an der so etwas ein zweites Mal passiert. Der Dateiname
    traegt Bindestriche und ist damit kein gueltiger Modulname, deshalb der
    Weg ueber importlib statt ueber ein import-Statement.
    """
    pfad = Path(__file__).with_name('build-foreign-candidates-28.py')
    spec = importlib.util.spec_from_file_location('gleis1_28', pfad)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def senses_je_lemma(concepts):
    """{sense_id: (lemma_id, hat_sprachkonzept)} aus api/lemmata/index.json."""
    with LEMMATA_INDEX.open(encoding='utf-8') as f:
        items = json.load(f)['items']
    out = {}
    for item in items:
        for sense in item.get('senses') or []:
            sid = sense.get('id')
            if not sid:
                continue
            cids = set(sense.get('conceptIds') or [])
            out[sid] = (item['id'], bool(cids & set(concepts)))
    return out


def token_text(el):
    return ''.join(el.itertext()).strip()


def scan(kandidaten, sense_info):
    """Ein Durchlauf: Belege, Streuung und die widersprechenden @ana-Tokens."""
    tokens = Counter()
    texte = defaultdict(set)
    ohne_ana = Counter()
    sprach_ana = Counter()
    gegen_ana = Counter()
    treffer = []

    for fp in corpus_files():
        baum = etree.parse(str(fp), etree.XMLParser(
            no_network=True, load_dtd=False, resolve_entities=False))
        body = baum.getroot().find('.//%sbody' % TEI)
        if body is None:
            continue
        sigle = fp.name.split('.')[0]
        ws = list(body.iter('%sw' % TEI))
        texts = [token_text(w) for w in ws]
        for i, w in enumerate(ws):
            ref = w.get('lemmaRef')
            if not ref:
                continue
            # Token-genau (CONTRACTS.md B.1), nie als Teilzeichenkette.
            lids = [t.split('#')[-1] for t in ref.split()]
            for lid in lids:
                if lid not in kandidaten:
                    continue
                tokens[lid] += 1
                texte[lid].add(sigle)
                ana = w.get('ana')
                if not ana:
                    ohne_ana[lid] += 1
                    continue
                # Ein Token kann mehrere Senses tragen; sprachbezogen zaehlt,
                # sobald einer davon ein Sprachkonzept fuehrt.
                sids = [t.split('#')[-1] for t in ana.split()]
                bekannt = [sense_info[s] for s in sids if s in sense_info]
                if not bekannt:
                    ohne_ana[lid] += 1
                    continue
                if any(hat for _, hat in bekannt):
                    sprach_ana[lid] += 1
                    continue
                gegen_ana[lid] += 1
                lo, hi = max(0, i - KONTEXT_FENSTER), i + KONTEXT_FENSTER + 1
                treffer.append({
                    'sigle': sigle,
                    'xml_id': w.get(XML_ID) or '',
                    'form': texts[i],
                    'lemma_id': lid,
                    'lemma': kandidaten[lid]['lemma'],
                    'sprachen': ' '.join(kandidaten[lid]['languages']),
                    'sense_ids': ' '.join(sids),
                    'kontext': ' '.join(
                        ('**%s**' % t) if j == i else t
                        for j, t in enumerate(texts[lo:hi], start=lo) if t),
                })
        baum.getroot().clear()
    return tokens, texte, ohne_ana, sprach_ana, gegen_ana, treffer


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--out-dir', required=True)
    args = ap.parse_args()
    out = Path(args.out_dir)
    if not out.is_absolute():
        out = REPO / out
    out.mkdir(parents=True, exist_ok=True)

    g1 = gleis1()
    concepts = g1.language_concepts()
    kandidaten, lemmata_gesamt = g1.candidate_lemmata(concepts)
    print('Sprachkategorien (mit Wurzel): %d' % len(concepts))
    print('Kandidaten-Lemmata: %d von %d' % (len(kandidaten), lemmata_gesamt))

    sense_info = senses_je_lemma(concepts)
    eigene = {s for s, (lid, _) in sense_info.items() if lid in kandidaten}
    mit_sprache = sum(1 for s in eigene if sense_info[s][1])
    print('Senses der Kandidaten: %d, davon mit Sprachkonzept: %d (%.1f %%)'
          % (len(eigene), mit_sprache, 100.0 * mit_sprache / len(eigene)))

    tokens, texte, ohne_ana, sprach_ana, gegen_ana, treffer = scan(
        kandidaten, sense_info)
    gesamt = sum(tokens.values())
    print('\nTokens ueber @lemmaRef: %d' % gesamt)
    print('  mit @ana auf einen Sprach-Sense : %d' % sum(sprach_ana.values()))
    print('  mit @ana, das WIDERSPRICHT      : %d' % sum(gegen_ana.values()))
    print('  ohne verwertbares @ana          : %d' % sum(ohne_ana.values()))

    # Menge 1
    treffer.sort(key=lambda r: (-gegen_ana[r['lemma_id']], r['lemma_id'],
                                r['sigle'], r['xml_id']))
    p1 = out / '28-phase2-ana-widerspruch.csv'
    with p1.open('w', encoding='utf-8-sig', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=list(treffer[0].keys()), delimiter=';')
        wr.writeheader()
        wr.writerows(treffer)
    print('\nMenge 1 geschrieben: %s (%d Zeilen, %d Lemmata)'
          % (p1, len(treffer), len({r['lemma_id'] for r in treffer})))
    print('  betroffene Lemmata, nach Widerspruechen:',
          dict(Counter({kandidaten[l]['lemma']: n
                        for l, n in gegen_ana.items()}).most_common(12)))

    # Menge 2
    hand = []
    for lid, n in tokens.most_common():
        if n < HANDPRUEFUNG_AB:
            break
        k = kandidaten[lid]
        if k['is_name']:
            continue
        hand.append({
            'lemma_id': lid, 'lemma': k['lemma'], 'pos': k['pos'],
            'pos_alle': ' '.join(k['posAll']),
            'sprachen': ' '.join(k['languages']),
            'sprachkonzepte': k['lang_concepts'],
            'konzepte_gesamt': k['concepts_total'],
            'belege': n, 'texte': len(texte[lid]),
            'ana_sprache': sprach_ana[lid],
            'ana_widerspruch': gegen_ana[lid],
            'ohne_ana': ohne_ana[lid],
            'urteil': '', 'begruendung': '',
        })
    p2 = out / '28-phase2-handpruefung.csv'
    with p2.open('w', encoding='utf-8-sig', newline='') as f:
        wr = csv.DictWriter(f, fieldnames=list(hand[0].keys()), delimiter=';')
        wr.writeheader()
        wr.writerows(hand)
    anteil = sum(r['belege'] for r in hand)
    nicht_namen = sum(n for l, n in tokens.items()
                      if not kandidaten[l]['is_name'])
    print('\nMenge 2 geschrieben: %s (%d Lemmata, %d Belege = %.1f %% der '
          'Nicht-Namen-Tokens)' % (p2, len(hand), anteil,
                                   100.0 * anteil / nicht_namen))
    print('  Die Spalten urteil und begruendung sind leer und fuer die '
          'Durchsicht da.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
