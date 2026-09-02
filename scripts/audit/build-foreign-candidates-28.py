#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#28 Phase 1, Gleis 1: Kandidatenmenge fuer Schicht B aus dem Begriffssystem.

Baut die Quelle A des Phasenplans (docs/features/FREMDSPRACHEN-PHASENPLAN-28.md,
Phase 1 Punkt 1): alle Lemmata, deren Senses auf eine Sprachkategorie unter
concept_23123000 ("Einzelsprachen", alternativ "Fremdsprachen") zeigen, mit
ihrer Korpusbelegung. Das Skript aendert nichts, es liest und zaehlt.

Es ersetzt Gleis 2 (LLM-Batch ueber alle 43.879 Lemmata) nicht, aber es
verkleinert dessen Aufgabe: der Entscheidungsraum sinkt von 43.879 auf die
hier ausgewiesene Kandidatenmenge.

## Warum ueber @lemmaRef und nie ueber Zeichenketten

Der Kommentar vom 2026-08-10 in #28 hat gemessen, warum eine Suche nach der
Oberflaechenform in lexicon.xml systematisch nichts findet: die Token-Form
"blamensir" kommt dort null mal vor, das Lemma heisst "blâmensier". Wer von
der Form im Text aus greppt, bekommt eine leere Menge und haelt sie fuer einen
Befund. Der Weg fuehrt ueber das @lemmaRef am Token. Diese Regel ist der
Grund, warum die Vorbedingung von Phase 1 als erledigt gilt, und sie ist hier
die einzige Verbindung zwischen Korpus und Lexikon.

## Was das Begriffssystem leistet und was nicht

concept_23123000 haengt unter concept_23120000 ("Kommunikation/Sprache"). Es
ist ein **Bedeutungsfeld, kein Herkunftsfeld**, und wird in der Praxis fuer
beides benutzt. Deshalb weist der Report drei Dinge getrennt aus:

  * die Belegklassen, denn die unteren sind sauber und die oberste traegt das
    Rauschen. Ein reiner Frequenz-Cutoff waere trotzdem falsch: in derselben
    obersten Klasse stehen echte Lehnwoerter (bischof, engel, klâr) neben
    ersichtlichem Rauschen (niht traegt "Lateinisch");
  * die Eigennamen, denn Namenherkunft ist eine eigene Frage (Entscheidung
    KZW, nicht Gegenstand dieses Skripts);
  * die Konzeptdichte, denn ein Schwellwert darueber hilft nicht: die Masse
    der Lemmata traegt mehrere Konzepte, von denen eines ein Sprachkonzept ist.

## Messvorschrift

Sprachkategorien: transitive Huelle unter concept_23123000 in
authority-files/concepts.xml. Der Baum steht dort **nicht** in der
Element-Verschachtelung, sondern in <ptr type="broader">; die <category>
sind Geschwister. Name einer Kategorie ist ihr <term xml:lang="de"> ohne
@type (der mit type="alternative" ist der Zweitname).

Lemmata: api/lemmata/index.json, Feld senses[].conceptIds. Das ist dieselbe
Quelle, aus der das Frontend arbeitet.

Tokens: die 667 Dateien in tei/ ueber corpus_files(), gezaehlt werden <w> im
<body> mit @lemmaRef. Lemma-Ids werden whitespace-getrennt und auf das ganze
Token verglichen, nie als Teilzeichenkette (CONTRACTS.md B.1): "#lemma_308"
darf "#lemma_3089" nicht treffen.

Streuung ist die Zahl der Korpusdateien mit mindestens einem Beleg.

Usage:
    python scripts/audit/build-foreign-candidates-28.py
    python scripts/audit/build-foreign-candidates-28.py --top 25
    python scripts/audit/build-foreign-candidates-28.py --csv ingest/foreign-lang/28-gleis1-kandidaten.csv
"""
import argparse
import csv
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
from corpus_files import corpus_files  # noqa: E402

# Konvention in scripts/audit/ (#329): das Skript druckt Korpusformen, und die
# MHG-Sonderzeichen liegen ausserhalb von cp1252. Ohne den Wrapper toetet eine
# Windows-Konsole den Lauf an seiner eigenen Ausgabe.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
XMLLANG = '{http://www.w3.org/XML/1998/namespace}lang'

CONCEPTS_XML = PROJECT_ROOT / 'authority-files' / 'concepts.xml'
LEMMATA_INDEX = PROJECT_ROOT / 'api' / 'lemmata' / 'index.json'

ROOT_CONCEPT = 'concept_23123000'

# Klassengrenzen der Belegverteilung. Die 501 ist keine Schwelle zum Wegwerfen,
# sondern die Stelle, an der die Handpruefung anfaengt: oberhalb sind es wenige
# genug Lemmata, um sie einzeln anzusehen, und sie tragen den Grossteil der
# Tokenmenge.
BELEG_CLASSES = [
    (1, 1, '1'),
    (2, 5, '2 bis 5'),
    (6, 20, '6 bis 20'),
    (21, 100, '21 bis 100'),
    (101, 500, '101 bis 500'),
    (501, None, 'ab 501'),
]

HAND_REVIEW_FROM = 501


def parse_xml(path):
    """Parser ohne Netz. Die Authority-Files deklarieren keine externe DTD,
    aber der Schalter ist billig und haelt das Verhalten ueber alle Skripte
    gleich."""
    parser = etree.XMLParser(no_network=True, load_dtd=False, resolve_entities=False)
    return etree.parse(str(path), parser)


def language_concepts():
    """ROOT_CONCEPT und seine Nachfahren, transitiv, mit deutschem Namen.

    Der Begriffsbaum steht in <ptr type="broader">, nicht in der Element-
    Verschachtelung: alle <category> sind Geschwister. Wer hier ueber
    getparent() geht, bekommt eine leere Menge.

    **Die Wurzel gehoert dazu.** Der Phasenplan definiert die Menge als die
    Lemmata, deren Senses auf den concept_23123000-*Subtree* zeigen, und ein
    Subtree enthaelt seine Wurzel. 31 Lemmata haengen direkt an ihr, 27 davon
    ohne jeden Treffer in einer der 17 benannten Sprachkategorien, und es sind
    genau die, die Gleis 1 sucht: englisch, welsch, rotwalsch, tolmetze,
    enwelsch, bardes. Wer nur die echten Nachfahren nimmt, verliert sie
    lautlos.

    Der Graph ist kein Baum: 51 Kategorien tragen mehr als ein <ptr
    type="broader">, und concept_12050000 zeigt auf sich selbst. Beides ist
    hier folgenlos, aber nur wegen der visited-Menge; ohne sie laeuft die
    Schleife nicht zurueck.
    """
    tree = parse_xml(CONCEPTS_XML)
    children = defaultdict(list)
    names = {}
    known = set()
    for cat in tree.iter('%scategory' % TEI):
        cid = cat.get(XMLID)
        if not cid:
            continue
        known.add(cid)
        desc = cat.find('%scatDesc' % TEI)
        if desc is None:
            continue
        for term in desc.findall('%sterm' % TEI):
            # Der Zweitname traegt type="alternative"; der Hauptname hat kein @type.
            if term.get(XMLLANG) == 'de' and term.get('type') is None:
                names[cid] = (term.text or '').strip()
                break
        for ptr in desc.findall('%sptr' % TEI):
            if ptr.get('type') == 'broader':
                parent = (ptr.get('target') or '').lstrip('#')
                if parent:
                    children[parent].append(cid)

    # Die Wurzel muss als <category> tatsaechlich vorkommen, und das wird hier
    # geprueft statt an der Rueckgabe. Seit die Huelle bei der Wurzel selbst
    # startet, ist die Rueckgabe naemlich nie leer: die Schleife unten setzt
    # out[ROOT_CONCEPT] auch dann, wenn names sie nicht kennt, und faellt auf
    # die Id als Namen zurueck. Ein "if not concepts" beim Aufrufer waere damit
    # toter Code, und ein umbenanntes Wurzelkonzept schriebe lautlos eine CSV
    # mit nur der Kopfzeile und Exit 0. Genau die leere Menge, die der
    # Docstring oben als Falle beschreibt.
    if ROOT_CONCEPT not in known:
        return {}

    out = {}
    stack = [ROOT_CONCEPT]
    while stack:
        cid = stack.pop()
        if cid in out:
            continue
        out[cid] = names.get(cid, cid)
        stack.extend(children.get(cid, []))
    return out


def candidate_lemmata(concepts):
    """Lemmata mit mindestens einem Sprachkonzept, aus api/lemmata/index.json.

    Rueckgabe: {lemma_id: dict}, dazu die Gesamtzahl der Lemmata im Index als
    Nenner fuer den Anteil.
    """
    with LEMMATA_INDEX.open(encoding='utf-8') as f:
        items = json.load(f)['items']

    out = {}
    for item in items:
        hits = set()
        concept_total = set()
        for sense in item.get('senses') or []:
            for cid in sense.get('conceptIds') or []:
                concept_total.add(cid)
                if cid in concepts:
                    hits.add(cid)
        if not hits:
            continue
        pos_all = item.get('posAll') or ([item['pos']] if item.get('pos') else [])
        out[item['id']] = {
            'id': item['id'],
            'lemma': item.get('lemma') or '',
            'normalized': item.get('normalized') or '',
            'pos': item.get('pos') or '',
            'posAll': pos_all,
            'is_name': 'NAM' in pos_all,
            'languages': sorted(concepts[c] for c in hits),
            'lang_concepts': len(hits),
            'concepts_total': len(concept_total),
        }
    return out, len(items)


def corpus_counts(candidates):
    """Belege je Kandidaten-Lemma ueber @lemmaRef, plus die Nenner.

    Ein Pass ueber die 667 Dateien. Gezaehlt wird im <body>: der <teiHeader>
    traegt keine <w>, aber die Einschraenkung ist die Vorschrift aus #216 und
    haelt das Skript gegen kuenftige Header-Aenderungen stabil.
    """
    tokens = Counter()
    texts = defaultdict(set)
    total_with_ref = 0
    files = corpus_files()

    for fp in files:
        body = parse_xml(fp).find('.//%sbody' % TEI)
        if body is None:
            continue
        sigle = fp.name.split('.')[0]
        for w in body.iter('%sw' % TEI):
            ref = w.get('lemmaRef')
            if not ref:
                continue
            total_with_ref += 1
            # Token-genau (CONTRACTS.md B.1): whitespace splitten, dann das
            # ganze Token vergleichen. Ein "in"-Test auf der Zeichenkette
            # wuerde lemma_308 in lemma_3089 finden.
            for tok in ref.split():
                lid = tok.split('#')[-1]
                if lid in candidates:
                    tokens[lid] += 1
                    texts[lid].add(sigle)
    return tokens, texts, total_with_ref, len(files)


def beleg_class(n):
    for lo, hi, label in BELEG_CLASSES:
        if n >= lo and (hi is None or n <= hi):
            return label
    return None


def print_report(concepts, candidates, tokens, texts, total_with_ref, n_files,
                 n_lemmata_total, top):
    attested = {k: v for k, v in candidates.items() if tokens[k] > 0}
    unattested = len(candidates) - len(attested)
    total_tokens = sum(tokens[k] for k in candidates)

    print('#28 Gleis 1: Kandidatenmenge aus dem Begriffssystem')
    print('=' * 62)
    root_name = concepts.get(ROOT_CONCEPT, ROOT_CONCEPT)
    print('Wurzel        : %s (%s)' % (ROOT_CONCEPT, root_name))
    print('Kategorien    : %d benannte Sprachen plus die Wurzel selbst'
          % (len(concepts) - 1))
    print('Korpusdateien : %d' % n_files)
    print()

    print('-- Kategorien (Lemmata je Kategorie, Mehrfachzuordnung moeglich) --')
    per_concept = Counter()
    for c in candidates.values():
        for lang in c['languages']:
            per_concept[lang] += 1
    for lang, n in sorted(per_concept.items(), key=lambda kv: (-kv[1], kv[0])):
        # Die Wurzel ist keine Sprache, sondern die unspezifische Zuordnung
        # "irgendeine Einzelsprache". Sie steht in derselben Spalte und darf
        # nicht wie Lateinisch oder Arabisch gelesen werden.
        mark = '  (Wurzel, keine Einzelsprache)' if lang == root_name else ''
        print('  %-22s %6d%s' % (lang, n, mark))
    print()

    print('-- Menge --')
    print('  Lemmata mit Sprachkonzept : %d von %d (%.2f %%)'
          % (len(candidates), n_lemmata_total, 100.0 * len(candidates) / n_lemmata_total))
    print('  davon im Korpus belegt    : %d' % len(attested))
    print('  davon unbelegt            : %d' % unattested)
    print('  Tokens ueber @lemmaRef    : %d von %d (%.2f %%)'
          % (total_tokens, total_with_ref, 100.0 * total_tokens / total_with_ref))
    print()

    names = {k: v for k, v in attested.items() if v['is_name']}
    plain = {k: v for k, v in attested.items() if not v['is_name']}
    name_tokens = sum(tokens[k] for k in names)
    plain_tokens = sum(tokens[k] for k in plain)
    print('  Eigennamen (NAM)          : %d Lemmata, %d Tokens' % (len(names), name_tokens))
    print('  ohne NAM                  : %d Lemmata, %d Tokens' % (len(plain), plain_tokens))
    print()

    print('-- Belegklassen, ohne Eigennamen --')
    print('  %-12s %8s %10s' % ('Belege', 'Lemmata', 'Tokens'))
    for lo, hi, label in BELEG_CLASSES:
        sel = [k for k in plain if beleg_class(tokens[k]) == label]
        print('  %-12s %8d %10d' % (label, len(sel), sum(tokens[k] for k in sel)))
    hand = [k for k in plain if tokens[k] >= HAND_REVIEW_FROM]
    rest = [k for k in plain if tokens[k] < HAND_REVIEW_FROM]
    hand_tokens = sum(tokens[k] for k in hand)
    print()
    print('  ab %d von Hand : %d Lemmata, %d Tokens (%.1f %% der Nicht-Namen-Tokens)'
          % (HAND_REVIEW_FROM, len(hand), hand_tokens,
             100.0 * hand_tokens / plain_tokens if plain_tokens else 0.0))
    print('  darunter       : %d Lemmata, %d Tokens'
          % (len(rest), sum(tokens[k] for k in rest)))
    print()

    only_lang = [k for k, v in candidates.items() if v['lang_concepts'] == v['concepts_total']]
    print('-- Konzeptdichte --')
    print('  Lemmata, die ausschliesslich Sprachkonzepte tragen: %d' % len(only_lang))
    print('  (ein Schwellwert darueber taugt nicht als Filter)')
    print()

    print('-- Die %d belegstaerksten Nicht-Namen (Handpruefung) --' % top)
    print('  %-20s %8s %7s  %s' % ('Lemma', 'Tokens', 'Texte', 'Sprachkonzepte'))
    for k in sorted(plain, key=lambda k: -tokens[k])[:top]:
        c = candidates[k]
        print('  %-20s %8d %7d  %s'
              % (c['lemma'][:20], tokens[k], len(texts[k]), ', '.join(c['languages'])))


def write_csv(path, candidates, tokens, texts):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Trennzeichen und BOM wie in ingest/wzb/235-breve/diff-liste.csv: die
    # Listen werden in Excel geoeffnet, und ohne BOM zerlegt Excel die Umlaute.
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['lemma_id', 'lemma', 'normalisiert', 'pos', 'pos_alle',
                         'ist_name', 'sprachkonzepte', 'konzepte_gesamt',
                         'belege', 'texte', 'belegklasse', 'handpruefung'])
        for k in sorted(candidates, key=lambda k: (-tokens[k], candidates[k]['normalized'])):
            c = candidates[k]
            n = tokens[k]
            writer.writerow([
                c['id'], c['lemma'], c['normalized'], c['pos'], ' '.join(c['posAll']),
                'ja' if c['is_name'] else 'nein',
                ', '.join(c['languages']), c['concepts_total'],
                n, len(texts[k]), beleg_class(n) or '0',
                'ja' if (n >= HAND_REVIEW_FROM and not c['is_name']) else 'nein',
            ])


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--top', type=int, default=25,
                    help='Wie viele belegstaerkste Nicht-Namen listen (Vorgabe 25)')
    ap.add_argument('--csv', type=Path, default=None,
                    help='Kandidatenliste zusaetzlich als CSV schreiben')
    args = ap.parse_args()

    concepts = language_concepts()
    if not concepts:
        print('FEHLER: %s kommt in %s nicht als <category> vor.'
              % (ROOT_CONCEPT, CONCEPTS_XML.name), file=sys.stderr)
        print('Umbenannt oder entfernt? Ohne die Wurzel gibt es keine Kandidatenmenge,'
              ' und eine leere Liste waere hier kein Befund, sondern ein Ausfall.',
              file=sys.stderr)
        return 1
    candidates, n_lemmata_total = candidate_lemmata(concepts)
    tokens, texts, total_with_ref, n_files = corpus_counts(candidates)

    print_report(concepts, candidates, tokens, texts, total_with_ref, n_files,
                 n_lemmata_total, args.top)

    if args.csv:
        write_csv(args.csv, candidates, tokens, texts)
        print()
        print('CSV geschrieben: %s (%d Zeilen)' % (args.csv, len(candidates)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
