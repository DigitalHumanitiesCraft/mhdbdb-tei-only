# CoReMA-Pilot (COR): Zwischenstand der Stufe 0

Artefakte der Stufe 0 für den CoReMA-Pilot aus Issue [#139](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/139): Bs1, GR1, M11 und W1. Wie sie entstehen, was Platzhalter ist und was für die gemeinsame Sitzung offen bleibt, steht in [`scripts/ingest/cor/README.md`](../../scripts/ingest/cor/README.md).

| Datei | Inhalt | Erzeugt von |
|---|---|---|
| `COR_BS1.tei.xml` | Basel, UB Basel, AN V 12 (Kochbuch des Meister Hans), unannotiert | `01-convert-corema-to-mhdbdb.py --buch bs1` |
| `COR_GR1.tei.xml` | Graz, Universitätsbibliothek, Ms. 1609 (Mondseer Koch- und Haushaltsbuch), unannotiert | `--buch gr1` |
| `COR_M11.tei.xml` | München, Universitätsbibl., Cim. 4 (Hausbuch Michaels de Leone), unannotiert | `--buch m11` |
| `COR_W1.tei.xml` | Wien, Österr. Nationalbibl., Cod. 2897, unannotiert | `--buch w1` |
| `COR_<BUCH>.annotationen.tsv` | die semantische Auszeichnung der Quelle (Zutaten, Werkzeuge, Gerichte, Handlungsanweisungen u. a.) mit Q-IDs, verankert an den `xml:id` der Wörter | dasselbe Skript |
| `quellen.tsv` | Je Buch Signatur, Datierung, PID, Pfad, Größe und sha256 der gelesenen Quelldatei, Wort- und Satzzeichenzahl | `--buch alle` |

| Buch | Dateien | `<w>` | `<pc>` | `<div>` (recipe + section) | `<pb>` | Zeilen in `annotationen.tsv` | valide gegen `schema/mhdbdb.rng` |
|---|---:|---:|---:|---:|---:|---:|---|
| COR_BS1 | 1 | 24 031 | 627 | 306 (269 + 37) | 183 | 7 622 | ja |
| COR_GR1 | 1 | 24 300 | 111 | 284 (254 + 30) | 154 | 7 750 | ja |
| COR_M11 | 1 | 8 046 | 666 | 101 (98 + 3) | 20 | 2 770 | ja |
| COR_W1 | 1 | 18 729 | 24 | 278 (263 + 15) | 58 | 6 492 | ja |
| zusammen | 4 | 75 106 | 1 428 | 969 (884 + 85) | 415 | 24 634 | 4 von 4 |

Stand 2026-11-08, gemessen mit `01-convert-corema-to-mhdbdb.py --buch alle`. Die Quelle stammt aus dem lokalen CoReMA-Datenrepository, das sich laufend ändert, `quellen.tsv` nennt die gelesenen Stände.

Die Textdaten stehen unter CC BY 4.0 (CoReMA, ZIM-ACDH Universität Graz, hg. von Helmut W. Klug, Transkription Astrid Böhm laut Quelle, der Förderhinweis steht im Header).

Die TEI-Dateien bleiben hier und nicht in `tei/`, solange die Header Platzhalter tragen (`work_TBD`, `genre_TBD`, Sprachstufe `TBD`). Gründe und Umzugsschritte wie bei [BRE](../bre/README.md) und [ARI](../ari/README.md).
