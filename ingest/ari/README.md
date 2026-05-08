# ARITHMETIC Ingest — Stage-0-Konversion

Konversions-Artefakte für das ARITHMETIC-Korpus (Issue [#92](https://github.com/DigitalHumanitiesCraft/mhdbdb-tei-only/issues/92), Beitrag von Carina, Universität Graz / GAMS).

## Status (2026-05-08)

Sechs Handschriften aus Carinas TEI-Daten, mechanisch ins MHDBDB-Schema konvertiert via [`scripts/ingest/ari/01-convert-original-to-mhdbdb.py`](../../scripts/ingest/ari/01-convert-original-to-mhdbdb.py):

| Datei | Beschreibung | Stage 2 |
|---|---|---|
| `ARI_AUG81.tei.xml` | Augsburg, UB, Cod. 81 I | PASS |
| `ARI_BRE1948.tei.xml` | Breslau, BU, 1948 | PASS |
| `ARI_EIN624.tei.xml` | Einsiedeln, StiftB, Cod. 624 | PASS |
| `ARI_MUE279.tei.xml` | München, UB, 8 Cod.ms. 279 | PASS |
| `ARI_MUE746.tei.xml` | München, UB, 8 Cod.ms. 746 | PASS |
| `ARI_WIEN5206.tei.xml` | Wien, ÖNB, Cod. 5206 | PASS |

Alle 6 validieren sauber gegen `schema/mhdbdb.rng` nach der Schema-Erweiterung vom 2026-05-08 (siehe [`docs/DECISIONS.MD § PD-001`](../../docs/DECISIONS.MD)).

## Warum hier statt in `tei/`

Die Header haben noch Platzhalter-Werte (`work_TBD`, `genre_TBD`, `msIdentifier corresp="works.xml#work_TBD"`), weil Carinas Antwort zu finaler Sigle, Edition, Genre und Begriffssystem-Mapping aussteht. In `tei/` hätten sie zwei Probleme:

1. `build-corpus-index.py` würde sie indexieren mit Platzhalter-Metadaten
2. Authority-File-Cross-References würden ins Leere zeigen

Hier in `ingest/ari/` bleiben sie als **dokumentierter Zwischenstand**: Stage-0-Konversion technisch durch, Schema passt, wartet auf inhaltliche Finalisierung.

## Ingest-Pattern (für künftige Korpora)

`ingest/<sigle>/` ist der Top-Level-Ordner für Source-Daten und Pipeline-Artefakte pro Korpus. Pipeline-Skripte leben unter `scripts/ingest/<sigle>/`. Konvention seit 2026-05-08.

**Wenzelsbibel** liegt aktuell noch unter `Wenzelsbibel/` im Repo-Root (historisch gewachsen, ~20 WZB-Skripte mit hardgecodeten Pfaden). Refactor zu `ingest/wzb/` ist Folge-Task.

## Wann nach `tei/` umziehen

Sobald Carina die letzten Metadaten geliefert hat:

1. Konversions-Skript mit finalen Werten neu laufen lassen (Sigle, Genre-ID aus genres.xml, work_N in works.xml, etc.)
2. Stage-2-Validierung prüfen
3. `git mv ingest/ari/ARI_*.tei.xml tei/`
4. Korpus-Index rebuilden (`python scripts/build-corpus-index.py`)
5. Commit + Push

Reproduzierbar via `scripts/ingest/ari/01-convert-original-to-mhdbdb.py` aus Carinas Originaldaten-ZIP (`Arithmetic_MHDBDB.zip`, untracked im Repo-Root).
