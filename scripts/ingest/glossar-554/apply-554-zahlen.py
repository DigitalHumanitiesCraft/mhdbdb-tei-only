#!/usr/bin/env python3
"""#554: historische MHDBDB-Trefferzahlen in Glossarkommentaren durch heutige Messungen ersetzen.

Freigabe: KZW am 16.10.2026 in #554, Abschnitt 4 ("Sie durch heutige Lemmazahlen zu
ersetzen, ist ausdrücklich in Ordnung ... die aktuellen Zahlen sind am heutigen Korpus zu
ermitteln"). Die Zahlen kommen aus `scripts/review/messen-554-zahlen.py` (Zaehlregeln im
Skriptkopf), gemessen am 18.10.2026 nach den Korrekturen aus apply-554-daten.py.

Die Aufteilung "innerhalb der Dichtung" bei wîn und brôt entfaellt: sie hat keine
reproduzierbare Definition. Nicht angefasst: die MPS-Suche bei salse (Klug-Datenbank,
nicht am Korpus messbar) und die "visch + haben"-Aussage (eine Lesung der Stellen, keine
Trefferzahl).

Usage:
    python scripts/ingest/glossar-554/apply-554-zahlen.py           # Trockenlauf
    python scripts/ingest/glossar-554/apply-554-zahlen.py --apply
"""

import io
import re
import sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ROOT = Path(__file__).resolve().parents[3]
APPLY = '--apply' in sys.argv

# (Lemma, orth, alt, neu); jede Ersetzung muss im Eintrag genau einmal treffen
ERSETZUNGEN = [
    ('lemma_1324', 'ei',
     'Auszüge aus 31 Beispielen der MHDBDB (Stand 03.10.2017, Suchstring @niht + @ein + @ei):',
     'Auszüge aus den 31 Verszeilen des Korpus, in denen „niht“, „ein“ und „ei“ in dieser Reihenfolge '
     'stehen (Stand 18.10.2026):'),
    ('lemma_1324', 'ei',
     'Der Suchstring @umbe + @ein + @ei liefert 31 Belege (darunter einige, die nicht mit „niht“ gebildet werden)',
     'Die Folge „umbe“, „ein“, „ei“ in einer Verszeile ist 29-mal belegt (Stand 18.10.2026; darunter einige, '
     'die nicht mit „niht“ gebildet werden)'),
    ('lemma_1383', 'enbîʒen',
     '„hunger“ (4 Belege in der MHDBDB innerhalb von drei Kontextzeilen), „spîse“ (16 Belege innerhalb von '
     'drei Zeilen) und „ezzen“ (9 Belege).',
     '„hunger“ (6 Belege), „spîse“ (18) und „ezzen“ (11), gezählt als Belege von „enbîʒen“, bei denen das '
     'Nahrungswort in derselben oder in einer der drei davor oder dahinter liegenden Verszeilen steht '
     '(Stand 18.10.2026).'),
    ('lemma_22022', 'brâmber',
     '(„rôt + rôse“ innerhalb einer Verszeile liefert mit Stand 04.01.2018 genau 116 Belege in der MHDBDB), '
     'weiße Lilien („wîz + lilje“: 18 Belege), grünen Lauch („grüene + louch“: 3 Belege, alle im '
     '„Trojanischen Krieg“ Konrads von Würzburg) und grünen Fenchel („grüene + venichel“: 1 Beleg im '
     '„Trojanischen Krieg“)',
     '(„rôt“ und „rôse“ stehen im Korpus in 48 Verszeilen zusammen, Stand 18.10.2026), weiße Lilien („wîʒ“ und '
     '„lilje“: 8 Verszeilen), grünen Lauch („grüene“ und „louch“: 3 Verszeilen, alle im „Trojanischen Krieg“ '
     'Konrads von Würzburg) und grünen Fenchel („grüene“ und „venchelkrût“: 1 Verszeile im „Trojanischen '
     'Krieg“)'),
    ('lemma_2954', 'hunger',
     '(71 Belege in der MHDBDB, Stand 28.10.2016)',
     '(24 Belege, in denen „hunger“ unmittelbar vor „nôt“ steht, Stand 18.10.2026)'),
    ('lemma_2954', 'hunger',
     '(84 Belege im Kontext von zwei Zeilen, Stand 28.10.2016)',
     '(35 Belege von „hunger“ mit „durst“ in derselben oder in einer der zwei davor oder dahinter liegenden '
     'Verszeilen, Stand 18.10.2026)'),
    ('lemma_2955', 'hungerc',
     '(41 Textbelege in der MHDBDB, Stand 10.11.2016)',
     '(78 Belege im Korpus, Stand 18.10.2026)'),
    ('lemma_2961', 'huon',
     'die Textstellensuche der MHDBDB findet in 658 Texten 14 Belege (Stand 13.05.2017)',
     'im Korpus steht „huon“ unmittelbar vor „unde“ und „visch“ in 4 Fällen (Stand 18.10.2026)'),
    ('lemma_3122', 'jeroffel',
     'liefert die MHDBDB 245 Treffer von zahlreichen Dichtern (zum Zeitpunkt der Recherche, 08.03.2017, noch '
     'nicht vollständig disambiguiert; einige Treffer, vor allem in der religiösen Dichtung, bezeichnen den '
     'Stift aus Metall oder Holz, oft ist aber die Gewürznelke gemeint)',
     'gibt es im Korpus 257 Belege in 97 Texten (Stand 18.10.2026; einige, vor allem in der religiösen '
     'Dichtung, bezeichnen den Stift aus Metall oder Holz, oft ist aber die Gewürznelke gemeint)'),
    ('lemma_7532', 'wîn',
     'Die Suche nach „wîn und“ (Suchstring „@wîn,unde,*“) in allen 664 Texten der MHDBDB liefert 257 Belege, '
     'innerhalb der Dichtung 98 (Stand 17.11.2017); die umgekehrte Suche nach „und brôt“ („*,unde,brôt“) '
     'ergibt 129 Belege im Gesamtkorpus und 96 in den poetischen Texten.',
     'Im Korpus steht „wîn“ 371-mal unmittelbar vor „und“ und „und“ 200-mal unmittelbar vor „wîn“ '
     '(Stand 18.10.2026).'),
    ('lemma_879', 'brôt',
     'Die Suche nach „brôt und“ (Suchstring „brôt,unde,*“) in allen 664 Texten der MHDBDB liefert 214 Belege, '
     'innerhalb der Dichtung 98 (Stand 17.11.2017); die umgekehrte Suche nach „und brôt“ („*,unde,brôt“) '
     'ergibt 129 Belege im Gesamtkorpus und 96 in den poetischen Texten.',
     'Im Korpus steht „brôt“ 284-mal unmittelbar vor „und“ und „und“ 127-mal unmittelbar vor „brôt“ '
     '(Stand 18.10.2026).'),
]


def main():
    pfad = ROOT / 'authority-files' / 'lexicon.xml'
    with open(pfad, encoding='utf-8', newline='') as fh:
        text = fh.read()
    fehler = []
    for lid, orth, alt, neu in ERSETZUNGEN:
        m = re.search(r'<entry xml:id="' + lid + r'">\s*<form type="lemma">\s*<orth>' + re.escape(orth) +
                      r'</orth>.*?</entry>', text, re.S)
        if not m:
            fehler.append(f'{lid} {orth}: Eintrag nicht gefunden')
            continue
        if m.group(0).count(alt) != 1:
            fehler.append(f'{lid} {orth}: alter Text {m.group(0).count(alt)}x gefunden, erwartet 1: {alt[:60]}')
            continue
        text = text[:m.start()] + m.group(0).replace(alt, neu) + text[m.end():]
    if fehler:
        print('ABBRUCH, nichts geschrieben:')
        for f in fehler:
            print('   ' + f)
        return 1
    if APPLY:
        with open(pfad, 'w', encoding='utf-8', newline='') as fh:
            fh.write(text)
    print(f'{len(ERSETZUNGEN)} Ersetzungen in {len({e[0] for e in ERSETZUNGEN})} Eintraegen'
          + ('' if APPLY else '  [Trockenlauf]'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
