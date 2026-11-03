# Weingrüße (BRE): Zwischenstand der Stufe 0

Artefakte des Ingests der Weingrüße aus dem Brevitas-Wiki (Issue [#147](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/147)). Wie sie entstehen und was offen ist, steht in [`scripts/ingest/bre/README.md`](../../scripts/ingest/bre/README.md).

| Datei | Inhalt | Erzeugt von |
|---|---|---|
| `zeugen.tsv` | Die 21 Überlieferungszeugen mit Signatur, Datierung, Schreibsprache, Ort, Stellen der Weingrüße, Epochenprüfung vor 1600 und Seitenbeleg in den Druckfahnen (Kapitel IV). Die letzte Spalte nennt, wo Silvans Word-Steckbriefe von 2022 abweichen | von Hand, aus den Druckfahnen |
| `revisionen.tsv` | Die gepinnten Wiki-Revisionen mit sha256 | `00-fetch-wiki.py` |
| `segmentierung.tsv` | Je Einzeltext und Zeuge Blattangabe, erster Vers und Überschrift aus den Synopsen | `01-segmentierung.py` |
| `BRE_CGM713.tei.xml` | Der erste Zeuge, Cgm 713 (Sigle B), unannotiert. Validiert nicht gegen `schema/mhdbdb.rng`, siehe die Schemafrage im Skript-README | `02-convert-wiki-to-mhdbdb.py --zeuge B` |

Die Daten stehen unter CC BY-NC-SA 4.0 (Freigabe Silvan Wagner, 23.10.2026). `zeugen.tsv` gibt Angaben aus der Einleitung der Hirzel-Ausgabe als Fakten mit Seitenbeleg wieder, ohne deren Text zu übernehmen.

Die TEI-Dateien bleiben hier und nicht in `tei/`, solange die Header Platzhalter tragen (`work_TBD`, `genre_TBD`, Sprachstufe `TBD`). Gründe und Umzugsschritte wie bei [ARI](../ari/README.md).
