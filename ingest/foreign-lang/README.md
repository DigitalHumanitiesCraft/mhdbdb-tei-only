# Fremdsprachigkeit und Lehnwortschatz: Kandidaten und Review-Artefakte (#28)

Entscheidungs-Artefakte zu Issue #28. Der Phasenplan liegt in
[`docs/features/FREMDSPRACHEN-PHASENPLAN-28.md`](../../docs/features/FREMDSPRACHEN-PHASENPLAN-28.md),
die erzeugenden Skripte in `scripts/audit/`.

Nichts hier ist Korpus oder Authority-File. Es sind Listen, aus denen kuratiert
wird; geschrieben wird erst in Phase 3.

## Was hier liegt

| Datei | Inhalt |
|---|---|
| `28-gleis1-kandidaten.csv` | Quelle A aus Phase 1 Punkt 1: 6.219 Lemmata, deren Senses auf eine Sprachkategorie unter `concept_23123000` zeigen, mit Belegzahl, Streuung und Belegklasse |

Erzeugt von
[`scripts/audit/build-foreign-candidates-28.py`](../../scripts/audit/build-foreign-candidates-28.py),
reproduzierbar mit:

```bash
python scripts/audit/build-foreign-candidates-28.py --csv ingest/foreign-lang/28-gleis1-kandidaten.csv
```

## Wie die Liste zu lesen ist

Die Spalte `handpruefung` sagt nicht „verwerfen", sondern „einzeln ansehen".
`concept_23123000` haengt unter „Kommunikation/Sprache" und ist ein
Bedeutungsfeld, kein Herkunftsfeld: es traegt Lemmata, die eine Sprache
**bezeichnen** oder in ihr **stehen**, und in der Praxis auch solche, die
weder das eine noch das andere sind. Das Rauschen sitzt fast vollstaendig in
den 25 belegstaerksten Nicht-Namen, und dort steht es neben echten
Lehnwoertern: `niht` traegt „Lateinisch" und ist ersichtlich keins,
`bischof`, `engel` und `klâr` stehen in derselben Klasse und sind welche.
Ein Frequenz-Cutoff waere deshalb falsch, eine Handpruefung dieser 25 ist
eine Viertelstunde und entscheidet ueber 77,5 % der Tokenmenge.

`ist_name` trennt die Eigennamen ab, weil Namenherkunft eine eigene Frage
ist (Entscheidung KZW, siehe #28). Die Zuordnung ist dort auffaellig
verlaesslich.

Die Liste ist **Quelle A** im Sinne von Phase 2: sie wird gegen Gleis 2
(LLM) und Gleis 3 (Woerterbuch-Crawl) gehalten, nicht fuer sich genommen
uebernommen.
