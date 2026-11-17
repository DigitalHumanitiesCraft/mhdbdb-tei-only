# Weingrüße (BRE): Stufe 0 und Phase 1 bis 3

Artefakte des Ingests der Weingrüße aus dem Brevitas-Wiki (Issue [#147](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/147)). Wie sie entstehen, mit welchen Zahlen und was offen ist, steht in [`scripts/ingest/bre/README.md`](../../scripts/ingest/bre/README.md).

| Datei | Inhalt | Erzeugt von |
|---|---|---|
| `zeugen.tsv` | Die 21 Überlieferungszeugen mit Signatur, Datierung, Schreibsprache, Ort, Stellen der Weingrüße, Epochenprüfung vor 1600 und Seitenbeleg in den Druckfahnen (Kapitel IV). Die letzte Spalte nennt, wo Silvans Word-Steckbriefe von 2022 abweichen | von Hand, aus den Druckfahnen |
| `revisionen.tsv` | Die gepinnten Wiki-Revisionen mit sha256 | `00-fetch-wiki.py` |
| `segmentierung.tsv` | Je Einzeltext und Zeuge Blattangabe, erster Vers und Überschrift aus den Synopsen | `01-segmentierung.py` |
| `hauptseite-abgleich.tsv` | Abweichungen zwischen Transkription und Überlieferungsliste der Hauptseite | `03-hauptseite-abgleich.py` |
| `BRE_*.tei.xml` | 18 der 21 Zeugen, mit `@lemmaRef`, `@pos`, `@ana` und `@corresp`, soweit maschinell zugewiesen. B2, d4 und d6 fehlen, ihre Segmentierung wartet auf Silvan. Von D (`BRE_MSCRM50`) nur Teil A | `02`, dann `10` bis `18` |
| `phase1/` | Lemma: mehrdeutige Wörter mit Entscheidung (`lemma-pending.tsv`), Bulk- und Patch-Entscheidungen, Wörter ohne Lemma nach Häufigkeit (`lemma-unmatched.tsv`) | `10`, `12`, `13` |
| `phase2/` | Wortart: dasselbe für `@pos` | `14`, `12`, `15` |
| `phase3/` | Bedeutung: dasselbe für `@ana`, dazu die Wörter mit mehreren Variantentypen (`corresp-mehrdeutig.tsv`) | `16`, `12`, `15`, `18` |
| `pruefung/` | Prüfpaket für Julia und KZW, mit eigenem [README](pruefung/README.md) | `20-pruefpaket.py` |

Die Daten stehen unter CC BY-NC-SA 4.0 (Freigabe Silvan Wagner, 23.10.2026). `zeugen.tsv` gibt Angaben aus der Einleitung der Hirzel-Ausgabe als Fakten mit Seitenbeleg wieder, ohne deren Text zu übernehmen.

Die TEI-Dateien bleiben hier und nicht in `tei/`, solange die Header Platzhalter tragen (`work_TBD`, `genre_TBD`, Sprachstufe `TBD`) und die maschinellen Zuweisungen nicht geprüft sind. Gründe und Umzugsschritte wie bei [ARI](../ari/README.md).
