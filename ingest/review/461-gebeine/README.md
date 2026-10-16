# Arbeitsliste #461: gebeine (lemma_1958)

Zuschnitt entschieden von @chsteiner am 10.10.2026: `lemma_1958` bekommt einen neuen Sense mit `concept_14011100` (Körper/Gliedmaßen von Säugetieren), die 21 Säugetier-Belege erhalten ihn als `@ana`, alles andere bleibt. Umsetzung: `scripts/ingest/pos-disambig/apply-461-gebeine.py`.

## Bestand

207 Tokens in 79 Texten, alle `@pos="NOM"`. Messvorschrift: alle `<w>` in `tei/*.tei.xml`, in deren `@lemmaRef` `#lemma_1958` als ganzes Token steht. Die Einstufung in `belege.tsv` (Spalten `xml:id`, `Sigle`, `Form`, `Kontext` mit Treffer in `[[ ]]`, `Einstufung`, `Begründung`) ist ein Leseurteil am Kontext, einzeln je Token, von der Koordination am 10.10.2026 vorgelegt; die Zählung der Tabelle und die Liste der 21 sind nachgezählt.

| Einstufung | Tokens |
|---|--:|
| menschlich | 131 |
| Reliquie/Heilige | 40 |
| tierisch | 27 |
| übertragen/sonstig | 5 |
| unklar | 4 |
| Summe | 207 |

Von den 27 tierischen Belegen sind **21 Säugetiere** in 15 Texten: Pferd 7, Elefant 5 (drei davon Elfenbein für einen Thron), Stier 3, Ferkel 2, Löwe, Bär, Ochsen und Tierknochen ohne genannte Art je 1. Sie bekommen den neuen Sense.

## Umsetzung

- **Sense:** `lemma_1958_sense_119196` mit genau einem Konzept, `concept_14011100`. Höchste Sense-Nummer vorher 119195. Kein `@ana` am Sense, wie bei `lemma_9644_sense_119194`.
- **Tokens:** `@ana` auf den neuen Sense; 5 der 21 trugen vorher `lemma_1958_sense_3004`, 16 keines. `@lemmaRef`, `@pos` und `@corresp` bleiben; `variants.xml` ändert sich dadurch nicht.
- **Revision:** je Datei ein `<change when="2026-10-10">` (15 Dateien).

## Unberührt, Frage an KZW

- **6 Tierbelege ohne Säugetier:** Hahn `AMI_972_3`, Fisch `FLG1_4135180940_2`, Phönix `TRO_37_4`, Drache `PL3_312606_7`, `VIR_17403_4`, `VIR_30008_4`. Frage: bekommen Vögel, Fische und Fabeltiere ein Konzept, oder bleiben sie ohne?
- **9 offene Belege:** unklar `HTR_201620_3`, `DRE_177_1`, `DRE_180_1`, `DRE_181_2`; übertragen oder sonstig `NAR_9303540_3`, `NAR_9400900_3`, `ROL_4345_1`, `JSG_410_1`, `IW_5852_4`.
- **`concept_21104000`** (Natürlicher/Gewaltsamer Tod) hängt an `lemma_1958_sense_3004` und damit auch an Belegen für lebende Körper („fleisch und gebeine“).

## Nachtrag 2026-10-16: KZWs Antworten vom 15.10.2026

Umsetzung: `scripts/ingest/pos-disambig/apply-460-461-rest.py`. Die Spalten `Entscheidung` und `Quelle` in `belege.tsv` tragen die Folge je Token.

- **Vögel und Fische** bekommen je einen Sense mit dem vorhandenen Körperkonzept (Hahn `AMI_972_3`: `lemma_1958_sense_119198` mit `concept_14021100`; Fisch `FLG1_4135180940_2`: `lemma_1958_sense_119199` mit `concept_14031100`). Höchste Sense-Nummer vorher 119197 (`lemma_79829_sense_119197`, gemessen an `lexicon.xml`), also fortlaufend. Je ein Beleg im Korpus.
- **Die 9 offenen Belege** (4 unklare, 5 übertragene) kommen nach KZWs Regel an `lemma_1958_sense_49690`. `NAR_9400900_3` trug ihn schon, 8 Tokens ändern sich; `JSG_410_1` wechselt von `lemma_1958_sense_3004` und verliert damit das Tod-Konzept `concept_21104000`. Die drei Würfelknochen in DRE sind menschlich: die Würfel sind aus den zwei Stockzähnen des Ritters gemacht (`tei/DRE.tei.xml`, V. 36, 117 und 122 bis 126). Die Tabelle vom 10.10. hielt die Herkunft für nicht genannt; sie steht im Text, vor dem Fenster, das die Einstufung las (V. 137 bis 217).
- **Unverändert**: Drache (`PL3_312606_7`, `VIR_17403_4`, `VIR_30008_4`) und Phönix (`TRO_37_4`); offen ist, ob `concept_14100000` direkt oder ein neues Unterkonzept gilt.
- **Richtigstellung zur Tabelle vom 10.10.:** die Begründung von `NAR_9303540_3` sagte „Sense 49690 gesetzt“. Im TEI trug dieses Token kein `@ana` (nur `NAR_9400900_3`); die Angabe ist aus der Tabelle gestrichen und der Sense jetzt wirklich gesetzt.

Stand danach, gemessen am 2026-10-16 (207 Tokens, `@ana` je Token): `sense_3004` 55, `sense_49690` 10, `sense_119196` 21, `sense_119198` 1, `sense_119199` 1, ohne `@ana` 119; Summe 207.
