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
| `28-phase2-ana-widerspruch.csv` | Phase 2: **424 Belege**, deren `@ana` auf einen Sense ohne Sprachkonzept zeigt, mit Kontext. Dort sagt der annotierte Bestand ausdrücklich, dass hier nicht die sprachbezogene Lesart gemeint ist |
| `28-phase2-handpruefung.csv` | Phase 2: die **26 belegstärksten Nicht-Namen** mit allem, was für ein Urteil nötig ist, plus zwei leeren Spalten `urteil` und `begruendung` |

Erzeugt von
[`scripts/audit/build-foreign-candidates-28.py`](../../scripts/audit/build-foreign-candidates-28.py)
und
[`scripts/audit/foreign-sense-contradictions-28.py`](../../scripts/audit/foreign-sense-contradictions-28.py),
reproduzierbar mit:

```bash
python scripts/audit/build-foreign-candidates-28.py --csv ingest/foreign-lang/28-gleis1-kandidaten.csv
python scripts/audit/foreign-sense-contradictions-28.py --out-dir ingest/foreign-lang
```

## Womit Phase 2 anfangen sollte, und warum nicht mit einer Frequenzschwelle

**Die Widerspruchsliste ist das schärfste rein maschinelle Ausschlusskriterium,
das Gleis 1 hat, und ihre Kleinheit ist ihr Vorzug.** Gemessen am 06.09.2026
über die 227.652 Tokens der Kandidatenmenge:

| | Tokens |
|---|---:|
| `@ana` zeigt auf einen Sprach-Sense | 209.832 |
| `@ana` **widerspricht** | **424** |
| gar kein `@ana` | 17.390 |
| `@ana` auf einen dem Lemma-Index unbekannten Sense | 6 |

424 Belege sind lesbar, 209.832 sind es nicht. Sie verteilen sich auf nur 19
Lemmata und konzentrieren sich stark: `zunge` 224, `nase` 100, `gebrechen`
37 (mit `gebrechenhaft` und `engebrechen` zusammen 39), `mël` 17, `klâr` 13.
Bei `zunge` ist der Mechanismus
mit bloßem Auge zu sehen: das Lemma trägt das Sprachkonzept, weil es „Sprache"
heißen kann, und in mehr als zweihundert Belegen sagt die Sense-Annotation
selbst, dass das Organ gemeint ist („sine zunge schouwen").

**Der Phasenplan nennt 430 statt 424, und die Differenz ist keine Drift,
sondern eine Zählweise.** Sechs Tokens tragen ein `@ana`, dessen Sense der
Lemma-Index nicht kennt (dreimal `soldân`, je einmal `Moab`, `kölnisch`,
`liber`). Der Plan zählte sie zu den Widersprüchen; hier stehen sie als eigene
Zeile, denn ein Verweis ins Leere widerspricht nichts, er sagt gar nichts.
424 plus 6 ergibt die 430.

**Die Widerspruchsliste ersetzt die Handpruefung aber nicht, sie ist fast
disjunkt von ihr.** Der Phasenplan empfiehlt, mit den Widerspruechen
anzufangen „statt mit einer Frequenzschwelle", und das liest sich wie eine
Alternative. Gemessen ist es keine: **22 der 26 belegstaerksten Nicht-Namen
tragen keinen einzigen Widerspruch**, und das sind 119.101 der 124.369 Tokens,
also 95,8 %.

| Lemma | Belege | `@ana` auf Sprach-Sense | Widerspruch | kein `@ana` |
|---|--:|--:|--:|--:|
| `niht` | 81.088 | 81.088 | **0** | 0 |
| `in` | 11.986 | 10.772 | 0 | 1.214 |
| `I` | 4.033 | 4.033 | 0 | 0 |
| `bischof` | 3.035 | 3.035 | 0 | 0 |
| `schrîben` | 3.007 | 295 | 0 | 2.712 |
| `klâr` | 2.530 | 284 | 13 | 2.233 |
| `engel` | 2.165 | 1.723 | 0 | 442 |
| `name` | 1.367 | 1.367 | 0 | 0 |

`niht` ist der Fall, an dem das sichtbar wird: alle 81.088 Belege tragen ein
`@ana`, und jedes einzelne zeigt auf den Sense mit dem Sprachkonzept. Der
annotierte Bestand widerspricht der Zuordnung dort nicht, er bestaetigt sie.
Das Kriterium kann den groessten Falschpositiven der Menge deshalb nicht
entfernen: die Annotation ist hier die Quelle des Problems und nicht sein
Korrektiv.

Umgekehrt liegen 184 der 424 Widersprueche auf 15 Lemmata, die gar nicht zu
den 26 gehoeren (`nase` 100, `gebrechen` 37, `mël` 17, `Agrippa` 6, `mate` 5,
`diuten` 4, dann einstellig bis `Exidiaces` 1); nur 240 fallen auf vier der 26
(`zunge` 224, `klâr` 13, `missa` 2, `mort` 1). Beide Listen sind also zu
lesen, und keine nimmt der anderen Arbeit ab.

Fuer die `gebrechen`-Frage aus dem Thread faellt dabei eine Bestaetigung ab:
`gebrechen` 37 plus `gebrechenhaft` 1 plus `engebrechen` 1 sind 39
Widersprueche, und mit dem einen Sprach-Beleg `JT_30921000_5` ergibt das die
40 sense-disambiguierten Tokens, die der Thread nennt. Unabhaengig gemessen,
anderes Skript, gleiche Zahl.

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
