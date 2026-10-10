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
