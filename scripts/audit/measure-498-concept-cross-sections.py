#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#498: Querschnittsbegriffe im Begriffssystem messen (read-only).

Kontext: Ein Thema wie "Wachsamkeit" hat keinen eigenen Begriff, steckt aber
in Bedeutungen, die einen Grundbegriff (hier "Aufmerksamkeit") zusammen mit
einer zweiten Achse tragen (Kriegswesen, Ordnungsmacht, Aemter ...). Dieses
Skript misst das generisch, fuer jeden Grundbegriff und jede Achsenwahl. Es
aendert nichts.

Drei Modi, einzeln oder zusammen:

  --base C --axes A B ...   Schnittmenge: Bedeutungen mit C und mindestens einer
                            Achse, je Achse gezaehlt und als Kandidatenliste
                            nach Token sortiert.
  --pairs                   Alle Begriffspaare, die an mindestens --min-support
                            Bedeutungen gemeinsam stehen und nicht in einer
                            Hierarchielinie liegen, gereiht nach PMI. Mit --base
                            zusaetzlich der Rang jedes Paars mit C.
  --spread                  Streuung der Mitbegriffe je Begriff (Entropie), fuer
                            Begriffe mit mindestens --min-senses Bedeutungen.

## Messvorschrift

**Eine Bedeutung ist ein <sense> in lexicon.xml, gezaehlt je xml:id.** Ihre
Begriffe sind die ptr/@target darunter. Bedeutungsangaben (def, gloss) gibt es
praktisch keine (am 28.09.2026: 1 def und 1 note unter 62.202 sense), deshalb
arbeitet alles hier auf den Begriffsverweisen und nicht auf Text.

**Token sind die <w> im Korpus, deren @ana auf die Bedeutung zeigt**, ueber
corpus_files(). @ana kann mehrere Verweise tragen; jeder zaehlt.

**"Nicht in einer Linie" heisst: keiner der beiden Begriffe ist Vorfahr des
anderen** ueber ptr[@type="broader"], transitiv und mit Mehrfach-Oberbegriffen.
Sonst dominieren Paare wie Obstbaeume x Obst, die das System bereits kennt.

**PMI = log2(k * N / (nA * nB))**, k gemeinsame Bedeutungen, N alle
Bedeutungen, nA und nB die Bedeutungen je Begriff. Ohne Mindeststuetze
gewinnen seltene Paare mit k = 1; deshalb --min-support.

## Stand 28.09.2026 (Issue #498)

Mit den Standardwerten: 143 von 652 Bedeutungen unter Aufmerksamkeit tragen
mindestens eine der sieben Achsen, 1.776 von 16.099 Token, 272 Texte. Im
Paar-Ranking steht Aufmerksamkeit x Kriegswesen auf Rang 2.114 von 3.470
(PMI 0,9): die Statistik findet den Fall nicht von selbst. Ein Lauf gegen einen
spaeteren Datenstand gibt andere Zahlen aus, und das ist kein Defekt.

Usage:
    python scripts/audit/measure-498-concept-cross-sections.py            # Wachsamkeits-Beispiel
    python scripts/audit/measure-498-concept-cross-sections.py --pairs --spread
    python scripts/audit/measure-498-concept-cross-sections.py --base concept_22650000 \\
        --axes concept_23240000 concept_24340000 --top 30
"""
import argparse
import io
import math
import re
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
from corpus_files import corpus_files  # noqa: E402

# Konvention in scripts/audit/ (#329): Lemmata mit MHG-Zeichen ausserhalb von
# cp1252 wuerden eine Windows-Konsole an der eigenen Ausgabe scheitern lassen.
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

TEI = '{http://www.tei-c.org/ns/1.0}'
XMLID = '{http://www.w3.org/XML/1998/namespace}id'
XMLLANG = '{http://www.w3.org/XML/1998/namespace}lang'
CONCEPTS = PROJECT_ROOT / 'authority-files' / 'concepts.xml'
LEXICON = PROJECT_ROOT / 'authority-files' / 'lexicon.xml'

# Das Wachsamkeits-Beispiel aus #498. Die Achsen sind ein Vorschlag, keine
# Festlegung; welche dazugehoeren, ist dort Frage 2.
DEFAULT_BASE = 'concept_22650000'           # Aufmerksamkeit
DEFAULT_AXES = [
    'concept_23240000',                     # Kriegswesen/Kampf/Gewalt
    'concept_24340000',                     # Ordnungsmacht
    'concept_23310200',                     # Aemter
    'concept_23250000',                     # Burg
    'concept_21080000',                     # Schlaf
    'concept_23134000',                     # Frauendienst
    'concept_23133000',                     # Hilfeleistung/Widerstand
]

ANA_RE = re.compile(r'<w\b[^>]*?\bana="([^"]*)"')


def load_concepts():
    """{id: deutscher Term}, {id: direkte Oberbegriffe}."""
    names, parents = {}, defaultdict(set)
    for cat in etree.parse(str(CONCEPTS)).iter(TEI + 'category'):
        cid = cat.get(XMLID)
        de = [t.text for t in cat.iterfind(TEI + 'catDesc/' + TEI + 'term')
              if t.get(XMLLANG) == 'de' and t.get('type') is None]
        names[cid] = de[0] if de else '?'
        for p in cat.iterfind(TEI + 'catDesc/' + TEI + 'ptr'):
            if p.get('type') == 'broader':
                parents[cid].add(p.get('target').lstrip('#'))
    return names, parents


def ancestors(cid, parents):
    """Alle Vorfahren ueber broader, iterativ. Die Hierarchie ist nicht zyklenfrei
    (siehe find_cycles), eine Rekursion ohne Besucht-Menge laeuft dort endlos."""
    seen, stack = set(), list(parents.get(cid, ()))
    while stack:
        p = stack.pop()
        if p not in seen:
            seen.add(p)
            stack.extend(parents.get(p, ()))
    return seen


def find_cycles(names, parents):
    """Begriffe, die ueber broader wieder bei sich selbst ankommen."""
    return sorted(c for c in names if c in ancestors(c, parents))


def load_senses():
    """{sense_id: frozenset(concept_ids)}, {sense_id: Lemma-Schreibung}."""
    concepts_of, lemma_of = {}, {}
    for entry in etree.parse(str(LEXICON)).iter(TEI + 'entry'):
        orth = entry.findtext(TEI + 'form/' + TEI + 'orth')
        for sense in entry.iterfind(TEI + 'sense'):
            sid = sense.get(XMLID)
            if sid in concepts_of:
                raise SystemExit(f'Doppelte sense-ID in lexicon.xml: {sid}')
            concepts_of[sid] = frozenset(
                p.get('target').split('#')[-1] for p in sense.iterfind(TEI + 'ptr'))
            lemma_of[sid] = orth
    return concepts_of, lemma_of


def count_tokens(known):
    """Token und Texte je Bedeutung aus w/@ana. Regex statt Baum: nur @ana zaehlt."""
    tokens, texts = Counter(), defaultdict(set)
    files = corpus_files()
    unknown = 0
    for f in files:
        sig = f.name.split('.')[0]
        for m in ANA_RE.finditer(f.read_text(encoding='utf-8')):
            for ref in m.group(1).split():
                sid = ref.split('#')[-1]
                if sid in known:
                    tokens[sid] += 1
                    texts[sid].add(sig)
                else:
                    unknown += 1
    print(f'Korpus: {len(files)} Dateien, {sum(tokens.values()):,} Token mit aufloesbarer '
          f'Bedeutung, {unknown:,} @ana-Verweise ohne Bedeutung in lexicon.xml')
    return tokens, texts


def cross_section(base, axes, names, concepts_of, lemma_of, tokens, texts, top):
    for c in [base, *axes]:
        if c not in names:
            raise SystemExit(f'Unbekannter Begriff: {c}')
    under = [s for s, cs in concepts_of.items() if base in cs]
    hits = [s for s in under if concepts_of[s] & set(axes)]
    tok_under = sum(tokens[s] for s in under)
    print(f'\n## Schnittmenge {names[base]} ({base}) x mind. eine von {len(axes)} Achsen\n')
    print(f'Bedeutungen: {len(hits)} von {len(under)} | '
          f'Lemmata: {len({lemma_of[s] for s in hits})} von {len({lemma_of[s] for s in under})} | '
          f'Token: {sum(tokens[s] for s in hits):,} von {tok_under:,} | '
          f'Texte: {len(set().union(*(texts[s] for s in hits))) if hits else 0} von {len(corpus_files())}')
    print('\nJe Achse (eine Bedeutung kann mehrere tragen, die Zeilen summieren nicht):')
    for a in axes:
        ss = [s for s in hits if a in concepts_of[s]]
        print(f'  {len(ss):>4} Bedeutungen  {sum(tokens[s] for s in ss):>6,} Token  {names[a]} ({a})')
    print(f'\nKandidaten nach Token (Top {top} von {len(hits)}):')
    for s in sorted(hits, key=lambda s: (-tokens[s], s))[:top]:
        ax = ', '.join(names[a] for a in axes if a in concepts_of[s])
        print(f'  {tokens[s]:>5} Tok {len(texts[s]):>4} Txt  {lemma_of[s]:<18} {s:<28} {ax}')


def pairs(base, names, parents, concepts_of, min_support, top):
    n = len(concepts_of)
    single = Counter(c for cs in concepts_of.values() for c in cs)
    together = Counter()
    for cs in concepts_of.values():
        together.update(combinations(sorted(cs), 2))
    anc = {c: ancestors(c, parents) for c in single}
    rows = []
    for (a, b), k in together.items():
        if k < min_support:
            continue
        if a in anc[b] or b in anc[a]:
            continue
        rows.append((math.log2(k * n / (single[a] * single[b])), k, a, b))
    rows.sort(key=lambda r: (-r[0], -r[1], r[2], r[3]))
    print(f'\n## Begriffspaare nach PMI\n')
    print(f'Nenner: {n:,} Bedeutungen | Paare mit >= 1 gemeinsamen Bedeutung: {len(together):,} | '
          f'davon mit >= {min_support} und nicht in einer Linie: {len(rows):,}')
    print(f'\nTop {top} von {len(rows):,} (k gemeinsam; in Klammern Bedeutungen je Begriff):')
    for pmi, k, a, b in rows[:top]:
        print(f'  PMI {pmi:4.1f}  k {k:>4}  {names[a]} ({single[a]})  x  {names[b]} ({single[b]})')
    if base:
        print(f'\nPaare mit {names[base]}, Rang von {len(rows):,}:')
        for i, (pmi, k, a, b) in enumerate(rows, 1):
            if base in (a, b):
                other = b if a == base else a
                print(f'  Rang {i:>5}  PMI {pmi:4.1f}  k {k:>4}  {names[other]} ({other})')


def spread(base, names, concepts_of, tokens, min_senses, top):
    senses_of = defaultdict(list)
    for s, cs in concepts_of.items():
        for c in cs:
            senses_of[c].append(s)
    rows = []
    for c, ss in senses_of.items():
        if len(ss) < min_senses:
            continue
        co = Counter(d for s in ss for d in concepts_of[s] if d != c)
        tot = sum(co.values())
        h = -sum(k / tot * math.log2(k / tot) for k in co.values()) if tot else 0.0
        strong = sum(1 for k in co.values() if k / len(ss) >= 0.05)
        rows.append((h, c, len(ss), sum(tokens[s] for s in ss), len(co), strong))
    rows.sort(key=lambda r: (-r[0], r[1]))
    print(f'\n## Streuung der Mitbegriffe (Begriffe mit >= {min_senses} Bedeutungen: '
          f'{len(rows)} von {len(senses_of)} verwendeten)\n')
    print('Rang | Entropie | Begriff | Bedeutungen | Token | Mitbegriffe | davon an >= 5 % der Bedeutungen')
    for i, (h, c, ns, t, nco, strong) in enumerate(rows[:top], 1):
        print(f'{i:>4} | {h:5.2f} | {names[c]} ({c}) | {ns:,} | {t:,} | {nco} | {strong}')
    if base:
        ranks = [i for i, r in enumerate(rows, 1) if r[1] == base]
        print(f'\nRang {names[base]}: {ranks[0] if ranks else "nicht im Nenner"} von {len(rows)}')


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--base', default=DEFAULT_BASE, help='Grundbegriff (default: Aufmerksamkeit)')
    ap.add_argument('--axes', nargs='+', default=DEFAULT_AXES, help='Achsenbegriffe fuer die Schnittmenge')
    ap.add_argument('--pairs', action='store_true', help='Paar-Ranking nach PMI')
    ap.add_argument('--spread', action='store_true', help='Streuung der Mitbegriffe je Begriff')
    ap.add_argument('--min-support', type=int, default=15, help='Mindestzahl gemeinsamer Bedeutungen je Paar')
    ap.add_argument('--min-senses', type=int, default=100, help='Mindestzahl Bedeutungen fuer --spread')
    ap.add_argument('--top', type=int, default=40)
    args = ap.parse_args()

    names, parents = load_concepts()
    concepts_of, lemma_of = load_senses()
    print(f'Begriffe: {len(names)} | Bedeutungen: {len(concepts_of):,}')
    cyc = find_cycles(names, parents)
    print(f'Begriffe auf einem broader-Zyklus: {len(cyc)} von {len(names)}'
          + ''.join(f'\n  {c} {names[c]} -> broader {sorted(parents[c])}' for c in cyc))

    # Die Schnittmenge laeuft immer, die beiden Ranglisten nur auf Anfrage;
    # nur die Schnittmenge und --spread brauchen den Korpuslauf.
    tokens, texts = count_tokens(set(concepts_of))
    cross_section(args.base, args.axes, names, concepts_of, lemma_of, tokens, texts, args.top)
    if args.pairs:
        pairs(args.base, names, parents, concepts_of, args.min_support, args.top)
    if args.spread:
        spread(args.base, names, concepts_of, tokens, args.min_senses, args.top)
    return 0


if __name__ == '__main__':
    sys.exit(main())
