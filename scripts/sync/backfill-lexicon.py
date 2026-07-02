#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backfill lexicon.xml with category-A stubs (Issue #115, Phase 2 — der
automatisierbare Teil).

Konsumiert die Klassifikation aus `scripts/audit/classify-lexicon-backfill.py`
(wird frisch per Subprozess erzeugt) und fuegt fuer jede Kategorie-A-Zeile
(ganzes <entry> fehlt) einen Stub in `authority-files/lexicon.xml` ein:

  - <orth>  = dominante Korpusform (candidate_orth). ACHTUNG: kann eine
              Flexionsform sein — die Grundform-Bestaetigung bleibt
              kuratorisch (KZW), siehe #115-Kommentar 2026-06-01.
  - <pos>   = die Tags des HAEUFIGSTEN @pos-Werts im Korpus als mehrere
              <pos>-Elemente, dominantes zuerst (Praezedenz: 10.167 Bestands-
              eintraege haben mehrere <pos>; der Index-Builder liest das
              erste). Achtung: candidate_pos stammt aus most_common(1) der
              Klassifikation — Tags aus Minderheits-@pos-Werten desselben
              Lemmas werden nicht uebernommen. OHNE
              Korpus-Evidenz (@pos="") wird EIN leeres <pos/> geschrieben —
              schema-valide (text erlaubt leer), aber ohne Praezedenz im
              Bestand; diese Lemmata stehen auf der kuratorischen
              Nachtrag-Liste im PR/Issue.
  - <sense> = alle im Korpus referenzierten dangling Sense-IDs des Lemmas,
              OHNE concept-<ptr> (Konzept-Zuordnung ist kuratorisch,
              CONTRACTS F.2; `check-lexicon-senses.py` haelt sie sichtbar).
              Referenziert der Korpus nur @lemmaRef (kein @ana), wird EINE
              Sense-ID oberhalb des globalen Maximums gemintet (Schema
              verlangt sense+).

Kategorien B (Sense fehlt an existierendem Lemma) und C (Tippfehler/
Homograph) werden bewusst NICHT angefasst — B ist rein kuratorisch, C
verlangt Korpus-Korrektur bzw. Neuanlage-Entscheidung (KZW/Julia).

Einfuege-Strategie: text-basiert an der String-Sortierposition der
xml:id (der Bestand ist string-sortiert: lemma_1, lemma_100, lemma_1000
...), KEIN lxml-Roundtrip der 31-MB-Datei — der Diff bleibt minimal und
reviewbar. Nach dem Einfuegen wird das Ergebnis mit lxml re-geparst
(Wohlgeformtheit) und die Entry-/Stub-Zahl verifiziert.

Nachgelagerte Pflicht-Schritte (Data-Change-Lifecycle, DATA-MODEL.md):
Authority-Index-Rebuild + Versions-Bump, build-api.py, Baseline-Senkung
in check-authority-cross-refs.py, Schema-Validierung.

Usage:
    python scripts/sync/backfill-lexicon.py            # Dry-Run (Report)
    python scripts/sync/backfill-lexicon.py --apply    # schreibt lexicon.xml
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from xml.sax.saxutils import escape

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
LEXICON = PROJECT_ROOT / 'authority-files' / 'lexicon.xml'
CLASSIFY = PROJECT_ROOT / 'scripts' / 'audit' / 'classify-lexicon-backfill.py'
CLASSIFY_JSON = PROJECT_ROOT / 'scripts' / 'audit' / 'lexicon-backfill.json'

ENTRY_RE = re.compile(r'([ \t]*)<entry xml:id="(lemma_\d+)"')


def build_stub(row, indent, minted_sense):
    """Ein A-Row -> eingerückter <entry>-Block (String)."""
    i2 = indent + '  '
    i3 = indent + '    '
    orth = escape(row['candidate_orth'])
    pos_tags = row['candidate_pos'].split() or ['']
    senses = sorted(row['dangling_senses'],
                    key=lambda s: int(s.rsplit('_', 1)[1]))
    if not senses:
        senses = [minted_sense]

    lines = [f'{indent}<entry xml:id="{row["lemma_id"]}">']
    lines.append(f'{i2}<form type="lemma">')
    lines.append(f'{i3}<orth>{orth}</orth>')
    lines.append(f'{i2}</form>')
    lines.append(f'{i2}<gramGrp>')
    for tag in pos_tags:
        lines.append(f'{i3}<pos>{escape(tag)}</pos>' if tag else f'{i3}<pos/>')
    lines.append(f'{i2}</gramGrp>')
    for sid in senses:
        lines.append(f'{i2}<sense xml:id="{sid}"/>')
    lines.append(f'{indent}</entry>')
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(
        description='Kategorie-A-Stubs in lexicon.xml einfuegen (#115).')
    parser.add_argument('--apply', action='store_true',
                        help='lexicon.xml wirklich schreiben (sonst Dry-Run)')
    parser.add_argument('--skip-classify', action='store_true',
                        help='NUR Debug: vorhandenes lexicon-backfill.json '
                             'verwenden. Ein stales JSON kann Orphan-Stubs '
                             'einfuegen (Lemma inzwischen anderweitig '
                             'aufgeloest) — fuer --apply immer frisch '
                             'klassifizieren lassen')
    args = parser.parse_args()

    if not args.skip_classify:
        print('Klassifikation frisch erzeugen (classify-lexicon-backfill.py) ...')
        proc = subprocess.run([sys.executable, str(CLASSIFY)],
                              cwd=PROJECT_ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            # classify meldet Fehler via print auf stdout — nicht verschlucken
            sys.exit(f'FEHLER: Klassifikation fehlgeschlagen (exit '
                     f'{proc.returncode}):\n{proc.stdout}\n{proc.stderr}')
    rows = json.loads(CLASSIFY_JSON.read_text(encoding='utf-8'))['rows']
    a_rows = sorted((r for r in rows if r['category'] == 'A_MISSING_ENTRY'),
                    key=lambda r: r['lemma_id'])
    if not a_rows:
        print('Keine Kategorie-A-Lücken — nichts zu tun.')
        return 0

    text = LEXICON.read_text(encoding='utf-8')

    # Bestand: Positionen + xml:ids aller Entries (string-sortiert im File).
    entries = [(m.start(), m.group(1), m.group(2)) for m in ENTRY_RE.finditer(text)]
    existing_ids = {e[2] for e in entries}
    indent = entries[0][1]

    # Die Einfuege-Logik setzt String-Sortierung des Bestands voraus; der
    # Bestand verletzt sie bereits an einer Stelle (WZB-Block lemma_78608-
    # 78688 vor lemma_7861). Warnen statt failen: Stubs in einer verletzten
    # Zone landen an der Position der ERSTEN groesseren ID in Dateireihenfolge.
    id_seq = [e[2] for e in entries]
    violations = sum(1 for a, b in zip(id_seq, id_seq[1:]) if a > b)
    if violations:
        print(f'WARNUNG: lexicon.xml ist an {violations} Stelle(n) nicht '
              f'string-sortiert — Stub-Positionen in diesen Zonen folgen der '
              f'Dateireihenfolge, nicht der reinen String-Sortierung.')

    dupes = [r['lemma_id'] for r in a_rows if r['lemma_id'] in existing_ids]
    if dupes:
        sys.exit(f'FEHLER: {len(dupes)} A-Lemmata existieren bereits in '
                 f'lexicon.xml (Klassifikation stale?): {dupes[:5]} ...')

    # Sense-Minting oberhalb des globalen Maximums (lexicon + Korpus-dangling).
    max_lex_sense = max(int(m) for m in re.findall(r'_sense_(\d+)"', text))
    max_dangling = max((int(s.rsplit('_', 1)[1])
                        for r in rows for s in r['dangling_senses']),
                       default=0)
    next_sense = max(max_lex_sense, max_dangling) + 1

    # Ende eines Entry-Blocks finden: schliessendes </entry> nach Position.
    close_tag = f'{indent}</entry>\n'

    minted = []
    out_parts, cursor = [], 0
    stubs_todo = list(a_rows)
    for pos, _ind, xid in entries:
        while stubs_todo and stubs_todo[0]['lemma_id'] < xid:
            row = stubs_todo.pop(0)
            mint = None
            if not row['dangling_senses']:
                mint = f'{row["lemma_id"]}_sense_{next_sense}'
                minted.append(mint)
                next_sense += 1
            out_parts.append(text[cursor:pos])
            out_parts.append(build_stub(row, indent, mint))
            cursor = pos
    # Rest (ids > letzter Bestand): vor dem schliessenden Tag des letzten Entry.
    if stubs_todo:
        last_close = text.rindex(close_tag) + len(close_tag)
        out_parts.append(text[cursor:last_close])
        cursor = last_close
        for row in stubs_todo:
            mint = None
            if not row['dangling_senses']:
                mint = f'{row["lemma_id"]}_sense_{next_sense}'
                minted.append(mint)
                next_sense += 1
            out_parts.append(build_stub(row, indent, mint))
    out_parts.append(text[cursor:])
    result = ''.join(out_parts)

    no_pos = [r['lemma_id'] for r in a_rows if not r['candidate_pos'].strip()]
    inserted = len(a_rows)  # Dupes-Check garantiert: jede A-Row genau einmal
    print(f'Kategorie-A-Stubs:        {inserted}')
    print(f'  davon ohne POS-Evidenz: {len(no_pos)} (leeres <pos/>, kuratorischer Nachtrag)')
    if minted:
        print(f'  gemintete Sense-IDs:    {len(minted)} (ab _sense_{next_sense - len(minted)})')
    else:
        print('  gemintete Sense-IDs:    0')
    print(f'  Senses ohne concept:    '
          f'{sum(len(r["dangling_senses"]) for r in a_rows) + len(minted)} (kuratorisch, check-lexicon-senses.py)')

    if not args.apply:
        print('\nDry-Run — nichts geschrieben. Mit --apply anwenden.')
        return 0

    # Wohlgeformtheits- und Zaehl-Verifikation VOR dem Schreiben.
    from lxml import etree
    root = etree.fromstring(result.encode('utf-8'))
    new_count = len(root.findall('.//{http://www.tei-c.org/ns/1.0}entry'))
    old_count = len(entries)
    if new_count != old_count + inserted:
        sys.exit(f'FEHLER: Entry-Zahl nach Einfuegen {new_count}, erwartet '
                 f'{old_count + inserted} — nichts geschrieben.')

    # newline='': ohne das uebersetzt der Text-Modus '\n' -> os.linesep und
    # wuerde unter Windows die komplette 31-MB-Datei auf CRLF umschreiben —
    # Riesen-Diff, deterministische Builds (#125) und Freshness-Gate kaputt.
    with open(LEXICON, 'w', encoding='utf-8', newline='') as f:
        f.write(result)
    print(f'\nGeschrieben: {LEXICON} ({old_count} -> {new_count} entries)')
    print('Naechste Schritte (Data-Change-Lifecycle): Authority-Index-Rebuild '
          '+ Bump, build-api.py, Baseline in check-authority-cross-refs.py '
          'senken, validate-corpus.py.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
