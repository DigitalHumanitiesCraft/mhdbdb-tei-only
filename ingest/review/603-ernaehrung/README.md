# #603: Ernährung von Menschen oder von Tieren (concept_21111000)

Prüfliste zu [#603](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/603), Stand 16.10.2026. **Prüfmaterial, keine Entscheidung.** Nichts davon steht in `authority-files/` oder `tei/`, und welches Konzept für die Ernährung von Tieren gilt, entscheidet KZW.

## Die Frage

KZW am 15.10.2026 zu den Fällen abebîʒen (A-432) und lëcken (A-1146) aus #554: Alle Belege, die „Objektbezogene Aktivität/Tätigkeit · Ernährung von Menschen“ bezeichnen, sind zu prüfen, ob wirklich immer Menschen gemeint sind oder auch Tiere. Im Kommentar vom 15.10.2026 in #603 fügt sie an: „dann sollten wir wirklich alle Belege, die mit menschlicher Ernährung annotiert sind, systematisch prüfen. Erst Claude alle, die er automatisiert schafft - dann der Rest als EIL-Prüfung.“ Die Dateien hier sind der automatisierte Teil.

## Was die Dateien sind und was nicht

**Die Klasse `tier` ist eine Prüfliste, keine Feststellung.** Sie sagt: im Umkreis des Belegs steht ein Wort, das nach Konzept oder Lemma ein Tier nennt. Sie sagt nicht, dass das Tier die Nahrung aufnimmt. In Stichprobe 1 trifft die Klasse bei 4 von 10 Belegen (siehe unten). Die Klassen `mensch` und `unklar` sind ebenso Vorsortierung und kein Urteil.

| Datei | Inhalt | Zeilen |
|---|---|--:|
| `senses-21111000.tsv` | jede Bedeutung mit `concept_21111000` (Lexikon, `ptr`), mit der Zahl ihrer Belege je Klasse | 485 |
| `belege-tier.tsv` | alle Belege der Klasse `tier`, mit und ohne `@ana` | 2.867 |
| `lemmata-ohne-ana.tsv` | je Lemma dieser Bedeutungen die Belege ohne `@ana`, nach Klasse | 471 |
| `faelle-abebizen-lecken.tsv` | alle Belege der beiden Lemmata, maschinelle Klasse und Handurteil | 39 |
| `manuell-faelle.tsv` | **Eingabe:** die Handurteile zu diesen 39 Belegen (`w_id`, `urteil`, `begruendung`), von einem Agenten gelesen, nicht von KZW | 39 |
| `konzepte-tier.tsv` | 28 Konzepte (Tier- und Nachbarkonzepte) mit Zahl der Bedeutungen im Lexikon und davon zusammen mit 21111000 | 28 |
| `stichprobe.tsv` | Stichprobe 1: je Klasse 10 Belege, Seed 603 | 30 |
| `stichprobe2-tier-ohne-mensch.tsv` | Stichprobe 2: 10 Belege der Klasse `tier` ohne Mensch-Treffer, Seed 604 | 10 |
| `stichprobe-urteile.tsv` | **Eingabe:** die Urteile zu beiden Stichproben (40 Zeilen), von einem Agenten gelesen | 40 |
| `zusammenfassung.txt` | Zählung des Laufs, Quelle der Zahlen unten | |

Nicht im Repo, weil regenerierbar: `alle-belege-vorsortiert.tsv` (7,5 MB, alle vorsortierten Belege; `stichprobe2-603.py` liest sie).

## Die Grundmengen

Stand des Lexikons und des Korpus bei dem Lauf (`zusammenfassung.txt`): 667 Dateien, 9.431.295 `<w>`; 62.198 Bedeutungen im Lexikon, davon 485 mit `concept_21111000` (alle verschieden), auf 471 Lemmata.

- **Belege mit `@ana` auf eine dieser Bedeutungen** (je `<w>` einmal gezählt): **11.491**. Davon Klasse `tier` 1.223, `mensch` 7.745, `unklar` 2.523 (1.223 + 7.745 + 2.523 = 11.491). 361 der 485 Bedeutungen haben mindestens einen solchen Beleg, 124 keinen.
- **Belege ohne `@ana` bei einem der 471 Lemmata**: **21.667**, davon `tier` 1.644, `mensch` 15.649, `unklar` 4.374. Sie sind nicht einer Bedeutung zugeordnet, die Klasse beruht allein auf dem Lemma. Das ist die größere Menge, und sie ist unsicherer.
- `belege-tier.tsv` führt beide `tier`-Mengen zusammen: 2.867 = 1.223 mit `@ana` + 1.644 ohne.

## Die Regeln der Vorsortierung

Für jeden Beleg werden die Wörter im Fenster von acht links und acht rechts angesehen (der Beleg selbst nicht).

| Regel | Treffer, wenn ein Wort im Fenster ... |
|---|---|
| T1 | per `@ana` eine Bedeutung mit einem der 28 Tierkonzepte trägt und diese Bedeutung kein Lebensmittelkonzept (Teilbaum 21111300, 9 Konzepte) hat |
| T2 | kein `@ana` hat und sein Lemma irgendeine Bedeutung mit Tierkonzept und keine mit Lebensmittelkonzept hat |
| M1 | eines der Pronomen ich, wir, du, ir mit `@pos` PRO ist |
| M2 | per `@ana` eine Bedeutung mit einem Menschkonzept trägt (13 Konzepte: Teilbäume 21010000, 21103000, 23112000, 23112500) |
| M3 | kein `@ana` hat und sein Lemma irgendeine Bedeutung mit Menschkonzept hat |

Trägt die Bedeutung eines Fensterworts ein Tier- und ein Lebensmittelkonzept, zählt das Wort nicht (Fleisch, Speisen). **Klasse:** `tier`, wenn mindestens ein T-Treffer; sonst `mensch`, wenn mindestens ein M-Treffer; sonst `unklar`. Ein Mensch-Treffer hebt einen Tier-Treffer also nicht auf: von den 1.223 `tier`-Belegen mit `@ana` haben 943 auch einen Mensch-Treffer und 280 keinen (Spalte `tier_und_mensch_treffer`).

Gezählt an den 11.491 Belegen mit `@ana` (ein Beleg kann mehrere Regeln auslösen): M1 2.875, M2 5.863, M3 2.962, T1 926, T2 347.

Die Tierkonzepte sind eine feste Liste von 28 Konzepten (Säugetiere, Vögel, Fische, Reptilien und weitere, mit den zugehörigen Namenskonzepten; Körper, Organe, Stoffwechsel, Verarbeitung, Krankheiten und Zucht sind ausgeschlossen). Die Liste steht in `zusammenfassung.txt` und in `scripts/review/vorsortieren-603.py`; `konzepte-tier.tsv` zeigt sie neben Nachbarkonzepten, die nicht auf ihr stehen.

## Der Fall abebîʒen und lëcken

`faelle-abebizen-lecken.tsv`: 39 Belege (lëcken 36, abebîʒen 3). Maschinell: `mensch` 22, `tier` 13, `unklar` 4. Handurteil (`manuell-faelle.tsv`): `mensch` 17, `tier` 16, `unklar` 6. Die Handurteile weichen also vom Maschinenurteil ab; sie sind die Grundlage für die Frage nach einer Bedeutung „Ernährung von Tieren“, nicht deren Beschluss.

## Ergebnisse der Stichproben

**n = 10 je Klasse und Stichprobe, von einem Agenten gelesen, nicht von KZW.** Zehn Belege tragen keine Aussage über die Häufigkeit in den Mengen oben, nur über die Art der Fehler. `treffer` in `stichprobe-urteile.tsv` heißt: die maschinelle Klasse stimmt mit dem Lesen überein.

| Stichprobe | Menge, aus der gezogen wurde | n | stimmt | stimmt nicht | unsicher |
|---|---|--:|--:|--:|--:|
| 1, Klasse `tier` | 1.223 Belege mit `@ana` | 10 | 4 | 5 | 1 |
| 1, Klasse `mensch` | 7.745 | 10 | 10 | 0 | 0 |
| 1, Klasse `unklar` | 2.523 | 10 | nicht bewertet | | |
| 2, `tier` ohne Mensch-Treffer | 280 | 10 | 5 | 3 | 2 |

Bei `unklar` ist keine Trefferangabe vergeben; der Agent las alle zehn als Nahrung von Menschen oder als andere Bedeutung (9 `mensch`, 1 `mensch/andere Bedeutung`). In Stichprobe 1 lasen alle 5 falschen `tier`-Belege als Nahrung von Menschen: das Tierwort ist Objekt der Handlung oder steht nur im Umkreis. Ohne Mensch-Treffer (Stichprobe 2) trifft die Klasse in 5 von 10 Fällen; bei n = 10 lässt sich ein Unterschied zu den 4 von 10 aus Stichprobe 1 nicht belegen.

## Regenerieren

Die Skripte lesen nur und ändern im Repo nichts. In einen leeren Ordner schreiben (nicht in diesen), `manuell-faelle.tsv` vorher hineinkopieren, dann vergleichen:

```
python scripts/review/vorsortieren-603.py <repo> <leerer-ordner>
python scripts/review/stichprobe2-603.py <leerer-ordner>
python scripts/review/ana-603.py ingest/review/603-ernaehrung
```

`vorsortieren-603.py` liest `lexicon.xml`, `concepts.xml` und alle 667 TEI-Dateien. Beim Nachlauf am 16.10.2026 waren acht Ausgaben byte-gleich mit den Dateien hier (`senses-21111000`, `belege-tier`, `lemmata-ohne-ana`, `faelle-abebizen-lecken`, `konzepte-tier`, `stichprobe`, `stichprobe2-tier-ohne-mensch`, `zusammenfassung`); `stichprobe-urteile.tsv` und `manuell-faelle.tsv` sind Eingaben und werden nicht erzeugt. Ändert sich Lexikon oder Korpus, ändern sich Zahlen und Stichproben.
