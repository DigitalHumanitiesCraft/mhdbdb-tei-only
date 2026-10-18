# #602: naschen (lemma_57919), Belege disambiguieren

Arbeitsnotiz zu #602, Lauf vom 18.10.2026 (Umsetzung `scripts/ingest/pos-disambig/apply-462-602.py`, zusammen mit #462).

## Ausgangslage

`lemma_57919` naschen hat zwei Bedeutungen: `lemma_57919_sense_93121` (Sexualleben/Erotik, `concept_21112000`) und `lemma_57919_sense_93122` (Ernährung von Menschen, `concept_21111000`, Genussmittel `concept_21111400`). Im Korpus stehen 5 Belege (`grep -rc lemma_57919 tei/`, 5 Dateien mit je einem Treffer), alle ohne `@ana`. KZW hat am 15.10.2026 festgehalten, dass bei naschen die Essensassoziation häufiger ist.

## Lesung

Alle 5 Belege im Kontext von mindestens 40 Wörtern davor und danach gelesen (OVW mit 120) (`belege.tsv`), dazu die MWB-Suche (`mhdwb-online.de`, Lemmaliste "nasch*": `naschen` swV. mit 1 Beleg im Belegarchiv, Enikel Weltchronik 27430, das ist `JEW_2743000000_3`).

| Einstufung | Belege |
|---|--:|
| Essen (`sense_93122`) | 4 (JEW, NEI, NEIC, NEIR) |
| offen | 1 (OVW) |

NEI, NEIC und NEIR sind drei Überlieferungen derselben Neidhart-Strophe. Gesetzt ist `@ana` auf `lemma_57919_sense_93122` an den 4 Essens-Belegen; `@lemmaRef`, `@pos` und `@corresp` bleiben. Der OVW-Beleg bleibt ohne `@ana` und geht als Frage an KZW.

Der Tausch der Bedeutungen in der Darstellung (Essen zuerst), den KZW am 15.10.2026 beschlossen hat, steht schon in `lexicon.xml` (`sense_93122` vor `sense_93121`); dieses Ticket ändert daran nichts.
