# #387 Nachlauf: ADJ oder ADV bei feststehendem Lemma

Lauf vom 06.09.2026. Zweiter Durchgang über die Belege, die der `fro`-Lauf
(`../387-fro/`) am selben Tag wegen mittlerer Konfidenz zurückgehalten hat.

## Warum das kein zweiter Wurf mit derselben Frage ist

Der erste Lauf hatte zwei Entscheidungen je Beleg zu treffen, Lemma und
Wortart, und musste laut Prompt auf höchstens `medium` gehen, sobald das Lemma
klar war und die Wortart nicht. Genau diese Fälle liegen hier. Sie sind sich
beim **Lemma alle einig**: 30 von 30 auf `lemma_7250` (*vrô* „froh"). Die
philologische Frage „Anrede *vrouwe* oder Adjektiv *vrô*" ist in keinem
einzigen offen.

Die Rechnung über die 35 zurückgehaltenen Fälle des ersten Laufs schliesst
damit vollständig: **3** liegen auf `lemma_7260` (*vrouwe*), sind von KZW am
01.09. entschieden und am 06.09. mit dem neu geprägten `type_372365`
geschrieben; **2** sind Substantivierungen und damit eine kuratorische Frage
(NOM), die hier nicht gestellt wird; die verbleibenden **30** sind dieser Lauf.
Eine frühere Fassung dieses Absatzes nannte 31 von 31. Gemessen sind es 30:
`cases.json` führt 30 Einträge, alle 30 stehen in `../387-fro/review-faelle.csv`,
und von den dortigen 32 Fällen mit `lemma_7250` sind genau die beiden
Substantivierungen (`FR1_13058020_4`, `FR2_419020_7`) nicht dabei.

Offen ist nur ADJ gegen ADV, und das ist **K4** nach
[POS-TAGSET §4](../../../docs/POS-TAGSET.md) („compound resolution `ADJ ADV`"),
also ausdrücklich die LLM-Aufgabe mit den Gates aus §6.3 und keine
kuratorische Entscheidung.

## Der Prior, der die Arbeit getan hat

`@pos` an `lemma_7250` über alle 667 Dateien, Stand `origin/main`:

```
git grep -h -oP '<w [^>]*lemmaRef="lexicon.xml#lemma_7250"[^>]*>' origin/main \
    -- 'tei/*.tei.xml' | grep -oP 'pos="[^"]*"' | sort | uniq -c
```

| `@pos` | Tokens |
|---|---:|
| `ADJ ADV` (unaufgelöstes Kompositum) | 4.661 |
| `ADJ` | 76 |
| `ADJ GRA` | 64 |
| `NOM ADJ ADV` | 45 |
| `NOM ADJ` | 9 |
| `NOM` | 7 |
| `NAM` | 5 |
| `NOM ADJ ADV GRA` | 1 |
| `ADJ ADV GRA` | 1 |
| **`ADV` allein** | **0** |
| Summe | **4.869** |

**Kein einziger Beleg trägt `ADV` allein.** Der erste Lauf hatte für 14 der 30
Fälle ADV vorgeschlagen. Unter diesem Prior und der Regel „depiktiv ist ADJ"
sind davon **13 gefallen**: das Argument lautete jedes Mal „modifiziert das
Verb ohne Kopula", und das ist bei einem Depiktiv gerade kein ADV-Argument.
*er schiet enweg frô* sagt, dass **er** froh war, nicht wie er ging.

### Korrektur zur Tabelle in `prompt.md`

**Die Fassung dieser Tabelle, die den Agenten vorlag, ist unvollständig und
mischt zwei Nenner.** Sie führt sieben Zeilen statt neun (die beiden
GRA-Kombinationen fehlen, zusammen 2 Tokens), summiert sich damit auf 4.867
statt 4.869, und der Fettsatz darunter nennt **5.215** als Nenner, obwohl die
Tabelle ausdrücklich `origin/main` misst. Die 5.215 sind der Stand **nach**
dem Lauf von 4.2.11, also inklusive der dort geschriebenen 355 Tokens.

Gemeldet vom CI-Review-Bot auf PR #398, Runde 10, hier nachgemessen und
bestätigt. Die tragende Aussage ist davon unberührt und in beiden Zählweisen
wahr: auf `origin/main` sind es 4.869 Belege mit null `ADV`, heute 5.215 mit
genau einem, und dieser eine (`NEIC_12710160_0`) stammt aus dem Lauf von
4.2.11, was `prompt.md` im nächsten Satz selbst offenlegt.

**`prompt.md` bleibt trotzdem unverändert.** Die Datei ist das Protokoll
dessen, was die vier Agenten gelesen haben, und darf nicht nachträglich zu
etwas anderem gemacht werden. Dieselbe Regel wie bei `../387-fro/cases.json`.

## Ergebnis

| | Fälle |
|---|---:|
| ADJ | 27 |
| ADV | 1 |
| unentschieden | 2 |
| **davon `high`, also geschrieben** | **19** |
| zurückgehalten | 11 |

Geschrieben sind 19 Tokens in DIO, FR1, FR3, GWTK, RVBR und WUB, alle
`lemma_7250` ADJ mit `corresp` aus dem Bestand (`type_41787` für `fro`,
`type_25866` für `frô`). Korpus-Index 4.2.13; `variants.xml` unverändert,
deshalb kein Bump des Authority-Index.

## Zwei Dinge, die der Lauf anders gemacht hat als übliche Batches

**`unentschieden` war ein erlaubtes Ergebnis**, und zwei Fälle haben davon
Gebrauch gemacht (beide die verblose Antithese *gein trurec fro, gein sorgen
lust*, wortgleich in FR1 und FR3). Eine erzwungene Entscheidung wäre schlechter
als eine saubere Vorlage. `apply-homograph.py` kennt keinen solchen `pos`-Wert;
diese Fälle tragen in `actions.json` den Platzhalter `ADJ` mit `medium` und dem
Präfix `UNENTSCHIEDEN:` in der Begründung, werden also nie geschrieben und
stehen in `review-faelle.csv` lesbar.

**Zur Konfidenz wurde nachgefragt statt überstimmt.** Im ersten Durchgang
standen 16 Fälle auf `medium`, **sechs** davon mit der Begründung, unsicher sei
nicht ADJ gegen ADV, sondern das Bezugswort, und alle Lesarten seien
adjektivisch (fünf in GWTK, einer in FR3). Das ist ein Zweifel an einer anderen
Frage als der gestellten; der Prompt war darin unscharf. Die betroffenen Läufe
haben ihre Konfidenz auf Rückfrage selbst neu bewertet, statt dass sie hier
umgeschrieben wurde. **Fünf** gingen auf `high`, einer blieb bewusst `medium`
(`GWTK_272211589800_5`: bei einem Verbum dicendi in Reimposition, *und saitte
im gütte mere fro*, kommt die Art-und-Weise-Lesart tatsächlich in Betracht). Die
Rechnung schliesst damit: 14 `high` und 16 `medium` nach dem ersten Durchgang,
19 und 11 danach, also plus fünf und minus fünf.

Eine frühere Fassung dieses Absatzes nannte an beiden Stellen nur die
GWTK-Zahlen (fünf nachgefragt, vier auf `high`) und liess den FR3-Fall aus,
wodurch 16 minus 4 auf 12 statt auf die gemessenen 11 führte. Gemeldet vom
CI-Review-Bot auf PR #398, Runde 11, hier nachgemessen. Kein Tag hängt daran:
geschrieben sind in beiden Lesarten dieselben 19.

## Was zurückgehalten ist und wo es liegt

11 Fälle in `review-faelle.csv`, jeder mit Verskontext und Begründung. Sie
gehen zusammen mit den zwei Substantivierungen aus dem ersten Lauf
(`FR2_419020_7`, `FR1_13058020_4`) als Paket an @wachauer, siehe den Kommentar
an #387 vom 06.09. Auf **11 verschiedene Stellen** reduzierbar, weil die
Antithese und die Judit-Stelle je zweimal in Parallelüberlieferung stehen.

Der bemerkenswerteste ist `RVBR_6083_0`, das einzige ADV-Urteil. Es fällt
bewusst gegen den Prior und ist gut begründet (Subjekt *mîn ouge*, ein
Körperteil, das nicht froh sein kann; Koordination mit *friuntlîchen*, einer
eindeutigen Adverbform). Wäre es richtig, wäre es der **erste** `ADV`-Beleg von
*vrô* im ganzen Korpus. Genau deshalb steht es nicht im Batch: eine
Entscheidung gegen den gesamten annotierten Bestand gehört nicht in einen
maschinellen Lauf.

## Reproduktion

```bash
python scripts/ingest/pos-disambig/apply-homograph.py \
    --config ingest/pos-disambig/387-fro-adjadv/config.json \
    --cases  ingest/pos-disambig/387-fro-adjadv/cases.json \
    --actions ingest/pos-disambig/387-fro-adjadv/actions.json \
    --out-dir ingest/pos-disambig/387-fro-adjadv
```

Ohne `--apply` ein Trockenlauf. `cases.json` entsteht aus den `REVIEW`-Zeilen
mit Grund `confidence` der `../387-fro/diff-liste.csv`; das Feld `next_token`
ist dabei entfernt, weil es das Anrede-Signal war (das Lemma steht hier fest)
und im ersten Lauf das unzuverlässige Feld. Ein Feld mit Warnhinweis
mitzuschleppen ist schlechter, als es wegzulassen.
