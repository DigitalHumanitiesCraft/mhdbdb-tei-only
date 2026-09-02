#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""#259: unsere dreistufige Lemma-Aufloesung gegen den Findebuch-Verweisgraph.

Das Findebuch zum mittelhochdeutschen Wortschatz (Trier, TEI-P5-Konversion von
2017) ist eine unabhaengig kuratierte Abbildung belegter Schreibformen auf
normalisierte Lemmata. Es ist hier **Pruefinstrument, keine Datenquelle**:
gemessen wird, wo unsere Aufloesung danebengreift, nichts wird uebernommen und
nichts korrigiert.

## Die Lizenzregel hat Vorrang vor jedem Ergebnis

Die Trierer Daten stehen unter Copyright 1998 Universitaet Trier, eine offene
Lizenz ist nicht erkennbar. Daraus folgt fuer dieses Skript:

  * **Der Dump wandert nicht ins Repositorium**, und die Befundliste, die
    dieses Skript schreibt, auch nicht. Die Vorgabe fuer --out zeigt deshalb
    nach temp/, das gitignoriert ist. Wer sie woanders hinschreibt, ist selbst
    dafuer verantwortlich, dass sie nicht committet wird.
  * **In einen Issue-Kommentar gehen nur aggregierte Zahlen**, keine
    Wortformen aus dem Dump. Der Report auf stdout ist entsprechend gebaut:
    er zaehlt und nennt keine Schreibform. Beispiele stehen ausschliesslich in
    der CSV.

## Zwei Teilmengen, und die kleinere ist nicht die wichtigere

Der Pruefdatensatz ist nicht die Eintragsebene, sondern die Sublemma-Ebene:
die Paare Schreibform -> Lemma. Brauchbar sind die, deren Findebuch-Lemma wir
selbst fuehren; alles andere ergibt bestenfalls "kennen wir nicht". Diese
Menge zerfaellt in zwei Teile, und das Ticket hat bisher nur den einen
gesehen.

**Teil 1, "beide Seiten behaupten etwas":** die Schreibform ist bei uns selbst
ein Lemma und im Findebuch die Variante eines anderen. Hier kann unsere
Stufenfolge auf eine Art danebengreifen, die im Betrieb unsichtbar ist: Stufe
1 (exakter Treffer) greift, bevor Stufe 2 (Variantenwoerterbuch) ueberhaupt
gefragt wird. Wo das Findebuch die Schreibform als Variante fuehrt und wir sie
als eigenes Lemma, gewinnt bei uns immer die Lemma-Lesart, auch wenn
variants.xml dieselbe Zuordnung kennt.

**Genau deshalb testet Teil 1 aber nur Stufe 1, und zwar per Konstruktion.**
Das Auswahlkriterium lautet "die Schreibform ist eines unserer Lemmata", und
das ist die Bedingung, unter der Stufe 1 immer trifft. Gemessen: alle Faelle
in Teil 1 loesen auf Stufe 1 auf, ausnahmslos. Ueber die Stufen 2 und 3, also
ueber das Variantenwoerterbuch und den Praefix-Fallback, sagt diese Teilmenge
nichts.

**Teil 2 ist die Gegenmenge und der eigentliche Test:** die Schreibform ist
bei uns *kein* Lemma, das Findebuch-Lemma aber schon. Dort laeuft die
Aufloesung in Stufe 2 oder 3 und kann gegen ein unabhaengiges Urteil geprueft
werden. Diese Menge ist rund zehnmal so gross wie Teil 1, und sie ist die,
in der die Fehlerklasse aus #224 (Praefix-Fallback) ueberhaupt auftreten
kann. Das Skript weist beide getrennt aus.

## Normalisierung

Unsere Seite ueber scripts/mhg_normalizer.normalize_mhg. Auf die Trierer Seite
kommen davor drei Zusatzregeln (ezh zu z, e-Trema zu e, Bindestrich raus).

**Sie retten hier sehr wohl etwas, anders als die Vorabmessung vom 01.09.
schliesst.** Deren Fazit lautet, die Regeln "kosten nur nichts und retten hier
auch nichts". Gemessen ueber --ohne-trier-regeln: die Paare, deren
Findebuch-Lemma wir fuehren, steigen von 5.081 auf 5.494, und die Faelle, in
denen beide Seiten etwas behaupten, von 424 auf 465. Das sind 41 Faelle oder
knapp ein Zehntel der Befundmenge.

Richtig an der Vorabmessung ist der Teil ueber das ezh: es kommt in den
Findebuch-Lemmaformen null mal vor, waehrend es in der Lexer-Lemmaliste 5.705
mal steht. Die Wirkung kommt vollstaendig vom e-Trema, das in 11 Prozent der
Findebuch-Formen steht. Die Vorabmessung hatte das mit "34,3 auf 37,4 Prozent"
selbst gemessen und im Fazit trotzdem verneint.

Die Regeln gehoeren ausdruecklich **nicht** in assets/js/lib/text-normalizer.js:
das ist unsere Korpus-Normalisierung und darf sich nicht an einer externen
Quelle verbiegen.

## Zwei Fallen des Dumps

Zeile 2 jeder Datei deklariert eine externe TEI-DTD auf tei-c.org. Ohne
no_network=True und load_dtd=False haengt der Lauf am Netz. Und die Dateien
tragen **keinen** Namensraum, anders als unser Korpus: wer mit dem
TEI-Praefix sucht, findet nichts.

Usage:
    python scripts/audit/compare-findebuch-resolution-259.py --dump <pfad>
    python scripts/audit/compare-findebuch-resolution-259.py --dump <pfad> --out temp/259-befunde.csv
    python scripts/audit/compare-findebuch-resolution-259.py --dump <pfad> --ohne-trier-regeln
"""
import argparse
import csv
import gzip
import io
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from lxml import etree

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'scripts'))
from mhg_normalizer import normalize_mhg  # noqa: E402

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ('utf-8', 'utf8'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)

AUTHORITY_INDEX = PROJECT_ROOT / 'data' / 'authority-index.json.gz'
DEFAULT_DUMP = PROJECT_ROOT / 'temp' / 'woerterbuchnetz2015' / 'FindeB' / 'P5'
DEFAULT_OUT = PROJECT_ROOT / 'temp' / '259-findebuch-befunde.csv'

# Mindestlaenge fuer die Richtung "Eingabe beginnt mit Lemma". Muss mit
# MIN_LEMMA_PREFIX_LENGTH in assets/js/lib/lemma-resolve.js uebereinstimmen
# (dieselbe Auflage traegt scripts/audit/measure-stage3-resolution.py).
MIN_LEMMA_PREFIX_LENGTH = 3

# Zusatzregeln fuer die Trierer Schreibung, vor unserer Normalisierung.
TRIER_CHARS = {'ʒ': 'z', 'ë': 'e'}


def trier_normalize(s, apply_rules=True):
    if apply_rules:
        for a, b in TRIER_CHARS.items():
            s = s.replace(a, b)
        s = s.replace('-', '')
    return normalize_mhg(s)


def parse_dump(dump_dir):
    """Die Paare Schreibform -> Lemma aus den Findebuch-Dateien.

    Je <entry> das erste <form type="lemma"> gegen alle <form type="sublemma">.
    Text jeweils ueber itertext(), damit Auszeichnung innerhalb der Form nicht
    verlorengeht (das <ref> mit dem Verweisgraph steht im <form> drin).
    """
    parser = etree.XMLParser(no_network=True, load_dtd=False, resolve_entities=False)
    pairs = []
    entries = 0
    lemma_forms = 0
    reflemma = 0
    with_ref = 0
    files = sorted(dump_dir.glob('*.xml'))
    for fp in files:
        root = etree.parse(str(fp), parser).getroot()
        for entry in root.iter('entry'):
            entries += 1
            lemma = None
            subs = []
            for form in entry.iter('form'):
                t = form.get('type')
                txt = ' '.join(''.join(form.itertext()).split())
                if t == 'lemma':
                    lemma_forms += 1
                    if lemma is None:
                        lemma = txt
                        ref = form.find('.//ref')
                        if ref is not None and ref.get('target'):
                            with_ref += 1
                elif t == 'reflemma':
                    reflemma += 1
                elif t == 'sublemma' and txt:
                    subs.append(txt)
            if lemma:
                for s in subs:
                    pairs.append((s, lemma))
    stats = {'dateien': len(files), 'entries': entries, 'lemma_forms': lemma_forms,
             'reflemma': reflemma, 'with_ref': with_ref}
    return pairs, stats


def load_ours():
    if not AUTHORITY_INDEX.exists():
        print('FEHLER: %s fehlt. Erst den Index bauen.' % AUTHORITY_INDEX, file=sys.stderr)
        sys.exit(2)
    with gzip.open(AUTHORITY_INDEX, 'rt', encoding='utf-8') as fh:
        data = json.load(fh)
    lemmata = data['lemmata']
    variants = data.get('variants', {})
    by_norm = defaultdict(list)
    for l in lemmata:
        if l.get('normalized'):
            by_norm[l['normalized']].append(l)
    return lemmata, variants, by_norm


def stage3(query, lemmata):
    """Stufe 3, gespiegelt aus assets/js/lib/lemma-resolve.js (isStage3Match),
    Rangfolge nach Laengendistanz wie stage3Distance. Der Tiebreak nach Id ist
    eine Messkonvention: produktiv bricht die Hauptseite Gleichstaende gar
    nicht, der Playground nach Korpus-Frequenz."""
    out = []
    for l in lemmata:
        n = l.get('normalized')
        if not n:
            continue
        if n.startswith(query):
            out.append(l)
        elif len(n) >= MIN_LEMMA_PREFIX_LENGTH and query.startswith(n):
            out.append(l)
    return sorted(out, key=lambda l: (abs(len(l['normalized']) - len(query)), l['id']))


def resolve(query, lemmata, variants, by_norm):
    """Die dreistufige Aufloesung, in der Reihenfolge, in der sie produktiv
    laeuft. Rueckgabe: (stufe, liste der Lemma-Ids)."""
    hit = by_norm.get(query)
    if hit:
        return 1, [l['id'] for l in hit]
    v = variants.get(query)
    if v:
        return 2, [v]
    return 3, [l['id'] for l in stage3(query, lemmata)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument('--dump', type=Path, default=DEFAULT_DUMP,
                    help='Verzeichnis mit den 22 Findebuch-XML (Vorgabe: temp/...)')
    ap.add_argument('--out', type=Path, default=DEFAULT_OUT,
                    help='Befundliste als CSV. Vorgabe temp/, gitignoriert. NICHT committen.')
    ap.add_argument('--ohne-trier-regeln', action='store_true',
                    help='Die drei Zusatzregeln weglassen, um ihre Wirkung zu messen')
    args = ap.parse_args()

    if not args.dump.is_dir():
        print('FEHLER: %s ist kein Verzeichnis.' % args.dump, file=sys.stderr)
        print('Der Dump liegt gitignoriert unter temp/ im Hauptbaum, nicht im Worktree.',
              file=sys.stderr)
        return 2

    apply_rules = not args.ohne_trier_regeln
    pairs, stats = parse_dump(args.dump)
    lemmata, variants, by_norm = load_ours()

    print('#259: Findebuch-Verweisgraph gegen unsere dreistufige Aufloesung')
    print('=' * 66)
    print('-- Struktur des Pruefdatensatzes --')
    print('  Dateien                    : %d' % stats['dateien'])
    print('  <entry>                    : %d' % stats['entries'])
    print('  <form type="lemma">        : %d' % stats['lemma_forms'])
    print('  davon mit ref/@target      : %d' % stats['with_ref'])
    print('  <form type="reflemma">     : %d' % stats['reflemma'])
    print('  Paare Schreibform -> Lemma : %d' % len(pairs))
    print('  Trierer Zusatzregeln       : %s' % ('an' if apply_rules else 'aus'))
    print()

    # Beide Seiten normalisiert. Die Findebuch-Seite bekommt die Zusatzregeln,
    # unsere Seite ist bereits normalisiert im Index. Dedupliziert wird auf dem
    # normalisierten Paar: dieselbe Zuordnung zweimal ist ein Befund, nicht zwei.
    both = []          # Teil 1: Schreibform ist bei uns selbst Lemma
    other = []         # Teil 2: Schreibform ist bei uns kein Lemma
    lemma_known = 0
    roh_both = 0
    seen = set()
    for form, lemma in pairs:
        nf = trier_normalize(form, apply_rules)
        nl = trier_normalize(lemma, apply_rules)
        if nl not in by_norm:
            continue
        lemma_known += 1
        key = (nf, nl)
        if nf in by_norm:
            roh_both += 1
        if key in seen:
            continue
        seen.add(key)
        (both if nf in by_norm else other).append((nf, nl, form, lemma))

    print('-- Der Ertrag --')
    print('  Paare, deren Findebuch-Lemma wir fuehren : %d (%.1f %%)'
          % (lemma_known, 100.0 * lemma_known / len(pairs)))
    print('  Teil 1, Schreibform bei uns selbst Lemma : %d (roh %d)'
          % (len(both), roh_both))
    print('  Teil 2, Schreibform bei uns kein Lemma   : %d' % len(other))
    print()

    kat = Counter()
    rows = []
    for nf, nl, form, lemma in both:
        stufe, ids = resolve(nf, lemmata, variants, by_norm)
        ziel_ids = [l['id'] for l in by_norm.get(nl, [])]
        v = variants.get(nf)
        stimmt_ueberein = bool(set(ids) & set(ziel_ids))

        if stufe == 1 and stimmt_ueberein:
            k = 'A gleiches Ziel'
        elif stufe == 1 and v and v in ziel_ids:
            k = 'B Stufe 1 verdeckt Stufe 2'
        elif stufe == 1 and v:
            k = 'C eigenes Lemma, variants zeigt anderswohin'
        elif stufe == 1:
            k = 'D eigenes Lemma, variants kennt die Form nicht'
        elif stufe == 2:
            k = 'E Stufe 2 entscheidet'
        else:
            k = 'F nur Stufe 3'
        kat[k] += 1
        rows.append({
            'kategorie': k, 'stufe': stufe,
            'fb_schreibform': form, 'fb_lemma': lemma,
            'norm_schreibform': nf, 'norm_lemma': nl,
            'unsere_aufloesung': ' '.join(ids[:5]),
            'treffer_gesamt': len(ids),
            'findebuch_ziel': ' '.join(ziel_ids),
            'variants_ziel': v or '',
            'uebereinstimmung': 'ja' if stimmt_ueberein else 'nein',
        })

    print('-- Teil 1: beide Seiten behaupten etwas (%d) --' % len(both))
    for k, n in sorted(kat.items()):
        print('  %-44s %5d' % (k, n))
    stufen = Counter(r['stufe'] for r in rows)
    print('  Aufloesungsstufen dabei: %s' % dict(sorted(stufen.items())))
    print()
    print('Kategorie B ist die interessanteste: dort kennt variants.xml dieselbe')
    print('Zuordnung wie das Findebuch, aber Stufe 1 greift vorher, weil die')
    print('Schreibform bei uns selbst ein Lemma ist. Das ist kein Fehler in den')
    print('Daten, sondern eine Folge der Stufenordnung, und im Betrieb unsichtbar.')
    print()
    print('Und Teil 1 prueft nur Stufe 1, per Konstruktion: das Auswahlkriterium')
    print('ist genau die Bedingung, unter der Stufe 1 trifft. Dafuer Teil 2.')
    print()

    # --- Teil 2: hier laufen Stufe 2 und 3 wirklich ---
    kat2 = Counter()
    for nf, nl, form, lemma in other:
        stufe, ids = resolve(nf, lemmata, variants, by_norm)
        ziel_ids = [l['id'] for l in by_norm.get(nl, [])]
        treffer = set(ids) & set(ziel_ids)
        if stufe == 2 and treffer:
            k = 'G Stufe 2 trifft dasselbe Lemma'
        elif stufe == 2:
            k = 'H Stufe 2 trifft ein anderes Lemma'
        elif stufe == 3 and not ids:
            k = 'K Stufe 3 liefert nichts'
        elif stufe == 3 and ids[0] in ziel_ids:
            k = 'I Stufe 3, bester Treffer stimmt'
        elif stufe == 3 and treffer:
            k = 'J Stufe 3, Ziel dabei aber nicht vorn'
        else:
            k = 'L Stufe 3 verfehlt das Ziel'
        kat2[k] += 1
        rows.append({
            'kategorie': k, 'stufe': stufe,
            'fb_schreibform': form, 'fb_lemma': lemma,
            'norm_schreibform': nf, 'norm_lemma': nl,
            'unsere_aufloesung': ' '.join(ids[:5]),
            'treffer_gesamt': len(ids),
            'findebuch_ziel': ' '.join(ziel_ids),
            'variants_ziel': variants.get(nf) or '',
            'uebereinstimmung': 'ja' if treffer else 'nein',
        })

    print('-- Teil 2: die Schreibform ist bei uns kein Lemma (%d) --' % len(other))
    for k, n in sorted(kat2.items()):
        print('  %-44s %5d' % (k, n))
    trefferquote = sum(n for k, n in kat2.items() if k[0] in 'GI')
    print()
    print('  Stufe 2 und 3 landen in %d von %d Faellen auf dem Findebuch-Lemma'
          % (trefferquote, len(other)))
    print('  (%.1f %%), gerechnet als bester Treffer, nicht als "irgendwo dabei".'
          % (100.0 * trefferquote / len(other) if other else 0.0))
    print()

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open('w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, delimiter=';', fieldnames=list(rows[0].keys()) if rows else ['leer'])
        w.writeheader()
        for r in sorted(rows, key=lambda r: (r['kategorie'], r['norm_schreibform'])):
            w.writerow(r)
    print('Befundliste: %s (%d Zeilen)' % (args.out, len(rows)))
    print('ACHTUNG: enthaelt Trierer Schreibformen. Nicht committen, nicht in')
    print('einen Issue-Kommentar uebernehmen. Nur die Zahlen oben sind frei.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
