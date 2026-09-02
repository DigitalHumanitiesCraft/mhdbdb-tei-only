# Fremdsprachigkeit und Lehnwortschatz: Kandidaten und Review-Artefakte (#28)

Entscheidungs-Artefakte zu Issue #28. Der Phasenplan liegt in
[`docs/features/FREMDSPRACHEN-PHASENPLAN-28.md`](../../docs/features/FREMDSPRACHEN-PHASENPLAN-28.md),
die erzeugenden Skripte in `scripts/audit/`.

Nichts hier ist Korpus oder Authority-File. Es sind Listen, aus denen kuratiert
wird; geschrieben wird erst in Phase 3.

## Was hier liegt

| Datei | Inhalt |
|---|---|
| `28-gleis1-kandidaten.csv` | Quelle A aus Phase 1 Punkt 1: 6.246 Lemmata, deren Senses auf `concept_23123000` oder eine seiner 17 Sprachkategorien zeigen, mit Belegzahl, Streuung und Belegklasse |

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
weder das eine noch das andere sind. Die 26 belegstaerksten Nicht-Namen
enthalten beides nebeneinander: `niht` traegt „Lateinisch" und ist
ersichtlich kein Latein, `bischof`, `engel` und `klâr` stehen in derselben
Klasse und sind echte Lehnwoerter. Ein Frequenz-Cutoff waere deshalb falsch.
Diese 26 durchzusehen ist eine Viertelstunde und entscheidet ueber
124.369 der 161.018 Nicht-Namen-Tokens, also 77,2 % davon (von allen
227.652 Tokens der Liste sind es 54,6 %).

Die Spalte `sprachkonzepte` kann „Einzelsprachen" enthalten. Das ist die
Wurzel selbst und keine Sprache, sondern die unspezifische Zuordnung
„irgendeine Einzelsprache"; 31 Lemmata haengen direkt an ihr, darunter
`englisch`, `welsch`, `rotwalsch` und `tolmetze`.

`ist_name` trennt die Eigennamen ab, weil Namenherkunft eine eigene Frage
ist (Entscheidung KZW, siehe #28). Die Zuordnung ist dort auffaellig
verlaesslich. Ein Lemma gilt als Name, wenn `NAM` in `pos_alle` steht, nicht
wenn die Spalte `pos` NAM sagt: `pos` ist der Erstwert einer praktisch
alphabetisch sortierten Liste, kein Urteil ueber die Hauptlesart.

Die Liste ist **Quelle A** im Sinne von Phase 2: sie wird gegen Gleis 2
(LLM) und Gleis 3 (Woerterbuch-Crawl) gehalten, nicht fuer sich genommen
uebernommen.
